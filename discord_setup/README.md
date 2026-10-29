# 🎮 Créer ton serveur Discord automatiquement

Gratuit, sans carte bancaire, faisable depuis ton téléphone. Compte environ 10 minutes.

**Ce que le bot crée :**
- **5 rôles :** 👑 Fondateur, 🛡️ Modérateur, 💎 VIP, 🎬 Abonné YouTube, 👥 Membre
- **📌 INFOS :** bienvenue, règles, annonces, nouvelles vidéos (seuls les modos peuvent y écrire)
- **💬 COMMUNAUTÉ :** discussion, idées de vidéos, médias, memes
- **💰 OBJECTIF 1 MILLION :** business et argent, réussites, objectifs
- **🔊 VOCAL :** Discussion, Gaming, Musique
- **🛡️ STAFF :** salons privés, visibles seulement par les modos
- Un **message de bienvenue** et les **règles**, déjà écrits

---

## Étape 1 : Créer le serveur vide
Dans Discord, appuie sur **➕** (à gauche), puis **Créer le mien** et **Pour moi et mes amis**. Donne-lui un nom et valide.

## Étape 2 : Créer le bot
1. Va sur <https://discord.com/developers/applications> et connecte-toi.
2. Clique sur **New Application**, donne-lui un nom (ex. `One-million-G Bot`), coche la case, puis **Create**.
3. À gauche, va dans **Bot** et clique sur **Reset Token**, puis **Copy**.
   👉 **Garde ce token secret**, c'est le mot de passe de ton bot. Ne l'envoie à personne.

## Étape 3 : Inviter le bot sur ton serveur
1. Toujours sur la page du bot, à gauche : **General Information**, puis copie l'**Application ID**.
2. Ouvre ce lien en remplaçant `TON_ID` par l'Application ID :
   ```
   https://discord.com/oauth2/authorize?client_id=TON_ID&scope=bot&permissions=8
   ```
3. Choisis ton serveur, puis **Continuer** et **Autoriser**.

## Étape 4 : Donner le token à GitHub
1. Sur GitHub, ouvre ton dépôt **one-million-g**.
2. Va dans **Settings**, puis **Secrets and variables**, puis **Actions**, et clique sur **New repository secret**.
3. Dans **Name**, écris `DISCORD_BOT_TOKEN`. Dans **Secret**, colle le token de l'étape 2. Clique sur **Add secret**.

## Étape 5 : Lancer la création 🚀
1. Dans ton dépôt, va dans l'onglet **Actions**.
2. Clique sur **Créer mon serveur Discord** dans la liste de gauche.
3. Clique sur **Run workflow**, puis sur le bouton vert **Run workflow**.
4. Attends environ 1 minute que la pastille devienne verte ✅. Ton serveur est prêt !

## Étape 6 : Te donner le rôle Fondateur
Dans Discord, appuie sur ton pseudo dans la liste des membres, puis **Rôles** et **👑 Fondateur**.

---

### Modifier les salons ou les règles
Tout se trouve dans `discord_setup/server.json` : noms des salons, rôles et textes. Modifie-le, puis relance l'étape 5. Ce qui existe déjà n'est pas recréé, seuls les nouveaux éléments sont ajoutés.

### Ça ne marche pas ?
- Si la pastille est rouge ❌, clique dessus pour voir l'erreur (en français).
- **« Token invalide »** : refais l'étape 2, puis mets à jour le secret de l'étape 4.
- **« N'a pas les droits »** : refais l'étape 3, avec bien `permissions=8` dans le lien.
