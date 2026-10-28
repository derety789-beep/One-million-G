"""Réponses automatiques aux nouveaux commentaires."""

import logging

from . import ai, storage, youtube
from .config import config

log = logging.getLogger(__name__)


def reply_to_new_comments() -> None:
    channel_id = youtube.my_channel()["id"]
    titles: dict[str, str] = {}
    replied = 0

    for thread in youtube.recent_comment_threads():
        if replied >= config.max_replies_per_run:
            break

        thread_id = thread["id"]
        top = thread["snippet"]["topLevelComment"]["snippet"]

        if storage.was_replied(thread_id):
            continue
        # Ne pas se répondre à soi-même, ni répondre deux fois au même fil
        if top.get("authorChannelId", {}).get("value") == channel_id:
            storage.mark_replied(thread_id, None)
            continue
        replies = thread.get("replies", {}).get("comments", [])
        if any(r["snippet"].get("authorChannelId", {}).get("value") == channel_id for r in replies):
            storage.mark_replied(thread_id, None)
            continue

        video_id = thread["snippet"].get("videoId", "")
        if video_id not in titles:
            titles[video_id] = youtube.video_title(video_id) if video_id else ""

        reply = ai.generate_reply(titles[video_id], top["authorDisplayName"], top["textDisplay"])
        if reply is None:
            log.info("Commentaire ignoré (%s) : %s", top["authorDisplayName"], top["textDisplay"][:80])
            storage.mark_replied(thread_id, None)
            continue

        if config.dry_run:
            log.info("[TEST] Répondrait à %s : %s", top["authorDisplayName"], reply)
            continue

        youtube.reply_to_comment(thread_id, reply)
        storage.mark_replied(thread_id, reply)
        replied += 1
        log.info("Réponse à %s : %s", top["authorDisplayName"], reply)

    log.info("%d réponse(s) publiée(s).", replied)
