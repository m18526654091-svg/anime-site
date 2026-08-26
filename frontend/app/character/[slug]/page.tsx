import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchCharacterBySlug } from "@/lib/api";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

function trimText(s: string, max = 150): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  try {
    const ch = await fetchCharacterBySlug(params.slug);
    const animeName = ch.anime?.chinese_title || ch.anime?.title || "";
    const va = ch.voice_actors?.[0]?.name || "";
    const pageTitle = `${ch.name}${animeName ? ` - ${animeName}角色` : ""} | AnimeHub`;
    const description = trimText(
      `${ch.name}${animeName ? `是${animeName}的角色` : ""}${va ? `，由声优${va}配音` : ""}。${ch.description || ""}`,
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

  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      <nav className="mb-4 text-sm text-slate-400">
        <Link href="/" className="hover:text-pink-400">首页</Link>
        <span className="mx-2">/</span>
        <Link href={`/anime/${ch.anime?.slug}/`} className="hover:text-pink-400">
          {ch.anime?.chinese_title || ch.anime?.title}
        </Link>
        <span className="mx-2">/</span>
        <span>{ch.name}</span>
      </nav>

      <h1 className="text-3xl font-black text-white">{ch.name}</h1>
      {ch.name_en && <p className="mt-1 text-sm text-slate-400">{ch.name_en}</p>}
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

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Person",
            name: ch.name,
            ...(ch.description ? { description: ch.description } : {}),
            ...(ch.anime
              ? { affiliation: { "@type": "Organization", name: ch.anime.chinese_title || ch.anime.title } }
              : {}),
          }),
        }}
      />
    </div>
  );
}
