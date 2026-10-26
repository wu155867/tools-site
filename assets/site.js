(function () {
  "use strict";

  var ROOT = (document.documentElement.getAttribute("data-root") || "./").replace(/\/?$/, "/");
  var PAGE = document.body.getAttribute("data-page") || "";
  var $ = function (sel, el) { return (el || document).querySelector(sel); };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function getJSON(path) {
    return fetch(ROOT + path).then(function (r) {
      if (!r.ok) throw new Error(path + " -> " + r.status);
      return r.json();
    });
  }

  var GH_SVG = '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>';

  function renderHeader(cfg) {
    var navHtml = (cfg.nav || []).map(function (n) {
      return '<a href="' + ROOT + n.href + '" data-nav="' + esc(n.key) + '">' + esc(n.text) + '</a>';
    }).join("");
    var gh = cfg.github
      ? '<a class="gh" href="' + esc(cfg.github) + '" target="_blank" rel="noopener">' + GH_SVG + '<span>GitHub</span></a>'
      : "";
    var el = document.createElement("header");
    el.className = "site-header";
    el.innerHTML =
      '<div class="container">' +
        '<a class="logo" href="' + ROOT + 'index.html">' +
          '<img src="' + ROOT + 'img/mp-icon.png?v=2" alt="logo">' +
          '<span>' + esc(cfg.siteName || "") + '</span>' +
          '<span class="logo-sub">' + esc(cfg.tagline || "") + '</span>' +
        '</a>' +
        '<nav class="nav">' + navHtml + gh + '</nav>' +
      '</div>';
    document.body.insertBefore(el, document.body.firstChild);
    var active = el.querySelector('[data-nav="' + PAGE + '"]');
    if (active) active.classList.add("active");
  }

  function renderFooter(cfg) {
    var el = document.createElement("footer");
    el.className = "site-footer";
    var year = new Date().getFullYear();
    el.innerHTML =
      '<div class="container">' +
        '<div class="f-left"><b>' + esc(cfg.siteName || "") + '</b> &copy; ' + year +
          (cfg.github ? ' &middot; <a href="' + esc(cfg.github) + '" target="_blank" rel="noopener" style="color:inherit">GitHub</a>' : "") +
        '</div>' +
        '<div class="f-links">' +
          '<a href="' + ROOT + 'index.html">软件</a>' +
          '<a href="' + ROOT + 'blog.html">教程</a>' +
          '<a href="' + ROOT + 'about.html">关于</a>' +
        '</div>' +
      '</div>';
    document.body.appendChild(el);
  }

  /* ---------- 软件列表 ---------- */

  function primaryDownload(a) {
    var list = a.downloads || [];
    for (var i = 0; i < list.length; i++) if (list[i].primary) return list[i];
    return list[0] || null;
  }

  function appCard(a) {
    var dl = primaryDownload(a);
    var ready = dl && dl.url && dl.url !== "#";
    var btn = ready
      ? '<a class="btn btn-primary btn-sm" href="' + esc(dl.url) + '" target="_blank" rel="noopener">' + esc(dl.name) + '</a>'
      : '<span class="btn btn-primary btn-sm" style="opacity:.45;cursor:not-allowed" title="链接配置中">' + esc(dl ? dl.name : "下载") + ' · 待配置</span>';
    return (
      '<div class="app-card" data-platform="' + esc(a.platform) + '">' +
        '<img class="app-icon" src="' + ROOT + esc(a.icon) + '" alt="' + esc(a.name) + '">' +
        '<div class="info">' +
          '<h3><a href="' + ROOT + esc(a.href) + '">' + esc(a.name) + '</a>' +
            '<span class="ver">v' + esc(a.version) + '</span>' +
            '<span class="tag">' + esc(a.platform) + '</span>' +
          '</h3>' +
          '<div class="desc">' + esc(a.desc) + '</div>' +
          '<div class="meta"><span>更新于 ' + esc(a.updated) + '</span></div>' +
        '</div>' +
        '<div class="side">' + btn + '<span class="size">' + esc(a.size || "") + '</span></div>' +
      '</div>'
    );
  }

  function renderAppList(apps) {
    var wrap = $("#appList");
    if (!wrap) return;
    wrap.innerHTML = apps.map(appCard).join("");
    var bar = $("#filterBar");
    if (!bar) return;
    bar.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      bar.querySelectorAll("button").forEach(function (b) { b.classList.toggle("on", b === btn); });
      var pf = btn.getAttribute("data-filter");
      wrap.querySelectorAll(".app-card").forEach(function (card) {
        card.style.display = (pf === "all" || card.getAttribute("data-platform") === pf) ? "" : "none";
      });
    });
  }

  /* ---------- 文章列表 ---------- */

  function postItem(p) {
    return (
      '<div class="post-item">' +
        '<span class="date">' + esc(p.date) + '</span>' +
        '<div style="flex:1;min-width:0">' +
          '<a class="title" href="' + ROOT + 'posts/' + esc(p.slug) + '.html">' + esc(p.title) + '</a>' +
          '<div class="desc">' + esc(p.desc) + '</div>' +
        '</div>' +
        '<span class="tag">' + esc(p.tag || "文章") + '</span>' +
      '</div>'
    );
  }

  function renderPosts(posts, limit) {
    var wrap = $("#postList");
    if (!wrap) return;
    var list = limit ? posts.slice(0, limit) : posts;
    wrap.innerHTML = list.length
      ? list.map(postItem).join("")
      : '<div class="post-item"><div style="flex:1"><span class="title" style="color:var(--faint)">文章筹备中</span></div></div>';
  }

  /* ---------- 启动 ---------- */

  getJSON("data/site.json")
    .then(function (cfg) {
      renderHeader(cfg);
      renderFooter(cfg);
      return Promise.all([
        getJSON("data/apps.json").catch(function () { return { apps: [] }; }),
        getJSON("data/posts.json").catch(function () { return { posts: [] }; })
      ]).then(function (res) {
        renderAppList(res[0].apps || []);
        renderPosts(res[1].posts || [], PAGE === "blog" ? 0 : 3);
      });
    })
    .catch(function (err) {
      console.error("site.js 初始化失败", err);
    });
})();
