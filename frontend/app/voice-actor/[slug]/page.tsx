import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchVoiceActorBySlug } from "@/lib/api";
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
    const va = await fetchVoiceActorBySlug(params.slug);
    const roles = va.characters?.slice(0, 3).map((c) => c.name).join("、");
    const pageTitle = `${va.name} - 声优 | AnimeHub`;
    const description = trimText(
      `${va.name}${va.description ? `，${va.description}` : ""}${roles ? ` 代表角色：${roles}` : ""}`,
    );
    return {
      title: { absolute: pageTitle },
      description,
      robots: { index: true, follow: true },
      alternates: { canonical: `${SITE_BASE}/voice-actor/${va.slug}/` },
    };
  } catch {
    return { title: "声优不存在", robots: { index: false, follow: false } };
  }
}

export default async function VoiceActorPage({ params }: { params: { slug: string } }) {
  let va;
  try {
    va = await fetchVoiceActorBySlug(params.slug);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      <nav className="mb-4 text-sm text-slate-400">
        <Link href="/" className="hover:text-pink-400">首页</Link>
        <span className="mx-2">/</span>
        <span>{va.name} 声优</span>
      </nav>

      <h1 className="text-3xl font-black text-white">{va.name}</h1>
      {va.name_en && <p className="mt-1 text-sm text-slate-400">{va.name_en}</p>}

      {va.description && <p className="mt-5 leading-7 text-slate-300">{va.description}</p>}

      {va.characters && va.characters.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-4 text-xl font-bold text-white">配音角色</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {va.characters.map((c) => (
              <Link key={c.id} href={`/character/${c.slug}/`}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-pink-500/50">
                <p className="font-bold text-white">{c.name}</p>
                {c.anime_slug && (
                  <p className="mt-1 text-sm text-slate-400">
                    出自
                    <Link href={`/anime/${c.anime_slug}/`} className="ml-1 text-pink-400 hover:underline">
                      {c.anime_title}
                    </Link>
                  </p>
                )}
              </Link>
            ))}
          </div>
        </section>
      )}

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Person",
            name: va.name,
            ...(va.description ? { description: va.description } : {}),
          }),
        }}
      />
    </div>
  );
}
