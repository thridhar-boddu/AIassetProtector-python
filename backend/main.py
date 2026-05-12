import os
import time
import random
import io
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont

# ─── Load configuration from environment ────────────────────────────────────
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",")]

# ─── App setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AssetGuardian Backend",
    description="Digital Asset Protection Backend (Python FastAPI)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ESPN endpoint map for Indian-first coverage
ESPN_ENDPOINTS = {
    "IPL":           "https://site.api.espn.com/apis/site/v2/sports/cricket/8048/scoreboard",
    "India Cricket": "https://site.api.espn.com/apis/site/v2/sports/cricket/1/scoreboard",
    "ISL":           "https://site.api.espn.com/apis/site/v2/sports/soccer/ind.1/scoreboard",
    "F1":            "https://site.api.espn.com/apis/site/v2/sports/racing/f1/scoreboard",
    "Tennis":        "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard",
    "NBA":           "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "UFC":           "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard",
    "EPL":           "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard"
}

def fetch_from_url(url: str) -> List[str]:
    names = []
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if "events" in data:
            for event in data["events"]:
                names.append(event.get("shortName", ""))
                if len(names) >= 5:
                    break
    except Exception:
        pass
    return [name for name in names if name]

def fetch_live_event_names(topic: str) -> List[str]:
    names = []
    url = ESPN_ENDPOINTS.get(topic)
    if url is None:
        for ep in ESPN_ENDPOINTS.values():
            names.extend(fetch_from_url(ep))
            if len(names) >= 6:
                break
    else:
        names.extend(fetch_from_url(url))
    return names

@app.post("/api/protection/watermark")
async def watermark_asset(file: UploadFile = File(...), text: str = Form(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGBA")
    
    # Create a transparent overlay
    txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt_layer)
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 64)
    except IOError:
        try:
            font = ImageFont.truetype("Arial.ttf", 64)
        except IOError:
            font = ImageFont.load_default()
            
    # Need to handle font size calculation properly for PIL version
    if hasattr(font, "getbbox"):
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        # Fallback for older PIL
        try:
            text_width, text_height = d.textsize(text, font=font)
        except AttributeError:
            text_width, text_height = 100, 20
    
    width, height = image.size
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Semi-transparent white
    d.text((x, y), text, font=font, fill=(255, 255, 255, int(255 * 0.3)))
    
    watermarked = Image.alpha_composite(image, txt_layer)
    watermarked = watermarked.convert("RGB") # Return as RGB/PNG
    
    img_byte_arr = io.BytesIO()
    watermarked.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return Response(content=img_byte_arr, media_type="image/png")

class ScanRequest(BaseModel):
    platform: str = "global"

@app.post("/api/protection/scan")
def start_scan(request: ScanRequest):
    platform = request.platform
    # simulate crawler async scan
    return {
        "status": "Scan Initiated",
        "platform": platform,
        "job_id": f"JOB-{int(time.time() * 1000)}"
    }

@app.get("/api/protection/stats")
def get_stats(topic: str = Query("All")):
    multiplier = 1.0 if topic == "All" else abs(hash(topic) % 100) / 50.0 + 0.5
    return {
        "total_monitored": f"{1.2 * multiplier:.1f}M",
        "high_risk_flags": int(154 * multiplier),
        "auto_takedowns": int(892 * multiplier),
        "ai_precision": f"99.{abs(hash(topic) % 9)}%"
    }

@app.get("/api/protection/detections")
def get_detections(topic: str = Query("All")):
    risks = ["High", "Critical", "Medium", "Low"]
    platforms = ["YouTube", "Telegram", "Instagram", "Twitter / X", "Twitch", "Discord"]
    types = ["Full Stream", "Clips", "Live Feed", "Behind Scenes"]
    
    live_events = fetch_live_event_names(topic)
    detections = []
    
    count = 3 + random.randint(0, 3)
    for _ in range(count):
        risk = random.choice(risks)
        is_danger = risk in ["High", "Critical"]
        event_name = random.choice(live_events) if live_events else topic
        
        detections.append({
            "name": f"{event_name} — {random.choice(types)} #{100 + random.randint(0, 899)}",
            "platform": random.choice(platforms),
            "risk": risk,
            "confidence": f"{85 + random.random() * 14:.1f}%",
            "danger": is_danger,
            "liveEvent": bool(live_events)
        })
    return detections

@app.get("/api/protection/takedowns")
def get_takedowns(topic: str = Query("All")):
    platforms = ["YouTube", "Telegram", "Dailymotion", "Twitter / X", "Twitch", "Facebook"]
    file_types = ["MP4 Stream", "HLS Playlist", "Live Clip", "Full Broadcast", "Highlight Reel"]
    methods = ["DMCA Notice", "Auto-AI Flag", "Platform Report", "Rights API"]
    statuses = ["Confirmed", "Confirmed", "Pending", "Confirmed"]
    
    live_events = fetch_live_event_names(topic)
    takedowns = []
    
    count = 4 + random.randint(0, 4)
    for _ in range(count):
        event_name = random.choice(live_events) if live_events else topic
        platform = random.choice(platforms)
        file_type = random.choice(file_types)
        status = random.choice(statuses)
        views_before = 1000 + random.randint(0, 998999)
        minutes_ago = random.randint(0, 89)
        
        takedowns.append({
            "title": f"{event_name} — Unauthorized {file_type}",
            "platform": platform,
            "fileType": file_type,
            "status": status,
            "views": f"{views_before:,}",
            "confidence": f"{88 + random.random() * 11:.1f}%",
            "method": random.choice(methods),
            "url": f"{platform.lower().replace(' / ', '')}.com/watch?v={hex(random.getrandbits(32))[2:]}",
            "takenAt": "Just now" if minutes_ago == 0 else f"{minutes_ago}m ago",
            "eventSource": event_name if live_events else ""
        })
        
    takedowns.sort(key=lambda x: int(x["takenAt"].replace("m ago", "").replace("Just now", "0")))
    return takedowns

@app.get("/api/protection/trending")
def get_trending():
    return [
        {"subject": "IPL Final Stream", "status": "Critical", "interest": "🔥 Trending"},
        {"subject": "F1 Monaco GP Cam", "status": "High Risk", "interest": "High"},
        {"subject": "Wimbledon Qualifiers", "status": "Monitoring", "interest": "Rising"},
        {"subject": "BWF Finals Hack", "status": "Flagged", "interest": "Medium"}
    ]

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
