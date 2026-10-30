// Adapted from the mature Transformers-Steel-Maidens single-audio lifecycle.
// One Audio element survives UI rerenders; DOM rendering never creates a second player.
export function createPlayer(audio, manifest, changed = () => {}) {
  const tracks = Array.isArray(manifest?.tracks) ? manifest.tracks : [];
  const defaultId = manifest?.default_track_id;
  if (!tracks.length || new Set(tracks.map(t => t.id)).size !== tracks.length || !tracks.some(t => t.id === defaultId)) {
    throw new Error('辉夜曲库配置无效');
  }

  let current = -1;
  let status = '待播放';
  let disposed = false;
  let attempt = 0;
  let blocked = false;
  const failures = new Set();
  const listeners = [];

  audio.preload = 'metadata';

  function snapshot() {
    return {
      current,
      track: tracks[current] || tracks.find(t => t.id === defaultId) || tracks[0],
      status,
      paused: audio.paused,
      currentTime: Number.isFinite(audio.currentTime) ? audio.currentTime : 0,
      duration: Number.isFinite(audio.duration) ? audio.duration : 0,
      failures: [...failures],
    };
  }

  function emit() {
    if (!disposed) changed(snapshot());
  }

  function validURL(track) {
    try {
      const u = new URL(track.url);
      return u.protocol === 'https:' &&
        u.hostname === 'raw.githubusercontent.com' &&
        u.pathname.includes('/3086013261qq-hue/Kaguya-sama-Love-Is-War-Sandbox/') &&
        u.pathname.includes('/mvu/media/music/');
    } catch {
      return false;
    }
  }

  function select(index) {
    if (disposed || !Number.isInteger(index) || index < 0 || index >= tracks.length) return false;
    if (!validURL(tracks[index])) {
      failures.add(index);
      status = '歌曲地址无效';
      emit();
      return false;
    }
    if (current !== index) {
      attempt++;
      blocked = false;
      audio.pause();
      current = index;
      audio.src = tracks[index].url;
      status = '加载中';
      audio.load();
    }
    emit();
    return true;
  }

  function play() {
    if (disposed) return;
    if (current < 0 && !select(tracks.findIndex(t => t.id === defaultId))) return;
    if (audio.error) {
      failures.delete(current);
      audio.load();
    }
    blocked = false;
    const token = ++attempt;
    try {
      const promise = audio.play();
      Promise.resolve(promise).catch(() => {
        if (!disposed && token === attempt) {
          blocked = true;
          status = '点击播放';
          emit();
        }
      });
    } catch {
      blocked = true;
      status = '点击播放';
      emit();
    }
  }

  function step(offset, skipFailed = false) {
    if (disposed) return;
    const base = current < 0 ? tracks.findIndex(t => t.id === defaultId) : current;
    for (let count = 1; count <= tracks.length; count++) {
      const next = (base + offset * count + tracks.length * count) % tracks.length;
      if (skipFailed && failures.has(next)) continue;
      if (select(next)) {
        play();
        return;
      }
    }
    status = '暂无可播放曲目';
    emit();
  }

  function seek(seconds) {
    if (!Number.isFinite(seconds) || !Number.isFinite(audio.duration)) return;
    audio.currentTime = Math.max(0, Math.min(seconds, audio.duration));
    emit();
  }

  const on = (name, fn) => {
    audio.addEventListener(name, fn);
    listeners.push([name, fn]);
  };

  for (const name of ['loadedmetadata', 'canplay', 'play', 'pause', 'timeupdate']) {
    on(name, () => {
      if (name === 'play') blocked = false;
      if (name !== 'timeupdate') {
        status = blocked ? '点击播放' : name === 'play' ? '播放中' : name === 'pause' ? '已暂停' : audio.paused ? '待播放' : '播放中';
      }
      emit();
    });
  }
  on('ended', () => step(1, true));
  on('error', () => {
    if (current >= 0) failures.add(current);
    status = '加载失败，可重试或切歌';
    emit();
  });

  return {
    snapshot,
    select,
    play,
    step,
    seek,
    enter() {
      if (current < 0) select(tracks.findIndex(t => t.id === defaultId));
      if (audio.paused) play();
    },
    toggle() {
      if (audio.paused) play();
      else {
        attempt++;
        audio.pause();
      }
    },
    choose(index) {
      if (select(index)) play();
    },
    destroy() {
      if (disposed) return;
      disposed = true;
      attempt++;
      listeners.forEach(([name, fn]) => audio.removeEventListener(name, fn));
      audio.pause();
      audio.removeAttribute('src');
      audio.load();
      audio.remove();
    },
  };
}
