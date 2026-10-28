"""Envoi de notifications sur Telegram (optionnel)."""

import logging

import requests

from .config import config

log = logging.getLogger(__name__)


def notify(message: str) -> None:
    log.info("Notification :\n%s", message)
    if not (config.telegram_bot_token and config.telegram_chat_id):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage",
            json={"chat_id": config.telegram_chat_id, "text": message},
            timeout=15,
        ).raise_for_status()
    except requests.RequestException as exc:
        log.error("Échec de l'envoi Telegram : %s", exc)
