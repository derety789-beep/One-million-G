"""Rapport quotidien des statistiques de la chaîne."""

from . import storage, youtube
from .notifier import notify


def _delta(now: int, before: int | None) -> str:
    if before is None:
        return ""
    diff = now - before
    return f" ({'+' if diff >= 0 else ''}{diff:,})".replace(",", " ")


def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def daily_report() -> None:
    s = youtube.channel_statistics()
    subs = int(s.get("subscriberCount", 0))
    views = int(s.get("viewCount", 0))
    videos = int(s.get("videoCount", 0))
    prev = storage.save_stats(subs, views, videos) or {}

    lines = [
        "📊 Rapport YouTube du jour",
        f"👥 Abonnés : {_fmt(subs)}{_delta(subs, prev.get('subscribers'))}",
        f"👁 Vues totales : {_fmt(views)}{_delta(views, prev.get('views'))}",
        f"🎬 Vidéos : {videos}",
    ]
    if subs < 1_000_000:
        lines.append(f"🎯 Objectif 1 million : {subs / 10_000:.2f} %")

    latest = youtube.latest_videos_stats()
    if latest:
        lines.append("\nDernières vidéos :")
        for v in latest:
            lines.append(f"• {v['title'][:50]} : {_fmt(v['views'])} vues, {v['likes']} likes, {v['comments']} comm.")

    notify("\n".join(lines))
