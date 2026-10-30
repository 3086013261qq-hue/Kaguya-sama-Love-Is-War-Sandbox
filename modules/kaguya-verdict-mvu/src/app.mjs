import { createPlayer } from './player.mjs';
import { createVideoLockscreen } from './lockscreen.mjs';
function fmtTime(value) {
  if (!Number.isFinite(value) || value < 0) return '0:00';
  const m = Math.floor(value / 60);
  const s = Math.floor(value % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

export function mountKaguyaVerdictMvu(root, { musicManifest, videoManifest, getVerdict, onEnter, session = {} } = {}) {
  if (!root) throw new Error('MVU root missing');
  const doc = root.ownerDocument || document;
  const readVerdict = typeof getVerdict === 'function' ? getVerdict : () => '今日，胜负未定。';
  const entered = typeof onEnter === 'function' ? onEnter : () => {};

  root.classList.add('kg-mvu');
  root.innerHTML = `
    <section class="kg-outer" data-outer>
      <div class="kg-outer__frame"><span class="kg-outer__edition">LOVE IS WAR · SHUCHIIN</span>
      <div class="kg-outer__crown" aria-hidden="true">♛</div><div class="kg-outer__heart" aria-hidden="true">♥</div>
      <h2>辉夜大小姐<span>想让我告白</span></h2><p class="kg-outer__subtitle">秀知院大学 × JOJO</p>
      <span class="kg-outer__jp">恋愛頭脳戦</span>
      <button type="button" class="kg-outer__unlock" data-unlock aria-label="解锁进入双视频页">⌃<small>轻触 · 解锁</small></button>
      <span class="kg-outer__folio">THE BATTLE BEGINS WITH A HEART.</span></div>
    </section>
    <section data-lockscreen hidden></section>
    <section class="kg-panel" data-panel hidden>
      <button type="button" class="kg-panel__back" data-back>‹ 映像集</button>
      <div class="kg-verdict-card">
        <div class="kg-verdict-strip">
          <div class="kg-verdict-card__jp">本日の勝敗</div>
          <div class="kg-verdict-card__text" data-verdict>今日，胜负未定。</div>
          <div class="kg-verdict-card__stamp">敗北</div>
        </div>
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

  const outer = root.querySelector('[data-outer]');
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

  let audio = doc.querySelector('audio[data-kaguya-mvu-audio]');
  if (!audio) {
    audio = doc.createElement('audio');
    audio.dataset.kaguyaMvuAudio = '1';
    audio.style.display = 'none';
    doc.body.appendChild(audio);
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

  let lockPageIndex = session.pageIndex ?? videoManifest.default_page ?? 0;
  const setStage = stage => { session.stage = stage; };
  const lockscreen = createVideoLockscreen(lockRoot, videoManifest, {
    initialPage: lockPageIndex,
    onPage(index) { session.pageIndex = index; lockPageIndex = index; },
    onEnter({ pageIndex }) {
      setStage('panel');
      lockPageIndex = pageIndex;
      lockRoot.hidden = true;
      panel.hidden = false;
      refreshVerdict();
      entered();
      player.enter();
    },
  });

  function refreshVerdict() {
    const next = String(readVerdict() || '今日，胜负未定。').trim();
    verdict.textContent = next || '今日，胜负未定。';
    root.querySelector('.kg-verdict-card__stamp').hidden = !/败北|敗北|双败|雙敗/.test(next);
  }

  root.querySelector('[data-unlock]').addEventListener('click', () => {
    setStage('video'); outer.hidden = true; lockscreen.show(lockPageIndex);
  });
  let startY = null;
  outer.addEventListener('touchstart', e => { startY = e.touches?.[0]?.clientY ?? null; }, {passive:true});
  outer.addEventListener('touchend', e => {
    if (startY !== null && startY - (e.changedTouches?.[0]?.clientY ?? startY) > 54) root.querySelector('[data-unlock]').click();
    startY = null;
  }, {passive:true});

  root.querySelector('[data-back]').addEventListener('click', () => {
    if (!player.snapshot().paused) player.toggle();
    setStage('video');
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
  lockscreen.hide();
  if (session.stage === 'panel') { outer.hidden = true; panel.hidden = false; }
  else if (session.stage === 'video') { outer.hidden = true; lockscreen.show(lockPageIndex); }

  return {
    refresh: refreshVerdict,
    showLockscreen() {
      if (!player.snapshot().paused) player.toggle();
      panel.hidden = true;
      lockRoot.hidden = false;
      lockscreen.show(lockPageIndex);
    },
    showPanel() {
      setStage('panel'); outer.hidden = true;
      lockscreen.hide();
      lockRoot.hidden = true;
      panel.hidden = false;
      refreshVerdict();
    },
    destroy() {
      lockscreen.destroy();
      player.destroy();
      root.innerHTML = '';
    },
  };
}
