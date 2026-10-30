export function createVideoLockscreen(root, manifest, options = {}) {
  if (!root) throw new Error('lockscreen root missing');
  const pages = Array.isArray(manifest?.pages) ? manifest.pages : [];
  if (pages.length !== 2) throw new Error('双页锁屏必须且只能配置2个视频');

  const onEnter = typeof options.onEnter === 'function' ? options.onEnter : () => {};
  let index = Number.isInteger(manifest.default_page) ? manifest.default_page : 0;
  let touchStartX = null;
  let disposed = false;

  root.classList.add('kg-lockscreen');
  root.innerHTML = `
    <div class="kg-lockscreen__shell">
      <div class="kg-lockscreen__eyebrow">秀知院大学 × JOJO</div>
      <div class="kg-lockscreen__video-wrap" data-video-wrap></div>
      <div class="kg-lockscreen__caption">
        <div class="kg-lockscreen__title" data-video-title></div>
        <div class="kg-lockscreen__meta" data-video-meta></div>
      </div>
      <div class="kg-lockscreen__nav">
        <button type="button" class="kg-lockscreen__arrow" data-prev aria-label="上一个视频">‹</button>
        <div class="kg-lockscreen__pager" data-pager></div>
        <button type="button" class="kg-lockscreen__arrow" data-next aria-label="下一个视频">›</button>
      </div>
      <div class="kg-lockscreen__actions">
        <button type="button" class="kg-lockscreen__enter" data-enter>进入秀知院</button>
        <a class="kg-lockscreen__external" data-external target="_blank" rel="noopener noreferrer">在 B 站打开</a>
      </div>
    </div>`;

  const wrap = root.querySelector('[data-video-wrap]');
  const title = root.querySelector('[data-video-title]');
  const meta = root.querySelector('[data-video-meta]');
  const pager = root.querySelector('[data-pager]');
  const external = root.querySelector('[data-external]');
  const prev = root.querySelector('[data-prev]');
  const next = root.querySelector('[data-next]');
  const enter = root.querySelector('[data-enter]');

  function destroyIframe() {
    const old = wrap?.querySelector('iframe');
    if (old) {
      old.src = 'about:blank';
      old.remove();
    }
  }

  function makeIframe(page) {
    destroyIframe();
    const frame = document.createElement('iframe');
    frame.className = 'kg-lockscreen__iframe';
    frame.title = page.title;
    frame.loading = 'eager';
    frame.allow = 'autoplay; fullscreen; picture-in-picture';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.setAttribute('allowfullscreen', 'true');
    frame.src = page.embed_url || page.source_url || page.short_url;
    wrap.appendChild(frame);
  }

  function render() {
    if (disposed) return;
    index = (index + pages.length) % pages.length;
    const page = pages[index];
    makeIframe(page);
    title.textContent = page.title;
    meta.textContent = `${index + 1} / ${pages.length} · ${page.role === 'primary' ? '主锁屏' : '彩蛋页'}`;
    pager.innerHTML = pages.map((_, i) => `<button type="button" class="kg-lockscreen__dot${i === index ? ' is-active' : ''}" data-dot="${i}" aria-label="切换到第${i + 1}页"></button>`).join('');
    pager.querySelectorAll('[data-dot]').forEach(btn => {
      btn.addEventListener('click', () => {
        index = Number(btn.dataset.dot);
        render();
      }, { once: true });
    });
    external.href = page.source_url || page.short_url;
  }

  function move(delta) {
    index += delta;
    render();
  }

  prev.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  enter.addEventListener('click', () => {
    destroyIframe();
    onEnter({ pageIndex: index, page: pages[index] });
  });

  root.addEventListener('touchstart', event => {
    touchStartX = event.touches?.[0]?.clientX ?? null;
  }, { passive: true });

  root.addEventListener('touchend', event => {
    if (touchStartX == null) return;
    const endX = event.changedTouches?.[0]?.clientX;
    if (!Number.isFinite(endX)) return;
    const delta = endX - touchStartX;
    touchStartX = null;
    if (Math.abs(delta) < 54) return;
    move(delta > 0 ? -1 : 1);
  }, { passive: true });

  render();

  return {
    snapshot: () => ({ index, page: pages[index] }),
    show(pageIndex = index) {
      index = Math.max(0, Math.min(pages.length - 1, pageIndex));
      root.hidden = false;
      render();
    },
    hide() {
      destroyIframe();
      root.hidden = true;
    },
    destroy() {
      disposed = true;
      destroyIframe();
      root.innerHTML = '';
    },
  };
}
