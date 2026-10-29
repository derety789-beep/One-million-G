# One-million-G : bot YouTube automatique 🤖

Un bot qui tourne 24h/24 sur un serveur et gère ta chaîne YouTube :

| Fonction | Ce qu'il fait |
|---|---|
| 📤 **Publication programmée** | Tu déposes tes vidéos dans `queue/` et il en publie une à chaque heure prévue (ex. 18h). |
| ✍️ **Contenu IA** | Si tu n'as pas écrit de titre ni de description, Claude les rédige (avec les tags et les hashtags). |
| 💬 **Réponses aux commentaires** | Toutes les 30 min, il répond aux nouveaux commentaires et ignore le spam et les insultes. |
| 📊 **Rapport des stats** | Chaque matin : abonnés, vues, évolution depuis la veille et progression vers 1 million, envoyés sur Telegram. |

> 🎮 **Tu veux aussi un serveur Discord ?** Suis le guide [discord_setup/README.md](discord_setup/README.md) : un bot crée tous les salons et les rôles pour toi, gratuitement.

---

## 1. Préparer les accès (une seule fois)

### a) API YouTube (Google Cloud)
1. Va sur <https://console.cloud.google.com/> et crée un projet.
2. Dans **API et services → Bibliothèque**, active **YouTube Data API v3**.
3. Dans **Écran de consentement OAuth**, choisis « Externe » et ajoute ton adresse Gmail dans **Utilisateurs test**.
4. Dans **Identifiants → Créer des identifiants → ID client OAuth**, choisis le type **Application de bureau**, puis télécharge le fichier JSON (`client_secret.json`).
5. Sur **ton ordinateur**, lance :
   ```bash
   pip install google-auth-oauthlib
   python scripts/get_refresh_token.py client_secret.json
   ```
   Connecte-toi avec le compte de ta chaîne. Le script affiche 3 lignes à copier dans le `.env`.

> ⚠️ **Important :** tant que ton projet Google n'a pas passé l'[audit YouTube](https://support.google.com/youtube/contact/yt_api_form), les vidéos envoyées par l'API restent **privées**. Demande l'audit (c'est gratuit) pour qu'elles soient publiées en public automatiquement. En attendant, tu peux les passer en public à la main dans YouTube Studio.

### b) Clé Claude (l'IA)
Crée une clé sur <https://console.anthropic.com/> et mets-la dans `ANTHROPIC_API_KEY`.

### c) Telegram (optionnel, pour recevoir les rapports)
1. Sur Telegram, écris à **@BotFather**, tape `/newbot` et récupère le **token**.
2. Envoie un message à ton nouveau bot, puis ouvre `https://api.telegram.org/bot<TOKEN>/getUpdates` : le nombre après `"chat":{"id":` est ton `TELEGRAM_CHAT_ID`.

---

## 2. Configurer

```bash
cp .env.example .env
```
Remplis le fichier `.env`. Les réglages importants sont :
- `CHANNEL_DESCRIPTION` : décris ta chaîne, l'IA s'en sert pour écrire comme toi.
- `PUBLISH_TIMES=12:00,18:00` : une vidéo publiée à chacune de ces heures.
- `DRY_RUN=true` : **mode test**, le bot affiche ce qu'il ferait sans rien publier. Passe-le à `false` quand tout est bon.

---

## 3. Ajouter des vidéos

Dépose les fichiers dans le dossier `queue/`. Elles sont publiées par **ordre alphabétique**, alors numérote-les : `001_intro.mp4`, `002_astuce.mp4`…

Pour chaque vidéo, tu peux ajouter (facultatif) :
- `001_intro.json` : tes notes, ou ton propre titre et ta description (voir `queue/exemple.json`)
- `001_intro.jpg` : la miniature (pour l'utiliser, ta chaîne doit être vérifiée sur YouTube)

Une fois publiée, la vidéo est déplacée dans `queue/done/`.

---

## 4. Lancer sur un serveur 24h/24

Il te faut un petit serveur Linux (VPS) : Hetzner, OVH, DigitalOcean… environ 4 à 6 € par mois.

```bash
git clone https://github.com/derety789-beep/one-million-g.git
cd one-million-g
cp .env.example .env && nano .env        # remplis tes clés
docker compose up -d --build             # démarre le bot (redémarre tout seul)
docker compose logs -f                   # voir ce qu'il fait
```

Pour envoyer des vidéos sur le serveur depuis ton PC :
```bash
scp ma_video.mp4 utilisateur@ip-du-serveur:one-million-g/queue/
```

### Lancer une action tout de suite (pour tester)
```bash
docker compose run --rm youtube-bot python -m youtube_bot.main publish
docker compose run --rm youtube-bot python -m youtube_bot.main comments
docker compose run --rm youtube-bot python -m youtube_bot.main stats
```

### Sans Docker
```bash
pip install -r requirements.txt
python -m youtube_bot.main
```

---

## Bon à savoir

- **Quota YouTube** : 10 000 unités par jour, gratuit. Un envoi de vidéo coûte environ 1 600 unités et une réponse à un commentaire 50 unités. Avec les réglages par défaut, tu restes largement dans la limite.
- **Coût de l'IA** : quelques centimes par jour pour une petite chaîne. Pour réduire le coût, mets `CLAUDE_MODEL=claude-sonnet-5-5` ou `claude-haiku-5-5`.
- Si Claude refuse une demande, une solution de secours prend le relais automatiquement.
- Le bot ne répond jamais deux fois au même commentaire, il le mémorise dans `data/bot.db`.
