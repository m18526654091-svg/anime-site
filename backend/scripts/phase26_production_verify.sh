#!/usr/bin/env bash
# AnimeHub Phase 26 — Production SEO Verification Script
# 在生产服务器（root@43.133.211.250）部署完成后执行：
#   bash backend/scripts/phase26_production_verify.sh
# 或单独下载执行。退出码：0=全部通过，1=存在 FAIL。

set -u
BASE="https://bunivoa.com"
PASS=0
FAIL=0

check() {
  local name="$1"; local cond="$2"
  if [ "$cond" = "true" ]; then PASS=$((PASS+1)); echo "  [PASS] $name";
  else FAIL=$((FAIL+1)); echo "  [FAIL] $name"; fi
}

echo "== 1. robots.txt =="
ROB=$(curl -s -o /tmp/p26_robots.txt -w "%{http_code}" "$BASE/robots.txt")
check "robots HTTP 200 (got $ROB)" "$([ "$ROB" = "200" ] && echo true || echo false)"
check "robots contains Sitemap:" "$(grep -q 'Sitemap:' /tmp/p26_robots.txt && echo true || echo false)"

echo "== 2. sitemap.xml =="
SM=$(curl -s -o /tmp/p26_sitemap.xml -w "%{http_code}" "$BASE/sitemap.xml")
check "sitemap HTTP 200 (got $SM)" "$([ "$SM" = "200" ] && echo true || echo false)"
LOC_COUNT=$(grep -c '<loc>' /tmp/p26_sitemap.xml || true)
echo "  sitemap loc count: $LOC_COUNT (expect ~3470)"
DUP_COUNT=$(grep -o '<loc>[^<]*</loc>' /tmp/p26_sitemap.xml | sort | uniq -d | wc -l)
check "sitemap duplicates = 0 (got $DUP_COUNT)" "$([ "$DUP_COUNT" = "0" ] && echo true || echo false)"

echo "== 3. 抽查页面 =="
PAGES=(
  "/"
  "/anime/monster/"
  "/anime/attack-on-titan/"
  "/anime/monster/similar/"
  "/watch-order/attack-on-titan/"
  "/best-anime/psychological/"
  "/anime-series/fate/"
)
for u in "${PAGES[@]}"; do
  CODE=$(curl -s -o /tmp/p26_page.html -w "%{http_code}" "$BASE$u")
  TITLE=$(grep -c '<title>' /tmp/p26_page.html || true)
  CANON=$(grep -o 'rel="canonical" href="[^"]*"' /tmp/p26_page.html | head -1)
  LD=$(grep -c 'application/ld+json' /tmp/p26_page.html || true)
  echo "  $u HTTP=$CODE title=$TITLE jsonld=$LD canon=$CANON"
  check "$u HTTP 200 (got $CODE)" "$([ "$CODE" = "200" ] && echo true || echo false)"
  check "$u has title" "$([ "$TITLE" -ge 1 ] && echo true || echo false)"
  check "$u has canonical" "$([ -n "$CANON" ] && echo true || echo false)"
  check "$u has JSON-LD" "$([ "$LD" -ge 1 ] && echo true || echo false)"
done

echo "== 4. Phase 10-24 内容（monster detail）=="
MH=$(curl -s "$BASE/anime/monster/")
check "Anime Information present" "$(echo "$MH" | grep -q 'Anime Information' && echo true || echo false)"
check "Genres block present" "$(echo "$MH" | grep -q '>Genres<' && echo true || echo false)"
check "Entity Summary present" "$(echo "$MH" | grep -q 'anime released in' && echo true || echo false)"
check "English UI (no 类型: label)" "$(echo "$MH" | grep -qv '类型:' && echo true || echo false)"

echo ""
echo "======================"
echo "RESULT: PASS=$PASS FAIL=$FAIL"
echo "======================"
[ "$FAIL" = "0" ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED — 见上"
exit $([ "$FAIL" = "0" ] && echo 0 || echo 1)
