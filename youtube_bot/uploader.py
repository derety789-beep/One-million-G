"""Publication programmée : publie la prochaine vidéo de la file d'attente."""

import json
import logging
import shutil
from pathlib import Path

from . import ai, storage, youtube
from .config import config
from .notifier import notify

log = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
THUMBNAIL_EXTENSIONS = (".jpg", ".jpeg", ".png")


def next_video() -> Path | None:
    """Renvoie la prochaine vidéo à publier (ordre alphabétique du nom de fichier)."""
    videos = sorted(
        p for p in config.queue_dir.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    )
    return videos[0] if videos else None


def _load_metadata(video: Path) -> dict:
    meta_file = video.with_suffix(".json")
    meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}

    if not meta.get("title") or not meta.get("description"):
        log.info("Génération du titre et de la description par l'IA pour %s", video.name)
        generated = ai.generate_metadata(video.name, meta.get("notes", ""))
        for key in ("title", "description", "tags"):
            meta.setdefault(key, generated[key])
            if not meta[key]:
                meta[key] = generated[key]
    return meta


def _thumbnail_for(video: Path) -> Path | None:
    for ext in THUMBNAIL_EXTENSIONS:
        candidate = video.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def _archive(video: Path) -> None:
    done = config.queue_dir / "done"
    done.mkdir(exist_ok=True)
    for related in [video, video.with_suffix(".json"), *[video.with_suffix(e) for e in THUMBNAIL_EXTENSIONS]]:
        if related.exists():
            shutil.move(str(related), done / related.name)


def publish_next() -> None:
    video = next_video()
    if video is None:
        log.info("File d'attente vide, rien à publier.")
        notify("📭 Aucune vidéo dans la file d'attente : pense à en ajouter !")
        return

    meta = _load_metadata(video)
    privacy = meta.get("privacy", config.default_privacy)

    if config.dry_run:
        log.info("[TEST] Publierait %s : %s", video.name, json.dumps(meta, ensure_ascii=False, indent=2))
        return

    video_id = youtube.upload_video(
        video,
        title=meta["title"],
        description=meta["description"],
        tags=meta.get("tags", []),
        privacy=privacy,
        category_id=str(meta.get("category_id", "22")),
        thumbnail=_thumbnail_for(video),
    )
    storage.save_upload(video_id, video.name, meta["title"])
    _archive(video)
    notify(f"✅ Vidéo publiée : {meta['title']}\nhttps://youtu.be/{video_id}")
