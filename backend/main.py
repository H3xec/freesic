"""
Backend minimal pour l'app iOS.
Deux routes :
  GET /search?q=...        -> liste de résultats (titre, id, durée, thumbnail)
  GET /stream?id=VIDEO_ID   -> URL audio directe + métadonnées

Lancer en local :
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8000

Sur ton téléphone (même réseau wifi que ton Mac), l'app appellera
http://<IP_DE_TON_MAC>:8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI(title="YTMusic Backend")

# Autorise les appels depuis l'app iOS (dev local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import shutil

# Render monte les "Secret Files" en LECTURE SEULE à /etc/secrets/, mais yt-dlp
# a besoin d'écrire dans le fichier de cookies. On copie donc vers /tmp (writable).
RENDER_SECRET_COOKIES = "/etc/secrets/cookies.txt"
COOKIES_PATH = "/tmp/cookies.txt"

if os.path.exists(RENDER_SECRET_COOKIES):
    shutil.copyfile(RENDER_SECRET_COOKIES, COOKIES_PATH)

_cookies_option = {"cookiefile": COOKIES_PATH} if os.path.exists(COOKIES_PATH) else {}

YDL_SEARCH_OPTS = {
    "quiet": True,
    "extract_flat": True,
    "default_search": "ytsearch10",
    "skip_download": True,
    **_cookies_option,
}

YDL_STREAM_OPTS = {
    "quiet": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    "skip_download": True,
    **_cookies_option,
}


@app.get("/search")
def search(q: str):
    if not q.strip():
        raise HTTPException(400, "Paramètre 'q' manquant")

    try:
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch10:{q}", download=False)
    except Exception as e:
        print(f"[DEBUG] Exception yt-dlp: {repr(e)}")
        raise HTTPException(500, f"Erreur yt-dlp: {e}")

    print(f"[DEBUG] Query: {q!r}")
    print(f"[DEBUG] Info keys: {list(info.keys()) if info else 'None'}")
    print(f"[DEBUG] Nb entries bruts: {len(info.get('entries', [])) if info else 0}")
    print(f"[DEBUG] _type: {info.get('_type')}")
    print(f"[DEBUG] url: {info.get('url')}")
    print(f"[DEBUG] extractor: {info.get('extractor')}")
    print(f"[DEBUG] extractor_key: {info.get('extractor_key')}")
    print(f"[DEBUG] webpage_url: {info.get('webpage_url')}")

    results = []
    for entry in info.get("entries", []):
        if not entry:
            continue
        results.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "duration": entry.get("duration"),
            "thumbnail": entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else None,
            "uploader": entry.get("uploader") or entry.get("channel"),
        })
    return {"results": results}


@app.get("/stream")
def stream(id: str):
    url = f"https://www.youtube.com/watch?v={id}"
    try:
        with yt_dlp.YoutubeDL(YDL_STREAM_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        raise HTTPException(500, f"Extraction impossible: {e}")

    audio_url = info.get("url")
    if not audio_url:
        raise HTTPException(404, "Pas de flux audio trouvé")

    return {
        "id": id,
        "title": info.get("title"),
        "duration": info.get("duration"),
        "audio_url": audio_url,
        "thumbnail": info.get("thumbnail"),
    }