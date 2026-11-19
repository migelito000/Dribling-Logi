"""Salas privadas para dos jugadores. El anfitrión simula la partida."""
import json
import os
import secrets
from pathlib import Path

from aiohttp import WSMsgType, web

ROOT = Path(__file__).resolve().parent
SKINS = {"soccer": 24, "hoops": 3}
COSMETICS = ("finish", "decal", "wheels", "topper", "antenna", "trail", "boost", "goal")
CAR_FIELDS = ("x", "y", "vx", "vy", "a", "w", "face", "fs", "sf", "roll", "jumps", "dodge", "br")
BALL_FIELDS = ("x", "y", "vx", "vy", "rot", "r")
rooms = {}


def valid_numbers(obj, fields):
    return isinstance(obj, dict) and all(
        type(obj.get(k)) in (int, float) and -1e10 < obj[k] < 1e10 for k in fields
    )


def valid_frame(state):
    if not valid_numbers(state, ("remaining", "pause")):
        return False
    cars, scores = state.get("cars"), state.get("scores")
    return (
        isinstance(cars, list) and len(cars) == 2
        and all(valid_numbers(c, CAR_FIELDS)
                and set(c) <= set(CAR_FIELDS) | {"boosting", "rolling"}
                and all(type(c.get(k, False)) is bool for k in ("boosting", "rolling"))
                and c["sf"] in range(5) for c in cars)
        and valid_numbers(state.get("ball"), BALL_FIELDS)
        and set(state["ball"]) == set(BALL_FIELDS) and state["ball"]["r"] > 0
        and isinstance(scores, list) and len(scores) == 2
        and all(type(v) is int and 0 <= v < 10000 for v in scores)
        and isinstance(state.get("banner"), str) and len(state["banner"]) <= 100
        and state.get("winner") in (None, 0, 1)
    )


def valid_outfit(model):
    if not isinstance(model, dict):
        return {}
    return {k: v for k, v in model.items() if k in COSMETICS and isinstance(v, str)
            and v in {f"{k}_{i}" for i in range(6)}}


async def home(request):
    return web.FileResponse(ROOT / "index.html")


async def broadcast(room, message):
    for peer in tuple(room["peers"]):
        if not peer.closed:
            await peer.send_json(message)


async def send_room(room):
    await broadcast(room, {"t": "room", "players": room["models"], "ready": room["ready"],
                           "joined": len(room["peers"]), "mode": room["mode"],
                           "skin": room["skin"], "outfits": room["outfits"]})


async def socket(request):
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=16384)
    await ws.prepare(request)
    code = request.query.get("room")
    if code is None:
        if len(rooms) >= 250:
            await ws.close(code=1013, message=b"Servidor ocupado")
            return ws
        code = secrets.token_urlsafe(12)
        rooms[code] = dict(peers=[], models=[0, 0], ready=[False, False], outfits=[{}, {}],
                           mode="soccer", skin=0, phase="lobby")
    room = rooms.get(code)
    if room is None or len(room["peers"]) >= 2:
        await ws.close(code=1008, message=b"Sala cerrada o completa")
        return ws
    side = len(room["peers"])
    room["peers"].append(ws)
    try:
        await ws.send_json(dict(t="seat", side=side, room=code))
        await send_room(room)
        async for message in ws:
            if message.type != WSMsgType.TEXT:
                break
            try:
                m = json.loads(message.data)
            except (ValueError, RecursionError):
                break
            if not isinstance(m, dict):
                break
            kind = m.get("t")
            if room["phase"] == "lobby":
                if kind == "pick" and type(m.get("model")) is int and 0 <= m["model"] < 10:
                    room["models"][side] = m["model"]
                    room["outfits"][side] = valid_outfit(m.get("outfit"))
                    room["ready"][side] = False
                elif side == 0 and kind == "rules" and m.get("mode") in ("soccer", "hoops") and type(m.get("skin")) is int and 0 <= m["skin"] < SKINS[m["mode"]]:
                    room.update(mode=m["mode"], skin=m["skin"], ready=[False, False])
                elif kind == "ready" and len(room["peers"]) == 2:
                    room["ready"][side] = not room["ready"][side]
                else:
                    continue
                start = all(room["ready"])
                if start:
                    room["phase"] = "play"
                await send_room(room)
                if start:
                    await broadcast(room, {"t": "start"})
            elif room["phase"] == "play":
                if side == 1 and kind == "input" and type(m.get("mask")) is int and 0 <= m["mask"] < 16 and m.get("edge") in ("", "jump", "roll"):
                    await room["peers"][0].send_json(dict(t="input", mask=m["mask"], edge=m["edge"]))
                if side == 0 and kind == "frame" and valid_frame(m.get("state")):
                    end = m.get("end") is True
                    if end:
                        room["phase"] = "ended"
                    await room["peers"][1].send_json(dict(t="frame", end=end, state=m["state"]))
            elif kind == "again":
                room["phase"] = "lobby"
                room["ready"] = [False, False]
                await send_room(room)
    except ConnectionError:
        pass
    finally:
        if rooms.pop(code, None) is not None:
            for peer in room["peers"]:
                if peer is not ws and not peer.closed:
                    await peer.close(code=1001, message=b"El otro jugador salio de la sala")
        await ws.close()
    return ws


app = web.Application()
app.router.add_get("/", home)
app.router.add_get("/rooms", socket)
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
