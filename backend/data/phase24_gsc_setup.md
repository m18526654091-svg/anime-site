# AnimeHub Phase 24 — GSC Setup

> 生成于 2026-08-29

## Required Steps

1. **添加域名验证**：Google Search Console → 域名验证（DNS TXT / HTML 文件）→ `bunivoa.com`
2. **提交 sitemap**：`https://bunivoa.com/sitemap.xml`
3. **等待状态**：
   - Discovered
   - Crawled
   - Indexed

## 索引状态跟踪

| 状态 | 数量 | 备注 |
|---|---|---|
| Discovered - currently not indexed | WAITING FOR REAL DATA | |
| Crawled - currently not indexed | WAITING FOR REAL DATA | |
| Indexed | WAITING FOR REAL DATA | |
| Excluded | WAITING FOR REAL DATA | |

## 前置条件
- **生产部署必须完成**（当前 dups=9，未达标）后再提交 sitemap
- 部署后重提 sitemap，确认 dups=0

## 数据原则
- 所有 GSC 数据标记 **WAITING FOR REAL DATA**（不模拟、不伪造）
- 未接入 GSC 前不做任何基于数据的优化动作
