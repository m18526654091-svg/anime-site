# AnimeHub Phase 23 — GSC Setup

> 生成于 2026-08-29

## Required Actions

1. **验证域所有权**：Google Search Console → 域名验证（DNS TXT 或 HTML 文件）→ bunivoa.com
2. **提交 sitemap**：`https://bunivoa.com/sitemap.xml`
3. **检查索引状态**：
   - Pages indexed
   - Pages not indexed
   - Crawled - currently not indexed
   - Discovered - currently not indexed

## Weekly Tracking Template

| Date | Indexed | Excluded | Clicks | Impressions | CTR | Avg Position |
|---|---|---|---|---|---|---|
| | | | | | | |

## 前置条件
- **生产部署**本地 12 个 pending release（Phase 10-22），否则 GSC 数据反映旧代码
- 部署后重提 sitemap（dups 应=0）
- GA4：设 `NEXT_PUBLIC_GA_ID` 后重建

## 数据原则
- 无 GSC 权限前不填数据（不伪造）
- 首周重点：indexed/sitemap 提交比 + 种子关键词位置
