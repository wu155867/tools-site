# 工具铺 - 站点仓库

这是 myfnos.men 的源码仓库。纯静态站，`build.py` 会把 `data/*.json` 的内容（顶栏、页脚、软件卡、教程列表、版本号）渲染进 HTML，搜索引擎和分享卡片能直接读到内容。

## 快速上手

改完任何文件后，在仓库根目录跑一次：

```
python3 build.py
```

然后提交推送 → Cloudflare Pages 自动部署（约 1 分钟）。

## 目录结构

```
├── index.html            首页
├── blog.html             教程列表
├── about.html            关于
├── 404.html              404 页
├── apps/                 每个软件一个详情页（HTML）
├── posts/                每篇教程一个页面（HTML）
├── data/
│   ├── site.json         站名 / 导航 / GitHub 链接（一处改全站生效）
│   ├── apps.json         软件列表（首页卡片的数据来源）
│   └── posts.json        教程列表数据
├── assets/               样式和脚本
├── img/                  图标和截图
├── scripts/
│   └── sync_release.py   从 GitHub Release 拉最新版本号更新 apps.json
├── build.py              静态构建（渲染 header/footer/列表/版本号，生成 sitemap）
└── .github/workflows/    每日自动同步 Release 版本号并重建
```

## 自动版本同步

`.github/workflows/sync-release.yml` 每天检查一次 `wu155867/moviepilot-fnos-lite` 的最新 Release：

- 有新版本 → 自动更新 `data/apps.json` 的版本号和日期 → 重跑 `build.py` → 提交推送 → 站点自动显示新版
- 详情页的**更新日志**和**「当前」徽章**是人工内容，发新版后记得手动补一条

## 如何新增一个软件

1. 复制 `apps/moviepilot-fnos-lite.html` 改名（如 `apps/xxx.html`），修改内容
2. 编辑 `data/apps.json`，照现有格式加一条（id、名称、简介、版本、下载链接）
3. 图标放到 `img/`，在 apps.json 里写相对路径
4. 跑 `python3 build.py`，提交推送

软件超过 4 款后再考虑加回平台筛选栏（样式已删，需要时重写）。

## 如何发布教程

1. 复制 `posts/` 下任意一篇改名，改标题和正文（用 `<h2>`、`<p>`、`<pre>`、`.tip`/`.warn` 提示框）
2. 编辑 `data/posts.json` 加一条
3. 跑 `python3 build.py`，提交推送

## 小改动

- 改站名 / 导航 / GitHub 链接：`data/site.json`（build 会渲染进每一页）
- 改下载链接：`data/apps.json` 里的 `downloads`
- 改版本号：正常由 Actions 自动同步；手动改就编辑 `data/apps.json` 后跑 build
- 换截图：替换 `img/shot-hero.jpg` 并把引用处的 `?v=1` 递增
