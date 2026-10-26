# 工具铺 - 站点仓库

这是 myfnos.men 的源码仓库。纯静态站，无构建，改完推送即自动发布。

## 目录结构

```
site/
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
└── img/                  图标和图片
```

## 如何新增一个软件

1. 复制 `apps/moviepilot-fnos-lite.html` 改名（如 `apps/xxx.html`），修改内容
2. 编辑 `data/apps.json`，照现有格式加一条（id、名称、简介、版本、下载链接）
3. 图标放到 `img/`，在 apps.json 里写相对路径
4. 提交（Commit）到 main 分支 → Cloudflare 自动部署，约 1 分钟生效

## 如何发布教程

1. 复制 `posts/` 下任意一篇改名，改标题和正文（正文是普通 HTML，用 `<h2>`、`<p>`、`<pre>`、`.tip`/`.warn` 提示框）
2. 编辑 `data/posts.json` 加一条
3. 提交推送即发布

## 小改动

- 改站名 / GitHub 链接：`data/site.json`
- 改下载链接：`data/apps.json` 里的 `downloads`
- 改完提交后不需要动 Cloudflare，自动部署
