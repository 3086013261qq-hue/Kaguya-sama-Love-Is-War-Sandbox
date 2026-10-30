/**
 * 日漫拟声字视觉插件 / Manga SFX Visualizer
 * v0.1.0
 * Target: Tavern Helper (JS-Slash-Runner) background script
 *
 * Primary cue syntax (invisible without this plugin):
 *   <!--SFX:impact|ドン！！-->
 *   <!--SFX:rumble|ゴゴゴゴゴ……-->
 *   <!--SFX:shock|ガーン！-->
 *
 * Aliases:
 *   warcry -> impact
 *   pressure -> rumble
 *
 * No network requests. No chat/worldbook/variable writes.
 */
(() => {
  'use strict';

  const VERSION = '0.1.0';
  const ROOT_ID = 'manga-sfx-visualizer-root';
  const STYLE_ID = 'manga-sfx-visualizer-style';
  const MAX_CUES_PER_MESSAGE = 4;
  const MAX_TEXT_LENGTH = 24;
  const ACTIVE_NODES = new Set();
  const SEEN = new Set();

  const TYPE_ALIASES = Object.freeze({
    impact: 'impact',
    warcry: 'impact',
    hit: 'impact',
    rumble: 'rumble',
    pressure: 'rumble',
    aura: 'rumble',
    shock: 'shock',
    surprise: 'shock',
    stun: 'shock',
  });

  const parentWindow = window.parent;
  const parentDocument = parentWindow?.document;

  if (!parentDocument?.body) {
    console.warn(`[MangaSFX v${VERSION}] parent document unavailable; plugin disabled.`);
    return;
  }

  const styleText = `
    #${ROOT_ID} {
      position: fixed;
      inset: 0;
      z-index: 2147483000;
      pointer-events: none;
      overflow: hidden;
      contain: layout style paint;
    }
    #${ROOT_ID} .mfx-sfx {
      position: absolute;
      margin: 0;
      padding: 0;
      user-select: none;
      pointer-events: none;
      white-space: pre;
      line-height: 0.92;
      font-family:
        "Noto Sans JP", "Yu Gothic", "Hiragino Kaku Gothic ProN",
        "Arial Black", "Impact", system-ui, sans-serif;
      font-weight: 1000;
      color: #111;
      -webkit-text-stroke: 2px rgba(255,255,255,0.96);
      paint-order: stroke fill;
      text-shadow:
        0 2px 0 rgba(255,255,255,0.92),
        0 7px 18px rgba(0,0,0,0.38);
      will-change: transform, opacity, filter;
      transform-origin: center;
    }
    #${ROOT_ID} .mfx-impact {
      left: 50%;
      top: 44%;
      font-size: clamp(56px, 13vw, 150px);
      transform: translate(-50%, -50%) rotate(-6deg) scale(0.12);
      animation: mfx-impact-pop 1050ms cubic-bezier(.12,.8,.24,1) both;
    }
    #${ROOT_ID} .mfx-rumble {
      right: clamp(10px, 4vw, 52px);
      top: 16%;
      font-size: clamp(38px, 8vw, 92px);
      writing-mode: vertical-rl;
      letter-spacing: .06em;
      opacity: 0;
      transform: rotate(5deg) translateX(24px);
      animation: mfx-rumble-drift 1550ms ease-out both;
    }
    #${ROOT_ID} .mfx-shock {
      left: 50%;
      top: 8%;
      font-size: clamp(48px, 10vw, 112px);
      transform: translate(-50%, -130%) rotate(2deg);
      animation: mfx-shock-drop 1200ms cubic-bezier(.16,.82,.24,1) both;
    }
    @keyframes mfx-impact-pop {
      0%   { opacity: 0; transform: translate(-50%,-50%) rotate(-12deg) scale(.12); filter: blur(7px); }
      18%  { opacity: 1; transform: translate(-50%,-50%) rotate(-4deg) scale(1.16); filter: blur(0); }
      31%  { transform: translate(-50%,-50%) rotate(-8deg) scale(.94); }
      44%  { transform: translate(-50%,-50%) rotate(-5deg) scale(1.02); }
      76%  { opacity: 1; transform: translate(-50%,-50%) rotate(-5deg) scale(1); }
      100% { opacity: 0; transform: translate(-50%,-50%) rotate(-3deg) scale(1.08); }
    }
    @keyframes mfx-rumble-drift {
      0%   { opacity: 0; transform: rotate(7deg) translateX(36px) translateY(8px); filter: blur(3px); }
      18%  { opacity: .88; filter: blur(0); }
      38%  { transform: rotate(4deg) translateX(-3px) translateY(-2px); }
      52%  { transform: rotate(6deg) translateX(3px) translateY(2px); }
      66%  { transform: rotate(4deg) translateX(-2px) translateY(-1px); }
      80%  { opacity: .9; }
      100% { opacity: 0; transform: rotate(5deg) translateX(-14px) translateY(-8px); }
    }
    @keyframes mfx-shock-drop {
      0%   { opacity: 0; transform: translate(-50%,-140%) rotate(3deg) scale(.9); }
      24%  { opacity: 1; transform: translate(-50%,16%) rotate(-2deg) scale(1.08); }
      36%  { transform: translate(-50%,-2%) rotate(1deg) scale(.98); }
      50%  { transform: translate(-50%,5%) rotate(-1deg) scale(1.01); }
      78%  { opacity: 1; }
      100% { opacity: 0; transform: translate(-50%,2%) rotate(0) scale(1.04); }
    }
    @media (prefers-reduced-motion: reduce) {
      #${ROOT_ID} .mfx-sfx {
        animation-duration: 520ms !important;
        filter: none !important;
      }
    }
  `;

  function ensureStage() {
    let style = parentDocument.getElementById(STYLE_ID);
    if (!style) {
      style = parentDocument.createElement('style');
      style.id = STYLE_ID;
      style.textContent = styleText;
      (parentDocument.head || parentDocument.documentElement).appendChild(style);
    }

    let root = parentDocument.getElementById(ROOT_ID);
    if (!root) {
      root = parentDocument.createElement('div');
      root.id = ROOT_ID;
      root.setAttribute('aria-hidden', 'true');
      parentDocument.body.appendChild(root);
    }
    return root;
  }

  function cleanupNode(node) {
    if (!node) return;
    ACTIVE_NODES.delete(node);
    node.remove();
  }

  function normalizeType(type) {
    const key = String(type || 'impact').trim().toLowerCase();
    return TYPE_ALIASES[key] || 'impact';
  }

  function cleanText(text) {
    return String(text ?? '')
      .replace(/<[^>]*>/g, '')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, MAX_TEXT_LENGTH);
  }

  function parseCues(source) {
    const input = String(source ?? '');
    const cues = [];

    // Preferred protocol: invisible HTML comments.
    const commentRe = /<!--\s*SFX(?:\s*:\s*([a-zA-Z_-]+))?\s*\|\s*([\s\S]*?)\s*-->/gi;
    let match;
    while ((match = commentRe.exec(input)) && cues.length < MAX_CUES_PER_MESSAGE) {
      const text = cleanText(match[2]);
      if (text) cues.push({ type: normalizeType(match[1]), text });
    }

    // Compatibility protocol for older drafts.
    const tagRe = /<sfx(?:\s+type\s*=\s*["']?([a-zA-Z_-]+)["']?)?\s*>([\s\S]*?)<\/sfx>/gi;
    while ((match = tagRe.exec(input)) && cues.length < MAX_CUES_PER_MESSAGE) {
      const text = cleanText(match[2]);
      if (text) cues.push({ type: normalizeType(match[1]), text });
    }

    return cues;
  }

  function hashText(text) {
    const input = String(text ?? '');
    let hash = 2166136261;
    for (let i = 0; i < input.length; i += 1) {
      hash ^= input.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(36);
  }

  function showCue(cue, delayMs = 0) {
    const root = ensureStage();
    const node = parentDocument.createElement('div');
    node.className = `mfx-sfx mfx-${cue.type}`;
    node.textContent = cue.text;
    node.setAttribute('role', 'presentation');

    const run = () => {
      root.appendChild(node);
      ACTIVE_NODES.add(node);

      const cleanup = () => cleanupNode(node);
      node.addEventListener('animationend', cleanup, { once: true });
      parentWindow.setTimeout(cleanup, 2200);
    };

    if (delayMs > 0) {
      parentWindow.setTimeout(run, delayMs);
    } else {
      run();
    }
  }

  function playCues(cues) {
    cues.slice(0, MAX_CUES_PER_MESSAGE).forEach((cue, index) => {
      showCue(cue, index * 260);
    });
  }

  function getAssistantMessage(messageId) {
    try {
      const messages = getChatMessages(Number(messageId), { role: 'assistant', include_swipes: false });
      return messages?.[0] || null;
    } catch (error) {
      console.warn('[MangaSFX] getChatMessages failed:', error);
      return null;
    }
  }

  function processMessage(messageId) {
    const message = getAssistantMessage(messageId);
    if (!message?.message) return;

    const cues = parseCues(message.message);
    if (!cues.length) return;

    const fingerprint = `${message.message_id}:${hashText(message.message)}`;
    if (SEEN.has(fingerprint)) return;
    SEEN.add(fingerprint);

    // Bound memory for long sessions.
    if (SEEN.size > 160) {
      const first = SEEN.values().next().value;
      if (first) SEEN.delete(first);
    }

    playCues(cues);
  }

  function preview() {
    showCue({ type: 'impact', text: 'ドン！！' }, 0);
    showCue({ type: 'rumble', text: 'ゴゴゴゴゴ……' }, 650);
    showCue({ type: 'shock', text: 'ガーン！' }, 1350);
  }

  ensureStage();

  // MESSAGE_RECEIVED only fires for newly received messages, so old chat history
  // will not replay its effects when the script is enabled or the page reloads.
  eventOn(
    tavern_events.MESSAGE_RECEIVED,
    errorCatched((messageId) => {
      processMessage(Number(messageId));
    })
  );

  // Optional one-click smoke test configured in the importable script JSON.
  try {
    eventOn(getButtonEvent('拟声字预览'), errorCatched(preview));
  } catch (error) {
    console.debug('[MangaSFX] preview button unavailable:', error);
  }

  $(window).on('pagehide', () => {
    for (const node of [...ACTIVE_NODES]) cleanupNode(node);
    parentDocument.getElementById(ROOT_ID)?.remove();
    parentDocument.getElementById(STYLE_ID)?.remove();
  });

  console.info(`[MangaSFX v${VERSION}] ready`);
})();
