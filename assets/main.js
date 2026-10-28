/* 首页脚本：导航吸顶状态、当前区块高亮、手机号按需显示。
   无第三方依赖；不支持 IntersectionObserver 时自动降级，不影响阅读。 */
(function () {
  "use strict";

  /* ---------- 1. 导航吸顶后加分隔线 ---------- */
  var nav = document.getElementById("nav");

  function onScroll() {
    if (!nav) return;
    nav.classList.toggle("is-stuck", window.scrollY > 8);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- 2. 当前区块高亮 ---------- */
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.nav__links a[href^="#"]')
  );

  var targets = links
    .map(function (a) {
      var el = document.querySelector(a.getAttribute("href"));
      return el ? { link: a, el: el } : null;
    })
    .filter(Boolean);

  function setActive(link) {
    links.forEach(function (a) {
      a.classList.toggle("is-active", a === link);
    });
  }

  if (targets.length && "IntersectionObserver" in window) {
    var visible = {};

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          visible[e.target.id] = e.isIntersecting ? e.intersectionRatio : 0;
        });

        var best = null;
        targets.forEach(function (t) {
          var r = visible[t.el.id] || 0;
          if (r > 0 && (!best || r > best.r)) best = { r: r, link: t.link };
        });

        if (best) setActive(best.link);
        else if (window.scrollY < 120) setActive(null);
      },
      { rootMargin: "-72px 0px -55% 0px", threshold: [0.05, 0.25, 0.5, 0.75] }
    );

    targets.forEach(function (t) {
      io.observe(t.el);
    });
  }

  /* ---------- 3. 手机号显示 / 隐藏 ---------- */
  var phone = document.getElementById("phone");
  var btn = document.getElementById("phoneBtn");

  if (phone && btn) {
    var full = phone.getAttribute("data-full") || "";
    var masked = phone.textContent;
    var shown = false;

    btn.addEventListener("click", function () {
      shown = !shown;
      phone.textContent = shown ? full : masked;
      btn.textContent = shown ? "隐藏" : "查看";
      btn.setAttribute("aria-expanded", shown ? "true" : "false");
    });
  }

  /* ---------- 4. 简历说明弹窗 ---------- */
  var modal = document.getElementById("resumeModal");
  var openers = Array.prototype.slice.call(
    document.querySelectorAll('[data-modal-open="resume"]')
  );

  if (modal && openers.length) {
    var lastFocus = null;

    function openModal() {
      lastFocus = document.activeElement;
      modal.hidden = false;
      document.body.style.overflow = "hidden";

      var card = modal.querySelector(".modal__card");
      if (card) card.focus();
    }

    function closeModal() {
      modal.hidden = true;
      document.body.style.overflow = "";

      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    openers.forEach(function (trigger) {
      trigger.addEventListener("click", openModal);
    });

    /* 点遮罩、点 × 、点「知道了」都关闭 */
    modal.addEventListener("click", function (e) {
      if (e.target.closest("[data-close]")) closeModal();
    });

    document.addEventListener("keydown", function (e) {
      if (modal.hidden) return;

      if (e.key === "Escape") {
        closeModal();
        return;
      }

      if (e.key !== "Tab") return;

      /* 焦点锁在弹窗内，避免 Tab 跑到被遮住的页面上 */
      var focusables = modal.querySelectorAll("button, a[href]");
      if (!focusables.length) return;

      var first = focusables[0];
      var last = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });
  }
})();
