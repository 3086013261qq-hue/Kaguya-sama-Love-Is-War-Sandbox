import { createPlayer } from './player.mjs';
import { createVideoLockscreen } from './lockscreen.mjs';

function fmtTime(value) {
  if (!Number.isFinite(value) || value < 0) return '0:00';
  const m = Math.floor(value / 60);
  const s = Math.floor(value % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

export function mountKaguyaVerdictMvu(root, { musicManifest, videoManifest, getVerdict } = {}) {
  if (!root) throw new Error('MVU root missing');
  const readVerdict = typeof getVerdict === 'function' ? getVerdict : () => '今日，胜负未定。';

  root.classList.add('kg-mvu');
  root.innerHTML = `
    <section data-lockscreen></section>
    <section class="kg-panel" data-panel hidden>
      <button type="button" class="kg-panel__back" data-back>返回锁屏</button>
      <div class="kg-verdict-card">
        <div class="kg-verdict-card__jp">本日の勝敗</div>
        <div class="kg-verdict-card__text" data-verdict>今日，胜负未定。</div>
        <div class="kg-verdict-card__stamp">敗北</div>
      </div>
      <div class="kg-player">
        <div class="kg-player__topline">
          <div>
            <div class="kg-player__title" data-track-title>Awake</div>
            <div class="kg-player__artist" data-track-artist>岩崎琢</div>
          </div>
          <div class="kg-player__status" data-track-status>待播放</div>
        </div>
        <div class="kg-player__controls">
          <button type="button" data-prev-track aria-label="上一首">‹</button>
          <button type="button" class="kg-player__play" data-toggle aria-label="播放或暂停">▶</button>
          <button type="button" data-next-track aria-label="下一首">›</button>
        </div>
        <div class="kg-player__progress-row">
          <span data-current>0:00</span>
          <input type="range" min="0" max="1000" value="0" step="1" data-progress aria-label="播放进度">
          <span data-duration>0:00</span>
        </div>
        <select class="kg-player__select" data-track-select aria-label="曲目选择"></select>
      </div>
    </section>`;

  const lockRoot = root.querySelector('[data-lockscreen]');
  const panel = root.querySelector('[data-panel]');
  const verdict = root.querySelector('[data-verdict]');
  const title = root.querySelector('[data-track-title]');
  const artist = root.querySelector('[data-track-artist]');
  const status = root.querySelector('[data-track-status]');
  const toggle = root.querySelector('[data-toggle]');
  const progress = root.querySelector('[data-progress]');
  const current = root.querySelector('[data-current]');
  const duration = root.querySelector('[data-duration]');
  const select = root.querySelector('[data-track-select]');

  select.innerHTML = musicManifest.tracks
    .map((track, i) => `<option value="${i}">${track.theme ? '★ ' : ''}${track.title} — ${track.artist}</option>`)
    .join('');

  let audio = document.querySelector('audio[data-kaguya-mvu-audio]');
  let ownsAudio = false;
  if (!audio) {
    audio = document.createElement('audio');
    audio.dataset.kaguyaMvuAudio = '1';
    audio.style.display = 'none';
    document.body.appendChild(audio);
    ownsAudio = true;
  }

  function renderPlayer(snap) {
    if (!snap?.track) return;
    title.textContent = snap.track.title;
    artist.textContent = snap.track.artist;
    status.textContent = snap.status;
    toggle.textContent = snap.paused ? '▶' : 'Ⅱ';
    current.textContent = fmtTime(snap.currentTime);
    duration.textContent = fmtTime(snap.duration);
    progress.value = snap.duration > 0 ? String(Math.round((snap.currentTime / snap.duration) * 1000)) : '0';
    if (snap.current >= 0) select.value = String(snap.current);
  }

  const player = createPlayer(audio, musicManifest, renderPlayer);
  renderPlayer(player.snapshot());

  let lockPageIndex = videoManifest.default_page || 0;
  const lockscreen = createVideoLockscreen(lockRoot, videoManifest, {
    onEnter({ pageIndex }) {
      lockPageIndex = pageIndex;
      lockRoot.hidden = true;
      panel.hidden = false;
      refreshVerdict();
      // Same gesture-triggered behavior as the mature Steel Maidens player.
      // The lockscreen iframe is already destroyed before Awake starts.
      player.enter();
    },
  });

  function refreshVerdict() {
    const next = String(readVerdict() || '今日，胜负未定。').trim();
    verdict.textContent = next || '今日，胜负未定。';
  }

  root.querySelector('[data-back]').addEventListener('click', () => {
    if (!player.snapshot().paused) player.toggle();
    panel.hidden = true;
    lockRoot.hidden = false;
    lockscreen.show(lockPageIndex);
  });
  root.querySelector('[data-prev-track]').addEventListener('click', () => player.step(-1, true));
  root.querySelector('[data-next-track]').addEventListener('click', () => player.step(1, true));
  toggle.addEventListener('click', () => player.toggle());
  select.addEventListener('change', () => player.choose(Number(select.value)));
  progress.addEventListener('input', () => {
    const snap = player.snapshot();
    if (snap.duration > 0) player.seek((Number(progress.value) / 1000) * snap.duration);
  });

  refreshVerdict();

  return {
    refresh: refreshVerdict,
    showLockscreen() {
      if (!player.snapshot().paused) player.toggle();
      panel.hidden = true;
      lockRoot.hidden = false;
      lockscreen.show(lockPageIndex);
    },
    showPanel() {
      lockscreen.hide();
      lockRoot.hidden = true;
      panel.hidden = false;
      refreshVerdict();
    },
    destroy() {
      lockscreen.destroy();
      player.destroy();
      if (!ownsAudio && audio) audio.pause();
      root.innerHTML = '';
    },
  };
}
