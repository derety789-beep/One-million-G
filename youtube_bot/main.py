"""Point d'entrée : lance le planificateur qui tourne 24h/24.

Usage :
    python -m youtube_bot.main            # lance le bot en continu
    python -m youtube_bot.main publish    # publie la prochaine vidéo tout de suite
    python -m youtube_bot.main comments   # traite les commentaires tout de suite
    python -m youtube_bot.main stats      # envoie le rapport tout de suite
"""

import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from . import comments, stats, uploader
from .config import config
from .notifier import notify

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s : %(message)s")
log = logging.getLogger("youtube_bot")

JOBS = {
    "publish": uploader.publish_next,
    "comments": comments.reply_to_new_comments,
    "stats": stats.daily_report,
}


def safe(job):
    """Empêche une erreur ponctuelle d'arrêter le bot."""

    def wrapper():
        try:
            job()
        except Exception as exc:  # noqa: BLE001
            log.exception("Erreur dans %s", job.__name__)
            notify(f"⚠️ Erreur dans {job.__name__} : {exc}")

    wrapper.__name__ = job.__name__
    return wrapper


def _hour_minute(value: str) -> tuple[int, int]:
    hour, minute = value.split(":")
    return int(hour), int(minute)


def run_forever() -> None:
    scheduler = BlockingScheduler(timezone=config.timezone)

    if config.enable_upload:
        for t in config.publish_times:
            h, m = _hour_minute(t)
            scheduler.add_job(safe(uploader.publish_next), CronTrigger(hour=h, minute=m, timezone=config.timezone))
        log.info("Publication programmée à : %s", ", ".join(config.publish_times))

    if config.enable_comments:
        scheduler.add_job(safe(comments.reply_to_new_comments), "interval", minutes=config.comment_check_minutes)
        log.info("Commentaires vérifiés toutes les %d minutes", config.comment_check_minutes)

    if config.enable_stats:
        h, m = _hour_minute(config.stats_time)
        scheduler.add_job(safe(stats.daily_report), CronTrigger(hour=h, minute=m, timezone=config.timezone))
        log.info("Rapport des stats chaque jour à %s", config.stats_time)

    if config.dry_run:
        log.warning("MODE TEST ACTIVÉ : rien ne sera publié sur YouTube.")

    notify("🤖 Bot YouTube démarré.")
    scheduler.start()


def main() -> None:
    config.check()
    config.queue_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name not in JOBS:
            raise SystemExit(f"Commande inconnue : {name}. Choix : {', '.join(JOBS)}")
        JOBS[name]()
        return

    run_forever()


if __name__ == "__main__":
    main()
