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

app = FastAPI(title="YTMusic Backend")

# Autorise les appels depuis l'app iOS (dev local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

YDL_SEARCH_OPTS = {
    "quiet": True,
    "extract_flat": True,
    "default_search": "ytsearch10",
    "skip_download": True,
}

YDL_STREAM_OPTS = {
    "quiet": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    "skip_download": True,
}


@app.get("/search")
def search(q: str):
    if not q.strip():
        raise HTTPException(400, "Paramètre 'q' manquant")

    with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
        info = ydl.extract_info(q, download=False)

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
