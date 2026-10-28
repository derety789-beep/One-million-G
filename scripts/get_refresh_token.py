"""À lancer UNE SEULE FOIS sur ton ordinateur (pas sur le serveur) pour autoriser le bot.

    pip install google-auth-oauthlib
    python scripts/get_refresh_token.py chemin/vers/client_secret.json

Une page Google s'ouvre : connecte-toi avec le compte de ta chaîne YouTube et accepte.
Le script affiche ensuite les 3 valeurs à copier dans ton fichier .env.
"""

import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def main() -> None:
    secret_file = sys.argv[1] if len(sys.argv) > 1 else "client_secret.json"
    flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    with open(secret_file, encoding="utf-8") as f:
        info = json.load(f)
    info = info.get("installed") or info.get("web")

    print("\n✅ Autorisation réussie ! Copie ces lignes dans ton fichier .env :\n")
    print(f"GOOGLE_CLIENT_ID={info['client_id']}")
    print(f"GOOGLE_CLIENT_SECRET={info['client_secret']}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
