"""Construit automatiquement un serveur Discord (rôles, catégories, salons, messages).

Usage :
    DISCORD_BOT_TOKEN=xxx python discord_setup/setup_server.py

Le bot doit déjà être invité sur le serveur (avec la permission Administrateur).
Le script peut être relancé sans risque : ce qui existe déjà n'est pas recréé.
"""

import json
import os
import sys
import time
from pathlib import Path

import requests

API = "https://discord.com/api/v10"
CONFIG_FILE = Path(__file__).with_name("server.json")

PERMISSIONS = {
    "KICK_MEMBERS": 1 << 1,
    "BAN_MEMBERS": 1 << 2,
    "ADMINISTRATOR": 1 << 3,
    "ADD_REACTIONS": 1 << 6,
    "VIEW_CHANNEL": 1 << 10,
    "SEND_MESSAGES": 1 << 11,
    "MANAGE_MESSAGES": 1 << 13,
    "READ_MESSAGE_HISTORY": 1 << 16,
    "CONNECT": 1 << 20,
    "SPEAK": 1 << 21,
    "MUTE_MEMBERS": 1 << 22,
    "MANAGE_NICKNAMES": 1 << 27,
    "MODERATE_MEMBERS": 1 << 40,
}
CHANNEL_TYPES = {"text": 0, "voice": 2, "category": 4}
STAFF_ROLE = "🛡️ Modérateur"


class Discord:
    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bot {token}",
            "User-Agent": "DiscordBot (https://github.com/derety789-beep/one-million-g, 1.0)",
        })

    def call(self, method: str, path: str, body: dict | None = None):
        while True:
            resp = self.session.request(method, API + path, json=body, timeout=30)
            if resp.status_code == 429:  # limite de vitesse : on attend
                time.sleep(float(resp.json().get("retry_after", 1)) + 0.2)
                continue
            if resp.status_code == 401:
                sys.exit("❌ Token du bot invalide. Vérifie DISCORD_BOT_TOKEN.")
            if resp.status_code == 403:
                sys.exit("❌ Le bot n'a pas les droits. Réinvite-le avec la permission Administrateur.")
            resp.raise_for_status()
            return resp.json() if resp.content else None


def _bits(names: list[str]) -> str:
    return str(sum(PERMISSIONS[n] for n in names))


def _overwrites(mode: str | None, everyone_id: str, staff_id: str | None) -> list[dict]:
    everyone_deny = {"read_only": ["SEND_MESSAGES"], "staff_only": ["VIEW_CHANNEL"]}.get(mode)
    if not everyone_deny:
        return []
    rules = [{"id": everyone_id, "type": 0, "allow": "0", "deny": _bits(everyone_deny)}]
    if staff_id:
        rules.append({"id": staff_id, "type": 0, "allow": _bits(["VIEW_CHANNEL", "SEND_MESSAGES"]), "deny": "0"})
    return rules


def pick_guild(api: Discord) -> dict:
    guilds = api.call("GET", "/users/@me/guilds")
    if not guilds:
        sys.exit("❌ Le bot n'est sur aucun serveur. Invite-le d'abord avec le lien du README.")
    wanted = os.getenv("DISCORD_GUILD_ID")
    if wanted:
        for g in guilds:
            if g["id"] == wanted:
                return g
        sys.exit(f"❌ Le bot n'est pas sur le serveur {wanted}.")
    if len(guilds) > 1:
        names = ", ".join(f"{g['name']} ({g['id']})" for g in guilds)
        sys.exit(f"❌ Le bot est sur plusieurs serveurs : {names}. Indique DISCORD_GUILD_ID.")
    return guilds[0]


def _hex_color(value: str) -> int:
    return int(value.lstrip("#"), 16)


def setup(api: Discord, guild_id: str, conf: dict) -> None:
    roles = {r["name"]: r for r in api.call("GET", f"/guilds/{guild_id}/roles")}
    everyone_id = guild_id  # le rôle @everyone a le même identifiant que le serveur

    for role in conf["roles"]:
        if role["name"] in roles:
            print(f"= Rôle déjà présent : {role['name']}")
            continue
        roles[role["name"]] = api.call("POST", f"/guilds/{guild_id}/roles", {
            "name": role["name"],
            "color": _hex_color(role.get("color", "#000000")),
            "hoist": role.get("hoist", False),
            "mentionable": False,
            "permissions": _bits(role.get("permissions", [])),
        })
        print(f"+ Rôle créé : {role['name']}")

    staff_id = roles.get(STAFF_ROLE, {}).get("id")
    existing = api.call("GET", f"/guilds/{guild_id}/channels")

    def find(name: str, ctype: int, parent_id: str | None = None):
        for c in existing:
            if c["name"] == name and c["type"] == ctype and (parent_id is None or c.get("parent_id") == parent_id):
                return c
        return None

    def create(body: dict) -> dict:
        channel = api.call("POST", f"/guilds/{guild_id}/channels", body)
        existing.append(channel)
        return channel

    system_channel_id = None
    for cat in conf["categories"]:
        category = find(cat["name"], CHANNEL_TYPES["category"])
        if category:
            print(f"= Catégorie déjà présente : {cat['name']}")
        else:
            category = create({
                "name": cat["name"],
                "type": CHANNEL_TYPES["category"],
                "permission_overwrites": _overwrites(cat.get("mode"), everyone_id, staff_id),
            })
            print(f"+ Catégorie créée : {cat['name']}")

        for ch in cat["channels"]:
            ctype = CHANNEL_TYPES[ch.get("type", "text")]
            channel = find(ch["name"], ctype, category["id"])
            if channel:
                print(f"  = Salon déjà présent : {ch['name']}")
            else:
                body = {
                    "name": ch["name"],
                    "type": ctype,
                    "parent_id": category["id"],
                    "permission_overwrites": _overwrites(ch.get("mode"), everyone_id, staff_id),
                }
                if ch.get("topic") and ctype == CHANNEL_TYPES["text"]:
                    body["topic"] = ch["topic"]
                channel = create(body)
                print(f"  + Salon créé : {ch['name']}")
                if ch.get("message"):
                    api.call("POST", f"/channels/{channel['id']}/messages",
                             {"content": conf["messages"][ch["message"]]})
            if ch.get("system_channel"):
                system_channel_id = channel["id"]

    if system_channel_id:
        # Les messages « X a rejoint le serveur » de Discord arriveront dans ce salon
        api.call("PATCH", f"/guilds/{guild_id}", {"system_channel_id": system_channel_id})


def main() -> None:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        sys.exit("❌ Il manque DISCORD_BOT_TOKEN.")
    api = Discord(token)
    guild = pick_guild(api)
    print(f"🔧 Configuration du serveur « {guild['name']} »…")
    setup(api, guild["id"], json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    print("✅ Serveur prêt ! Ouvre Discord pour voir le résultat.")


if __name__ == "__main__":
    main()
