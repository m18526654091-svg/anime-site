import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchCharacterBySlug, fetchCharactersByAnime } from "@/lib/api";
import type { Metadata } from "next";
import type { AnimeCharacter } from "@/lib/api";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

function trimText(s: string, max = 150): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

/** Phase 40-A：英文优先主显示名（name_en || name，不伪造翻译） */
function primaryName(ch: { name: string; name_en?: string | null }): string {
  return ch.name_en || ch.name;
}

/** 拆分别名并去重，去除与主名/英文名重复的项 */
function parseAliases(name: string, nameEn: string, aliases: string): string[] {
  return Array.from(
    new Set(
      (aliases || "")
        .split(/[，,、/]+/)
        .map((a) => a.trim())
        .filter(Boolean),
    ),
  ).filter((a) => a !== name && a.toLowerCase() !== String(nameEn || "").toLowerCase());
}

/**
 * 组装 title 补充名（别名 / 日文名）。
 * Phase 40-A：主名改为英文优先，补充名排除与主名重复的项（name_en/native）。
 */
function buildExtraNames(ch: {
  name: string;
  name_en?: string | null;
  aliases?: string;
  native_name?: string | null;
}): string[] {
  const primary = primaryName(ch);
  const extra: string[] = [];
  if (ch.name_en && ch.name_en !== primary) extra.push(ch.name_en);
  if (ch.native_name && ch.native_name !== primary) extra.push(ch.native_name);
  extra.push(...parseAliases(ch.name, ch.name_en || "", ch.aliases || ""));
  return Array.from(new Set(extra)).filter(Boolean);
}

/** sameAs：仅在存在可核验的外部 ID 时输出（当前 API 未暴露，防御式） */
function buildSameAs(ch: unknown): string[] {
  const source = String(((ch as { source?: string }).source) || "").toLowerCase();
  const sourceId = (ch as { source_id?: number | string }).source_id;
  if (!source || !sourceId) return [];
  if (source.includes("anilist")) return [`https://anilist.co/character/${sourceId}`];
  if (source.includes("mal")) return [`https://myanimelist.net/character/${sourceId}`];
  return [];
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  try {
    const ch = await fetchCharacterBySlug(params.slug);
    const animeName = ch.anime?.chinese_title || ch.anime?.title || "";
    const vaNames = (ch.voice_actors || [])
      .map((v) => v.name)
      .filter(Boolean)
      .join("、");
    const extra = buildExtraNames(ch).join(" / ");
    // Phase 40-A：只替换 name 来源为英文优先（保留现有模板结构，不发明新模板）
    const primary = primaryName(ch);
    const pageTitle = `${primary}${extra ? `（${extra}）` : ""}${
      animeName ? ` - ${animeName}角色` : ""
    } | AnimeHub`;
    const description = trimText(
      `${primary}${animeName ? `是${animeName}的角色` : "角色"}${
        vaNames ? `，由声优${vaNames}配音` : ""
      }。${extra ? `别称：${extra}。` : ""}${ch.description || ""}`,
    );
    return {
      title: { absolute: pageTitle },
      description,
      robots: { index: true, follow: true },
      alternates: { canonical: `${SITE_BASE}/character/${ch.slug}/` },
    };
  } catch {
    return { title: "角色不存在", robots: { index: false, follow: false } };
  }
}

export default async function CharacterPage({ params }: { params: { slug: string } }) {
  let ch;
  try {
    ch = await fetchCharacterBySlug(params.slug);
  } catch {
    notFound();
  }

  // Sprint 6-F：SSR 同作品其他角色互链（复用现有 GET /api/characters?anime_id=）
  let siblings: AnimeCharacter[] = [];
  if (ch.anime?.id) {
    try {
      siblings = (await fetchCharactersByAnime(ch.anime.id)).filter((c) => c.id !== ch.id);
    } catch {
      siblings = [];
    }
  }

  const primary = primaryName(ch);
  const extraNames = buildExtraNames(ch);
  const sameAs = buildSameAs(ch);

  const ld = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: primary,
    ...(ch.native_name && ch.native_name !== primary ? { additionalName: ch.native_name } : {}),
    ...(extraNames.length ? { alternateName: extraNames } : {}),
    ...(ch.description ? { description: ch.description } : {}),
    ...(ch.image ? { image: ch.image } : {}),
    ...(sameAs.length ? { sameAs } : {}),
    ...(ch.anime
      ? { affiliation: { "@type": "Organization", name: ch.anime.chinese_title || ch.anime.title } }
      : {}),
  };

  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      <nav className="mb-4 text-sm text-slate-400">
        <Link href="/" className="hover:text-pink-400">首页</Link>
        <span className="mx-2">/</span>
        {ch.anime && (
          <>
            <Link href={`/anime/${ch.anime.slug}/`} className="hover:text-pink-400">
              {ch.anime.chinese_title || ch.anime.title}
            </Link>
            <span className="mx-2">/</span>
          </>
        )}
        <span>{primary}</span>
      </nav>

      <h1 className="text-3xl font-black text-white">{primary}</h1>
      {extraNames.length > 0 && (
        <p className="mt-1 text-sm text-slate-400">{extraNames.join(" / ")}</p>
      )}
      {ch.aliases && <p className="mt-1 text-sm text-slate-500">别名：{ch.aliases}</p>}

      {ch.description && (
        <p className="mt-5 leading-7 text-slate-300">{ch.description}</p>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {ch.anime && (
          <Link href={`/anime/${ch.anime.slug}/`}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-pink-500/50">
            <p className="text-xs text-slate-400">所属动漫</p>
            <p className="mt-1 font-bold text-white">{ch.anime.chinese_title || ch.anime.title}</p>
          </Link>
        )}
        {ch.voice_actors?.map((va) => (
          <Link key={va.id} href={`/voice-actor/${va.slug}/`}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-pink-500/50">
            <p className="text-xs text-slate-400">配音声优</p>
            <p className="mt-1 font-bold text-white">{va.name}</p>
          </Link>
        ))}
      </div>

      {/* Sprint 6-F：同作品其他角色（SSR 互链，复用 GET /api/characters?anime_id=） */}
      {siblings.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-4 text-xl font-bold text-white">同作其他角色</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {siblings.map((c) => (
              <Link
                key={c.id}
                href={`/character/${c.slug}/`}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-pink-500/50"
              >
                <p className="font-bold text-white">{c.name}</p>
                {c.voice_actors && c.voice_actors.length > 0 && (
                  <p className="mt-1 text-sm text-slate-400">
                    配音：{c.voice_actors.map((v) => v.name).join("、")}
                  </p>
                )}
              </Link>
            ))}
          </div>
        </section>
      )}

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }}
      />
    </div>
  );
}
