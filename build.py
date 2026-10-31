#!/usr/bin/env python3
"""工具铺静态构建。

把 data/*.json 渲染进 HTML（顶栏 / 页脚 / 软件卡 / 教程列表 / 版本号），并生成 sitemap.xml。
幂等：重复运行只替换标记之间的内容，不会产生重复节点。

用法：python3 build.py   （site/ 目录下；Cloudflare Pages 构建命令同）
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAIN = "https://myfnos.men"

GH_SVG = '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>'
MENU_SVG = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M3 5.5h14M3 10h14M3 14.5h14"/></svg>'


def esc(s):
    return (
        str(s if s is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def primary_download(app):
    dls = app.get("downloads") or []
    for d in dls:
        if d.get("primary"):
            return d
    return dls[0] if dls else None


def header_html(cfg, page, root):
    nav = []
    for n in cfg.get("nav", []):
        cls = ' class="active"' if n.get("key") == page else ""
        nav.append(f'<a href="{root}{esc(n["href"])}" data-nav="{esc(n["key"])}"{cls}>{esc(n["text"])}</a>')
    gh = ""
    if cfg.get("github"):
        gh = f'<a class="gh" href="{esc(cfg["github"])}" target="_blank" rel="noopener">{GH_SVG}<span>GitHub</span></a>'
    return (
        '<header class="site-header">'
        '<div class="container">'
        f'<a class="logo" href="{root}index.html">'
        f'<img src="{root}img/logo-64.png" alt="logo" width="28" height="28">'
        f'<span>{esc(cfg.get("siteName", ""))}</span>'
        f'<span class="logo-sub">{esc(cfg.get("tagline", ""))}</span>'
        '</a>'
        f'<nav class="nav" id="siteNav">{"".join(nav)}{gh}</nav>'
        f'<button class="menu-btn" id="menuBtn" aria-label="打开菜单" aria-expanded="false">{MENU_SVG}</button>'
        '</div>'
        '</header>'
    )


def footer_html(cfg, root):
    year = date.today().year
    gh = ""
    if cfg.get("github"):
        gh = f' &middot; <a href="{esc(cfg["github"])}" target="_blank" rel="noopener" style="color:inherit">GitHub</a>'
    return (
        '<footer class="site-footer">'
        '<div class="container">'
        f'<div class="f-left"><b>{esc(cfg.get("siteName", ""))}</b> &copy; {year}{gh}</div>'
        '<div class="f-links">'
        f'<a href="{root}index.html">软件</a>'
        f'<a href="{root}blog.html">教程</a>'
        f'<a href="{root}about.html">关于</a>'
        '</div>'
        '</div>'
        '</footer>'
    )


def app_card(app, root):
    dl = primary_download(app)
    ready = dl and dl.get("url") and dl["url"] != "#"
    if ready:
        btn = f'<a class="btn btn-primary btn-sm" href="{esc(dl["url"])}" target="_blank" rel="noopener">{esc(dl["name"])}</a>'
    else:
        name = esc(dl["name"]) if dl else "下载"
        btn = f'<span class="btn btn-primary btn-sm" style="opacity:.45;cursor:not-allowed" title="链接配置中">{name} · 待配置</span>'
    return (
        f'<div class="app-card" data-platform="{esc(app.get("platform", ""))}">'
        f'<img class="app-icon" src="{root}{esc(app.get("icon", ""))}" alt="{esc(app.get("name", ""))}" width="58" height="58">'
        '<div class="info">'
        f'<h3><a href="{root}{esc(app.get("href", ""))}">{esc(app.get("name", ""))}</a>'
        f'<span class="ver">v{esc(app.get("version", ""))}</span>'
        f'<span class="tag">{esc(app.get("platform", ""))}</span>'
        '</h3>'
        f'<div class="desc">{esc(app.get("desc", ""))}</div>'
        f'<div class="meta"><span>更新于 {esc(app.get("updated", ""))}</span></div>'
        '</div>'
        f'<div class="side">{btn}<span class="size">{esc(app.get("size", ""))}</span></div>'
        '</div>'
    )


def post_item(post, root):
    return (
        '<div class="post-item">'
        f'<span class="date">{esc(post.get("date", ""))}</span>'
        '<div class="item-body">'
        f'<a class="title" href="{root}posts/{esc(post.get("slug", ""))}.html">{esc(post.get("title", ""))}</a>'
        f'<div class="desc">{esc(post.get("desc", ""))}</div>'
        '</div>'
        f'<span class="tag">{esc(post.get("tag") or "文章")}</span>'
        '</div>'
    )


def inject_block(html, marker, open_default_re, block):
    """替换 <!--@marker-->...<!--/@marker-->；没有标记时按 open_default_re 插入。"""
    pattern = re.compile(rf"<!--@{marker}-->.*?<!--/@{marker}-->", re.S)
    wrapped = f"<!--@{marker}-->{block}<!--/@{marker}-->"
    if pattern.search(html):
        return pattern.sub(lambda m: wrapped, html, count=1)
    m = re.search(open_default_re, html)
    if not m:
        return html
    end = m.end()
    return html[:end] + "\n" + wrapped + html[end:]


def fill_container(html, div_id, block):
    """把内容填进 <div id="...">：已有标记块则替换，否则填充空容器。"""
    pattern = re.compile(rf"<!--@{div_id}-->.*?<!--/@{div_id}-->", re.S)
    wrapped = f"<!--@{div_id}-->{block}<!--/@{div_id}-->"
    if pattern.search(html):
        return pattern.sub(lambda m: wrapped, html, count=1)
    pattern2 = re.compile(rf'(<div id="{div_id}"[^>]*>)(\s*)(</div>)')
    if pattern2.search(html):
        return pattern2.sub(lambda m: m.group(1) + wrapped + m.group(3), html, count=1)
    return html


def process(path, cfg, apps, posts):
    rel = path.relative_to(ROOT).as_posix()
    root = "../" if "/" in rel else "./"
    page_match = re.search(r'<body[^>]*data-page="([^"]*)"', path.read_text(encoding="utf-8"))
    page = page_match.group(1) if page_match else ""
    html = path.read_text(encoding="utf-8")

    # 版本号占位符
    app0 = apps[0] if apps else {}
    html = html.replace("{{APP_VERSION}}", str(app0.get("version", "")))
    html = html.replace("{{APP_UPDATED}}", str(app0.get("updated", "")))

    # 顶栏 / 页脚
    html = inject_block(html, "header", r'<body[^>]*>', header_html(cfg, page, root))
    html = inject_block(html, "footer", r'</main>', footer_html(cfg, root))

    # 列表预渲染（site.js 检测到已有内容会跳过）
    app_html = "".join(app_card(a, root) for a in apps)
    html = fill_container(html, "appList", app_html)
    limit = 0 if page == "blog" else 3
    items = posts if limit == 0 else posts[:limit]
    post_html = "".join(post_item(p, root) for p in items) or (
        '<div class="post-item"><div class="item-body"><span class="title" style="color:var(--faint)">文章筹备中</span></div></div>'
    )
    html = fill_container(html, "postList", post_html)

    path.write_text(html, encoding="utf-8")
    return rel


def write_sitemap(apps, posts):
    today = date.today().isoformat()
    entries = [
        ("", "1.0", "weekly", today),
        ("blog.html", "0.8", "weekly", posts[0]["date"] if posts else today),
        ("about.html", "0.5", "monthly", today),
    ]
    for a in apps:
        entries.append((a["href"], "0.9", "weekly", a.get("updated", today)))
    for p in posts:
        entries.append((f"posts/{p['slug']}.html", "0.7", "monthly", p.get("date", today)))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, pri, freq, lastmod in entries:
        loc = DOMAIN + "/" + path
        lines.append(f'  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>'
                     f'<changefreq>{freq}</changefreq><priority>{pri}</priority></url>')
    lines.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    cfg = load("site.json")
    apps = load("apps.json").get("apps", [])
    posts = load("posts.json").get("posts", [])

    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        rel = process(path, cfg, apps, posts)
        changed.append(rel)

    write_sitemap(apps, posts)
    print(f"build ok: {len(changed)} pages -> {', '.join(changed)}")


if __name__ == "__main__":
    main()
