"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiErrorMessage, fetchRatings, rateAnime } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const MAX_SCORE = 10;

interface Props {
  animeId: number;
}

export default function RatingWidget({ animeId }: Props) {
  const router = useRouter();
  const { isLoggedIn } = useAuth();

  const [avg, setAvg] = useState(0);
  const [count, setCount] = useState(0);
  const [myScore, setMyScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [hover, setHover] = useState(0);
  const [error, setError] = useState("");

  // Load rating info on mount (avg / count / my_score).
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchRatings(animeId);
        if (!cancelled) {
          setAvg(Number(data.avg_score) || 0);
          setCount(Number(data.rating_count) || 0);
          setMyScore(data.my_score);
        }
      } catch {
        // backend offline; keep empty state
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [animeId]);

  async function handleRate(score: number) {
    // Never send a rating request for anonymous users — send them to login.
    if (!isLoggedIn) {
      router.push("/login");
      return;
    }
    if (submitting) return;
    setSubmitting(true);
    setError("");
    try {
      await rateAnime(animeId, score);
      // Refresh to reflect the new average + my_score.
      const data = await fetchRatings(animeId);
      setAvg(Number(data.avg_score) || 0);
      setCount(Number(data.rating_count) || 0);
      setMyScore(data.my_score);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  const displayed = hover || myScore || 0;

  return (
    <section className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="flex items-center gap-3 text-lg font-semibold text-white">
          <span className="h-5 w-1 rounded-full bg-gradient-to-b from-amber-400 to-pink-500" />
          用户评分
        </h2>
        {!loading && count > 0 && (
          <span className="text-sm text-slate-400">
            ★ {avg.toFixed(1)} · 共 {count} 人评分
          </span>
        )}
      </div>

      {loading ? (
        <p className="py-6 text-center text-sm text-slate-500">评分加载中...</p>
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-1.5">
            {Array.from({ length: MAX_SCORE }, (_, i) => i + 1).map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => handleRate(n)}
                onMouseEnter={() => setHover(n)}
                onMouseLeave={() => setHover(0)}
                disabled={submitting}
                aria-label={`${n} 分`}
                className={`text-xl leading-none transition hover:scale-125 ${
                  displayed >= n ? "text-amber-400" : "text-slate-600"
                }`}
              >
                ★
              </button>
            ))}

            {isLoggedIn && myScore !== null && (
              <span className="ml-2 text-sm text-slate-400">
                我的评分:{" "}
                <span className="font-semibold text-amber-400">{myScore} 分</span>
              </span>
            )}
          </div>

          {!isLoggedIn && (
            <p className="mt-4 text-sm text-slate-400">
              🔒
              <button
                type="button"
                onClick={() => router.push("/login")}
                className="ml-1 font-medium text-pink-400 hover:underline"
              >
                登录后评分
              </button>
            </p>
          )}

          {isLoggedIn && count === 0 && (
            <p className="mt-4 text-sm text-slate-500">暂无评分，快来给这部作品打分吧</p>
          )}

          {submitting && (
            <p className="mt-3 text-sm text-slate-500">提交中...</p>
          )}

          {error && (
            <p className="mt-3 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400">
              {error}
            </p>
          )}
        </>
      )}
    </section>
  );
}