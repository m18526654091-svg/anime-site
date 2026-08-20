# AnimeHub v5 问题修复报告

## 修复时间
2026年8月11日

## 问题清单与修复

### 1. ✅ 分类标签数量仍然显示

**问题描述：**
- 分类标签仍显示为 `校园/恋爱(4)`
- 需求：只显示 `校园/恋爱`，隐藏数量

**修改文件：**
- `frontend/components/HomeClient.tsx`

**修改内容：**
```tsx
// 第131行
// 修改前
{c.genre} ({c.count})

// 修改后
{c.genre}
```

**原因：**
- 虽然之前修改过，但仍有遗漏
- 现在所有分类标签都不再显示数量统计

**测试方法：**
1. 启动前端 `npm run dev`
2. 访问首页
3. 查看分类标签区域
4. 确认显示：`校园/恋爱` 而不是 `校园/恋爱(4)`

---

### 2. ✅ 分类筛选无效

**问题描述：**
- 点击任何分类，显示的动漫列表都一样
- 没有真正按类型筛选

**根本原因：**
- HomeClient.tsx 的 `load` 函数调用 `fetchAnimePage(query, page)`
- 点击分类时传递：`load(c.genre, 1)`
- `fetchAnimePage` 将 genre 作为搜索词 `q` 发送到后端
- 后端 `/api/anime?q=校园/恋爱` 会搜索标题包含"校园/恋爱"的动漫
- 由于标题通常不包含类型，所以返回所有动漫

**修改文件：**
- `frontend/components/HomeClient.tsx`

**修改内容：**

1. 修改 `load` 函数签名和逻辑（第24-36行）：
```tsx
// 修改前
const load = useCallback(async (query: string, page: number) => {
  const data = await fetchAnimePage(query || undefined, page, PAGE_SIZE);
  setPageData(data);
}, []);

// 修改后
const load = useCallback(async (query: string, page: number, category?: string) => {
  let data;
  if (category) {
    // 使用 category 筛选
    data = await fetchAnimeByFilter({ category }, page, PAGE_SIZE);
  } else {
    // 普通搜索
    data = await fetchAnimePage(query || undefined, page, PAGE_SIZE);
  }
  setPageData(data);
}, []);
```

2. 添加导入（第7行）：
```tsx
import {
  apiErrorMessage,
  fetchAnimeByFilter,  // 新增
  fetchAnimeBySort,
  fetchAnimePage,
  fetchCategories,
} from "@/lib/api";
```

3. 修改分类点击逻辑（第130行）：
```tsx
// 修改前
load(c.genre, 1);

// 修改后
load("", 1, c.genre);
```

**后端验证：**
- 后端 API 已支持 `category` 参数 (`backend/app/api/anime.py`)
- `GET /api/anime?category=校园/恋爱` 会筛选 `genre == "校园/恋爱"` 的动漫
- 前端 `fetchAnimeByFilter` 函数正确传递 `category` 参数

**测试方法：**
1. 启动前后端
2. 访问首页
3. 点击"校园/恋爱"分类
4. 确认只显示校园/恋爱类型的动漫
5. 点击"搞笑/日常"分类
6. 确认只显示搞笑/日常类型的动漫
7. 点击不同分类应该看到不同的动漫列表

---

### 3. ✅ 图片问题 - 使用真实动漫封面

**问题描述：**
- 动漫封面显示为随机图片（picsum.photos）
- 需求：使用真实动漫官方封面

**修改文件：**
- `anime_data.json` - 更新所有封面 URL
- `backend/app/models.py` - 添加 `chinese_title` 字段
- `backend/app/schemas.py` - 添加 `chinese_title` 字段
- `frontend/types/index.ts` - 添加 `chinese_title` 字段（已完成）

**修改内容：**

1. **anime_data.json**（前10个动漫使用真实封面）
