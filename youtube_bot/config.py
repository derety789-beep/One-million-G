"""Chargement de la configuration depuis les variables d'environnement (.env)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "oui"}


def _list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Config:
    # Google / YouTube
    google_client_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID", ""))
    google_client_secret: str = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET", ""))
    google_refresh_token: str = field(default_factory=lambda: os.getenv("GOOGLE_REFRESH_TOKEN", ""))

    # Claude
    claude_model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-opus-5-5"))
    channel_description: str = field(
        default_factory=lambda: os.getenv("CHANNEL_DESCRIPTION", "Une chaîne YouTube francophone.")
    )
    language: str = field(default_factory=lambda: os.getenv("LANGUAGE", "français"))

    # Telegram (optionnel)
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # Planification
    timezone: str = field(default_factory=lambda: os.getenv("TIMEZONE", "Europe/Paris"))
    publish_times: list[str] = field(default_factory=lambda: _list("PUBLISH_TIMES", "18:00"))
    default_privacy: str = field(default_factory=lambda: os.getenv("DEFAULT_PRIVACY", "public"))
    comment_check_minutes: int = field(
        default_factory=lambda: int(os.getenv("COMMENT_CHECK_MINUTES", "30"))
    )
    max_replies_per_run: int = field(default_factory=lambda: int(os.getenv("MAX_REPLIES_PER_RUN", "10")))
    stats_time: str = field(default_factory=lambda: os.getenv("STATS_TIME", "09:00"))

    # Modules activés
    enable_upload: bool = field(default_factory=lambda: _bool("ENABLE_UPLOAD", True))
    enable_comments: bool = field(default_factory=lambda: _bool("ENABLE_COMMENTS", True))
    enable_stats: bool = field(default_factory=lambda: _bool("ENABLE_STATS", True))

    # Mode test : rien n'est publié, tout est seulement affiché dans les logs
    dry_run: bool = field(default_factory=lambda: _bool("DRY_RUN", False))

    # Dossiers
    queue_dir: Path = field(default_factory=lambda: Path(os.getenv("QUEUE_DIR", "queue")))
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", "data")))

    def check(self) -> None:
        missing = [
            name
            for name, value in {
                "GOOGLE_CLIENT_ID": self.google_client_id,
                "GOOGLE_CLIENT_SECRET": self.google_client_secret,
                "GOOGLE_REFRESH_TOKEN": self.google_refresh_token,
            }.items()
            if not value
        ]
        if missing:
            raise SystemExit(f"Variables manquantes dans le .env : {', '.join(missing)}")


config = Config()
