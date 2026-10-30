import { mountKaguyaVerdictMvu } from './app.mjs';

const HOST = 'kg-mvu-host';
const STYLE_ID = 'kg-mvu-style-v1';
const MUSIC_URL = new URL('../../../mvu/music-manifest.v1.json', import.meta.url).href;
const VIDEO_URL = new URL('../../../mvu/video-lockscreen-manifest.v1.json', import.meta.url).href;
const STYLE_URL = new URL('./styles.css', import.meta.url).href;

let active = null;
let manifestsPromise = null;

function doc() {
  try { return window.parent.document; } catch { return document; }
}

function ensureStyle() {
  const d = doc();
  if (d.getElementById(STYLE_ID)) return;
  const link = d.createElement('link');
  link.id = STYLE_ID;
  link.rel = 'stylesheet';
  link.href = STYLE_URL;
  d.head.appendChild(link);
}

function resetGlobalAudio() {
  try {
    const audio = doc().querySelector('audio[data-kaguya-mvu-audio]');
    if (!audio) return;
    audio.pause();
    audio.removeAttribute('src');
    delete audio.dataset.kaguyaTrackId;
    audio.load();
  } catch {}
}

async function manifests() {
  if (!manifestsPromise) {
    manifestsPromise = Promise.all([
      fetch(MUSIC_URL).then(r => { if (!r.ok) throw new Error(`music manifest ${r.status}`); return r.json(); }),
      fetch(VIDEO_URL).then(r => { if (!r.ok) throw new Error(`video manifest ${r.status}`); return r.json(); }),
    ]).then(([musicManifest, videoManifest]) => ({ musicManifest, videoManifest }));
  }
  return manifestsPromise;
}

function chatMessage(id) {
  try {
    const list = getChatMessages(id);
    return list && list[0] ? list[0] : null;
  } catch {
    return null;
  }
}

function isEligible(id) {
  const m = chatMessage(id);
  if (!m) return false;
  return m.is_user !== true && m.role !== 'user';
}

function latestEligibleId() {
  let last = -1;
  try { last = Number(getLastMessageId()); } catch {}
  for (let id = last; id >= 0; id--) {
    if (isEligible(id)) return id;
  }
  return -1;
}

function textBox(id) {
  try { return doc().querySelector(`#chat > .mes[mesid="${id}"] .mes_text`); }
  catch { return null; }
}

function unwrap(v) {
  return Array.isArray(v) && v.length === 2 && typeof v[1] === 'string' ? v[0] : v;
}

function readVerdict(id) {
  try {
    const data = Mvu.getMvuData({ type: 'message', message_id: id });
    const value = unwrap(data?.stat_data?.today_verdict);
    if (typeof value === 'string' && value.trim()) return value.trim();
  } catch {}
  try {
    const vars = getVariables({ type: 'message', message_id: id });
    const value = unwrap(vars?.stat_data?.today_verdict);
    if (typeof value === 'string' && value.trim()) return value.trim();
  } catch {}
  return '今日，胜负未定。';
}

function clearHosts(exceptId = -1) {
  const d = doc();
  d.querySelectorAll(`.${HOST}`).forEach(node => {
    if (Number(node.dataset.messageId) !== exceptId) node.remove();
  });
}

async function mountLatest() {
  const id = latestEligibleId();
  if (id < 0) {
    if (active) { active.app.destroy(); active = null; }
    clearHosts();
    return;
  }

  const box = textBox(id);
  if (!box) return;

  if (active?.id === id && active.host?.isConnected) {
    active.app.refresh();
    return;
  }

  if (active) {
    try { active.app.destroy(); } catch {}
    active.host?.remove();
    active = null;
  }
  clearHosts();

  ensureStyle();
  const { musicManifest, videoManifest } = await manifests();
  if (!textBox(id)) return;

  const d = doc();
  const host = d.createElement('div');
  host.className = HOST;
  host.dataset.messageId = String(id);
  box.appendChild(host);

  const top = window.parent;
  const app = mountKaguyaVerdictMvu(host, {
    musicManifest,
    videoManifest,
    getVerdict: () => readVerdict(id),
    onEnter: () => { top.__kaguyaMvuEntered = true; },
  });

  active = { id, host, app };
  if (top.__kaguyaMvuEntered === true) app.showPanel();
}

function refreshActive() {
  try { active?.app?.refresh(); } catch {}
}

$(async () => {
  try { await waitGlobalInitialized('Mvu'); } catch {}
  const ev = (typeof Mvu === 'object' && Mvu && Mvu.events) || {};
  const remountSoon = () => { setTimeout(() => mountLatest().catch(console.error), 0); setTimeout(() => mountLatest().catch(console.error), 500); };
  const refreshSoon = () => { setTimeout(refreshActive, 0); setTimeout(refreshActive, 700); };

  eventOn(ev.VARIABLE_UPDATE_ENDED || 'mag_variable_update_ended', refreshSoon);
  eventOn(ev.VARIABLE_INITIALIZED || 'mag_variable_initialized', refreshSoon);
  eventOn(tavern_events.CHARACTER_MESSAGE_RENDERED, remountSoon);
  eventOn(tavern_events.MESSAGE_UPDATED, remountSoon);
  eventOn(tavern_events.MESSAGE_SWIPED, remountSoon);
  eventOn(tavern_events.MESSAGE_DELETED, remountSoon);
  eventOn(tavern_events.CHAT_CHANGED, () => {
    resetGlobalAudio();
    window.parent.__kaguyaMvuEntered = false;
    remountSoon();
  });

  await mountLatest();
});

$(window).on('pagehide', () => {
  resetGlobalAudio();
  try { active?.app?.destroy(); } catch {}
  active = null;
  clearHosts();
});
