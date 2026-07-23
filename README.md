# YTMusic — Prototype (Windows + Sideloadly)

Lecteur audio basé sur YouTube, sans pub, avec lecture en arrière-plan (écran éteint).

⚠️ **Usage personnel uniquement.** Ce projet contourne les conditions d'utilisation de
YouTube (extraction de flux + suppression des pubs). Pas de publication App Store —
uniquement pour du sideload perso avec un Apple ID gratuit ou payant.

## Vue d'ensemble

Comme tu es sous Windows, tu ne peux pas compiler du Swift toi-même (Xcode = Mac only).
Solution : **GitHub Actions** compile l'app pour toi sur un Mac dans le cloud (gratuit
pour un repo public), et te génère un fichier `.ipa`. Tu télécharges ce fichier et tu
l'installes sur ton iPhone avec **Sideloadly**, qui gère la signature avec ton Apple ID.

```
Toi (Windows) → push le code sur GitHub → GitHub Actions (Mac cloud) compile
→ télécharge le .ipa → Sideloadly → installé sur ton iPhone
```

## Étape 1 — Lancer le backend

Le backend doit tourner sur une machine accessible depuis ton iPhone (ton PC Windows,
en local sur le même wifi, suffit pour tester).

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Récupère l'IP locale de ton PC (`ipconfig` → IPv4), ex: `192.168.1.42`.

Dans `ios/Sources/ContentView.swift`, remplace :
```swift
let BACKEND_URL = "http://192.168.1.XX:8000"
```
par ta vraie IP.

## Étape 2 — Mettre le projet sur GitHub

```bash
git init
git add .
git commit -m "init"
gh repo create ytmusic --public --source=. --push
# ou crée le repo sur github.com et fais un git push classique
```

⚠️ Repo **public** = minutes macOS gratuites illimitées sur GitHub Actions.
En privé, tu as un quota limité (les runners macOS coûtent 10x plus de minutes).

## Étape 3 — Lancer le build

Sur GitHub → ton repo → onglet **Actions** → workflow **Build IPA** →
**Run workflow**. Ça prend 2-5 minutes.

Une fois terminé, clique sur le run → section **Artifacts** en bas → télécharge
**YTMusic-ipa** (c'est un zip contenant `YTMusic.ipa`).

## Étape 4 — Sideloadly

1. Installe [Sideloadly](https://sideloadly.io/) sur ton PC + iTunes (pour les drivers)
2. Branche ton iPhone en USB, fais-lui confiance
3. Ouvre Sideloadly, glisse `YTMusic.ipa` dedans
4. Renseigne ton Apple ID (compte gratuit suffit) → **Start**
5. Sur l'iPhone : **Réglages → Général → VPN et gestion de l'appareil** →
   fais confiance au profil développeur

⚠️ Avec un Apple ID gratuit, l'app expire au bout de **7 jours** — il faudra
la resideloader régulièrement (ou passer à un compte développeur payant, 99$/an,
pour 1 an de validité).

## Étape 5 — Vérifier la lecture en arrière-plan

Lance un morceau, verrouille l'écran → la musique doit continuer et les contrôles
doivent apparaître sur l'écran verrouillé. C'est géré par `UIBackgroundModes: audio`
(déjà configuré dans `project.yml`) + `AVAudioSession` en mode `.playback` dans
`PlayerManager.swift`.

## Structure du projet

```
backend/            → serveur Python (recherche + extraction audio yt-dlp)
ios/
  project.yml        → spec XcodeGen (génère le .xcodeproj automatiquement)
  Info.plist
  Sources/
    YTMusicApp.swift
    ContentView.swift
    PlayerManager.swift
    Track.swift
.github/workflows/build.yml   → build automatique sur macOS cloud
```

## Ce qui manque pour une vraie v2

- Playlist / file d'attente (un seul morceau à la fois pour l'instant)
- Déploiement du backend sur un vrai serveur (Render, Railway, VPS) au lieu de
  ton PC local — sinon l'app ne marche que sur ton wifi
- Renouvellement auto du sideload (ou compte développeur payant)
- Cache local, historique, favoris (SwiftData/CoreData)
