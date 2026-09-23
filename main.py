"""
KATCHO - Real-Time Multiplayer Social Deduction & Memory Game
Main Server: FastAPI, WebSockets, Static File Serving, Dynamic Word Modes (1 vs 2 words)
Branding: Created by KABIR VYAS
"""

import os
import io
import json
import base64
import socket
import logging
from typing import Dict, Set, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import qrcode

from game_manager import GameManager, GamePhase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KATCHO")

app = FastAPI(title="KATCHO - Created by KABIR VYAS")

# Enable CORS for local development and LAN play
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gm = GameManager()
active_connections: Dict[str, Dict[str, WebSocket]] = {}


def get_local_ip() -> str:
    """Detects primary local network IP (e.g., 192.168.x.x or 10.x.x.x) for Hotspot/LAN play."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_all_local_ips() -> List[str]:
    """Retrieves all detected non-loopback IP addresses."""
    ips = set()
    primary = get_local_ip()
    if primary and not primary.startswith("127."):
        ips.add(primary)
    try:
        host_name = socket.gethostname()
        for info in socket.getaddrinfo(host_name, None):
            addr = info[4][0]
            if ":" not in addr and not addr.startswith("127."):
                ips.add(addr)
    except Exception:
        pass
    return list(ips) if ips else [primary]


def generate_qr_base64(url: str) -> str:
    """Generates a Base64-encoded PNG Data URL of a QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E272E", back_color="#FFFFFF", image_factory=qrcode.image.pil.PilImage)
    pil_img = img.get_image()
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


async def broadcast_room_state(room_code: str, custom_event: Optional[dict] = None):
    """Broadcasts individualized, state-synchronized messages to all connected players in a room."""
    room = gm.get_room(room_code)
    if not room or room_code not in active_connections:
        return

    dead_connections = []
    conns = active_connections[room_code]

    for player_id, ws in list(conns.items()):
        try:
            state_data = room.to_state_dict(for_player_id=player_id)
            message = {
                "type": "state_update",
                "state": state_data,
            }
            if custom_event:
                message["event"] = custom_event
            await ws.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send state to {player_id}: {e}")
            dead_connections.append(player_id)

    for p_id in dead_connections:
        conns.pop(p_id, None)
        gm.player_disconnect(room_code, p_id)


STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def get_landing():
    """Serves the KATCHO Home & Pre-Game Lobby landing page."""
    landing_file = os.path.join(STATIC_DIR, "landing.html")
    if os.path.exists(landing_file):
        return FileResponse(landing_file)
    # Fallback to index.html if landing page doesn't exist
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>KATCHO backend is running. Please add static/landing.html</h1>")


@app.get("/play")
async def get_game():
    """Serves the main KATCHO game UI (the original index.html)."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>KATCHO game UI not found. Please add static/index.html</h1>")


@app.get("/manifest.json")
async def get_manifest():
    manifest_file = os.path.join(STATIC_DIR, "manifest.json")
    return FileResponse(manifest_file, media_type="application/manifest+json")


@app.get("/service-worker.js")
async def get_service_worker():
    sw_file = os.path.join(STATIC_DIR, "service-worker.js")
    return FileResponse(sw_file, media_type="application/javascript")


@app.get("/api/lan-info")
async def get_lan_info(port: int = 8000):
    local_ip = get_local_ip()
    all_ips = get_all_local_ips()
    lan_url = f"http://{local_ip}:{port}"
    qr_data = generate_qr_base64(lan_url)

    return JSONResponse({
        "local_ip": local_ip,
        "all_ips": all_ips,
        "port": port,
        "lan_url": lan_url,
        "qr_data_url": qr_data,
        "title": "KATCHO",
        "author": "KABIR VYAS",
    })


@app.get("/api/rooms/{room_code}")
async def get_room_info(room_code: str):
    room = gm.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return JSONResponse({
        "room_code": room.code,
        "phase": room.phase.value,
        "player_count": len(room.players),
    })


@app.websocket("/ws/{room_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, player_id: str):
    await websocket.accept()
    room_code = room_code.strip().upper()

    if room_code not in active_connections:
        active_connections[room_code] = {}

    active_connections[room_code][player_id] = websocket
    logger.info(f"WebSocket connected: Player {player_id} in Room {room_code}")

    try:
        await broadcast_room_state(room_code)

        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
            except json.JSONDecodeError:
                continue

            action = msg.get("action")
            logger.info(f"Action '{action}' from player {player_id} in {room_code}")

            if action == "create_room":
                player_name = msg.get("name", "Host")
                room, player = gm.create_room(player_name, player_id)
                if room.code not in active_connections:
                    active_connections[room.code] = {}
                active_connections[room.code][player_id] = websocket
                await broadcast_room_state(room.code, {"type": "room_created", "room_code": room.code})

            elif action == "join_room":
                target_room = msg.get("room_code", room_code).strip().upper()
                player_name = msg.get("name", "Player")
                room, player, err_msg = gm.join_room(target_room, player_name, player_id)
                if not room:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": err_msg
                    }))
                else:
                    if target_room not in active_connections:
                        active_connections[target_room] = {}
                    active_connections[target_room][player_id] = websocket
                    await broadcast_room_state(target_room)

            elif action == "set_word_mode":
                count = int(msg.get("words_per_player", 1))
                success, reason = gm.set_word_mode(room_code, player_id, count)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "word_mode_changed",
                        "words_per_player": count,
                    })

            elif action == "submit_word":
                # Support single string or array of words
                if "words" in msg and isinstance(msg["words"], list):
                    words_list = msg["words"]
                elif "word" in msg:
                    words_list = [msg["word"]]
                else:
                    words_list = []

                success, reason = gm.submit_secret_words(room_code, player_id, words_list)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code)

            elif action == "start_reveal":
                success, reason, words = gm.start_reveal_phase(room_code, player_id)
                if not success:
                    if reason == "PROMPT_MODE_SELECTION":
                        # Tell host to pick mode before starting
                        await websocket.send_text(json.dumps({
                            "type": "prompt_mode_selection"
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": reason
                        }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "reveal_started",
                        "word_sequence": words,
                    })

            elif action == "finish_reveal":
                room = gm.get_room(room_code)
                if room and room.phase == GamePhase.REVEAL:
                    gm.finish_reveal_phase(room_code)
                    await broadcast_room_state(room_code, {"type": "guessing_started"})

            elif action == "make_accusation":
                target_id = msg.get("target_id")
                guessed_word = msg.get("guessed_word", "")
                success, reason = gm.make_accusation(room_code, player_id, target_id, guessed_word)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "accusation_made",
                        "guesser_id": player_id,
                        "target_id": target_id,
                        "word": guessed_word.strip().upper(),
                    })

            elif action == "respond_accusation":
                response_val = bool(msg.get("response", False))
                success, reason, result_data = gm.respond_accusation(room_code, player_id, response_val)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "accusation_resolved",
                        "result": result_data,
                    })

            elif action == "pass_turn":
                success, reason, next_id = gm.pass_turn(room_code, player_id)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "turn_passed",
                        "next_player_id": next_id,
                    })

            elif action == "call_draw":
                success, reason = gm.call_draw(room_code, player_id)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "draw_vote_started",
                        "initiator_id": player_id,
                    })

            elif action == "vote_draw":
                agree = bool(msg.get("agree", False))
                success, reason, is_unanimous = gm.vote_draw(room_code, player_id, agree)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {
                        "type": "draw_vote_updated",
                        "unanimous": is_unanimous,
                    })

            elif action == "play_again":
                success, reason = gm.play_again_reset(room_code, player_id)
                if not success:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": reason
                    }))
                else:
                    await broadcast_room_state(room_code, {"type": "game_reset"})

            elif action == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: Player {player_id} in Room {room_code}")
        if room_code in active_connections and player_id in active_connections[room_code]:
            active_connections[room_code].pop(player_id, None)
        gm.player_disconnect(room_code, player_id)
        await broadcast_room_state(room_code)

    except Exception as e:
        logger.error(f"WebSocket exception for player {player_id}: {e}", exc_info=True)
        if room_code in active_connections and player_id in active_connections[room_code]:
            active_connections[room_code].pop(player_id, None)
        gm.player_disconnect(room_code, player_id)
        await broadcast_room_state(room_code)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    local_ip = get_local_ip()
    port = 8000
    print("\n" + "=" * 60)
    print("  [GAME] KATCHO - Multiplayer Social Deduction Party Game")
    print("  [AUTHOR] Created by KABIR VYAS")
    print("=" * 60)
    print(f"  -> Local URL:   http://localhost:{port}")
    print(f"  -> LAN / Wi-Fi: http://{local_ip}:{port}")
    print("=" * 60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
