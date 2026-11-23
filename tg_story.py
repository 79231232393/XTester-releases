#!/usr/bin/env python3
"""Publish queued reels as Telegram channel stories (and optional channel posts).

Queue lives in GitHub: branch `tg-stories` of 79231232393/XTester-releases.
  queue.json   -> {"items": [{"id", "video", "caption", "period_hours", "also_post", "post_text"}]}
  videos/*.mp4 -> files referenced by "video"

Commands:
  python tg_story.py login +79990000000            # one time: Telegram sends a login code
  python tg_story.py login +79990000000 1-2-3-4-5  # then sign in with it (+ 2FA password as 4th arg)
  python tg_story.py check   # can this account post stories to the channel?
  python tg_story.py run     # pull queue, publish every item not yet published

Config: config.env next to this script (TG_API_ID, TG_API_HASH, TG_CHANNEL; optional GH_STATUS_TOKEN,
        a fine-grained token for XTester-releases with Contents: read/write only, so Claude sees results).
State:  state.json next to this script (ids already published). Never commit either.
"""
import asyncio, json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.stories import CanSendStoryRequest, SendStoryRequest
from telethon.tl.types import (DocumentAttributeVideo, InputMediaUploadedDocument,
                               InputPrivacyValueAllowAll)

HERE = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/79231232393/XTester-releases/tg-stories/"
STATE = HERE / "state.json"
LOG = HERE / "tg_story.log"
MAX_BYTES = 30 * 1024 * 1024  # keep uploads small; larger files get re-encoded to 720x1280


def load_config():
    cfg = {}
    for line in (HERE / "config.env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"')
    for k in ("TG_API_ID", "TG_API_HASH", "TG_CHANNEL"):
        if not cfg.get(k):
            sys.exit(f"config.env: {k} is missing")
    return cfg


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch(url, dest=None):
    req = urllib.request.Request(url + ("&" if "?" in url else "?") + f"t={int(time.time())}",
                                 headers={"User-Agent": "tg-story"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    if dest:
        Path(dest).write_bytes(data)
    return data


def probe(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=width,height:format=duration",
                              "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
        j = json.loads(out)
        s = j["streams"][0]
        return float(j["format"]["duration"]), int(s["width"]), int(s["height"])
    except Exception:
        return 30.0, 1080, 1920


def shrink(path):
    if path.stat().st_size <= MAX_BYTES:
        return path
    out = path.with_name(path.stem + "-720.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf", "scale=720:1280",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-c:a", "aac",
                    "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    return out


def report(cfg, state, note):
    """Write status.json to branch tg-status so Claude can read publish results."""
    tok = cfg.get("GH_STATUS_TOKEN")
    if not tok:
        return
    import base64
    api = "https://api.github.com/repos/79231232393/XTester-releases/contents/status.json"
    hdr = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": "tg-story"}
    try:
        with urllib.request.urlopen(urllib.request.Request(api + "?ref=tg-status", headers=hdr), timeout=60) as r:
            sha = json.load(r)["sha"]
    except Exception:
        sha = None
    tail = LOG.read_text(encoding="utf-8").splitlines()[-30:] if LOG.exists() else []
    body = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "note": note, "done": state["done"], "log": tail}
    data = {"message": "status", "branch": "tg-status",
            "content": base64.b64encode(json.dumps(body, indent=1, ensure_ascii=False).encode()).decode()}
    if sha:
        data["sha"] = sha
    try:
        urllib.request.urlopen(urllib.request.Request(api, data=json.dumps(data).encode(), headers=hdr, method="PUT"), timeout=60)
    except Exception as e:
        log(f"status report failed: {e}")


async def client_for(cfg):
    c = TelegramClient(str(HERE / "tg_story"), int(cfg["TG_API_ID"]), cfg["TG_API_HASH"])
    await c.connect()
    return c


async def cmd_login(cfg):
    # Non-interactive so an agent can run it. The code may be typed with dashes or spaces:
    # Telegram expires a login code that is sent as-is inside a Telegram chat.
    a = sys.argv[2:]
    if not a:
        sys.exit("usage: login PHONE [CODE] [2FA_PASSWORD]")
    c = await client_for(cfg)
    hash_file = HERE / "login_hash.txt"
    if len(a) == 1:
        sent = await c.send_code_request(a[0])
        hash_file.write_text(sent.phone_code_hash)
        print("Code sent. Run: login PHONE CODE (write the code with dashes, e.g. 1-2-3-4-5)")
    else:
        code = "".join(ch for ch in a[1] if ch.isdigit())
        try:
            await c.sign_in(a[0], code, phone_code_hash=hash_file.read_text().strip())
        except Exception as e:
            if type(e).__name__ != "SessionPasswordNeededError":
                raise
            if len(a) < 3:
                sys.exit("2FA is on: run again with the cloud password as the 4th argument")
            await c.sign_in(password=a[2])
        hash_file.unlink(missing_ok=True)
        me = await c.get_me()
        print(f"Logged in as {me.first_name} (@{me.username})")
    await c.disconnect()


async def cmd_check(cfg):
    c = await client_for(cfg)
    if not await c.is_user_authorized():
        sys.exit("Not logged in: run `python tg_story.py login` first")
    peer = await c.get_input_entity(cfg["TG_CHANNEL"])
    try:
        r = await c(CanSendStoryRequest(peer=peer))
        print("OK: stories can be posted to", cfg["TG_CHANNEL"], r)
    except Exception as e:
        print("NO:", type(e).__name__, e,
              "\n(BOOSTS_REQUIRED = channel needs boost level 1; CHAT_ADMIN_REQUIRED = account lacks 'Post stories' admin right)")
    await c.disconnect()


async def cmd_run(cfg):
    try:
        await _run(cfg)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        log("FAIL queue: " + tb.strip().splitlines()[-1] + " | " + " / ".join(tb.strip().splitlines()[-6:-1]))
        state = json.loads(STATE.read_text()) if STATE.exists() else {"done": {}}
        report(cfg, state, "run crashed:\n" + tb)
        raise


async def _run(cfg):
    queue = json.loads(fetch(RAW + "queue.json"))
    state = json.loads(STATE.read_text()) if STATE.exists() else {"done": {}}
    # schema 1 (see FORMAT.md): unknown kinds/targets are skipped with a NOTE, never a crash
    if int(queue.get("schema", 1)) > 1:
        log(f"NOTE: queue schema {queue.get('schema')} is newer than this script (1), update tg_story.py")
    todo = []
    for it in queue.get("items", []):
        iid = it.get("id")
        if not iid or iid in state["done"]:
            continue
        kind = it.get("kind") or ("link_post" if it.get("link") else
                                  "square_video" if it.get("target") == "binance_square" else "story_video")
        if kind in ("square_video", "diagnostic"):
            continue  # handled by Hermes itself
        if kind not in ("story_video", "link_post"):
            log(f"NOTE {iid}: skipped, unknown kind {kind}; need: instructions for {kind} in FORMAT.md")
            continue
        need = ["video"] if kind == "story_video" else ["link"]
        miss = [f for f in need if not it.get(f)]
        if miss:
            log(f"FAIL {iid}: missing {','.join(miss)}")
            continue
        it["kind"] = kind
        todo.append(it)
    if not todo:
        log("queue: nothing new")
        if time.strftime("%H%M") < "0030":  # daily heartbeat
            report(cfg, state, "alive, queue empty")
        return
    c = await client_for(cfg)
    if not await c.is_user_authorized():
        sys.exit("Not logged in: run `python tg_story.py login` first")
    channel = await c.get_entity(cfg["TG_CHANNEL"])
    limit = int(cfg.get("TG_CAPTION_LIMIT", "200"))  # 200 without Premium, 2048 with
    for it in todo:
        try:
            if it["kind"] == "link_post":  # text post with a YouTube Shorts link; Telegram shows the video preview
                text = it.get("post_text") or it.get("caption", "")
                if it["link"] not in text:
                    text += "\n\n" + it["link"]
                msg = await c.send_message(channel, text, link_preview=True)
                state["done"][it["id"]] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "story": None, "post": msg.id}
                STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False))
                log(f"OK {it['id']}: link post {msg.id}")
                continue
            with tempfile.TemporaryDirectory() as tmp:
                src = Path(tmp) / "video.mp4"
                fetch(RAW + it["video"], src)
                vid = shrink(src)
                dur, w, h = probe(vid)
                caption = (it.get("caption") or "")[:limit]
                up = await c.upload_file(str(vid))
                media = InputMediaUploadedDocument(
                    file=up, mime_type="video/mp4",
                    attributes=[DocumentAttributeVideo(duration=dur, w=w, h=h, supports_streaming=True)])
                res = await c(SendStoryRequest(
                    peer=channel, media=media, privacy_rules=[InputPrivacyValueAllowAll()],
                    caption=caption, period=int(it.get("period_hours") or 24) * 3600,
                    pinned=bool(it.get("pinned", True))))
                story_id = next((u.id for u in getattr(res, "updates", []) if hasattr(u, "id")), None)
                post_id = None
                if it.get("also_post"):
                    msg = await c.send_file(channel, str(vid), caption=it.get("post_text") or it.get("caption", ""),
                                            supports_streaming=True)
                    post_id = msg.id
            state["done"][it["id"]] = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "story": story_id, "post": post_id}
            STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False))
            log(f"OK {it['id']}: story posted" + (f", post {post_id}" if post_id else ""))
        except Exception as e:
            log(f"FAIL {it['id']}: {type(e).__name__}: {e}")
    await c.disconnect()
    report(cfg, state, "run finished")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    cfg = load_config()
    fn = {"login": cmd_login, "check": cmd_check, "run": cmd_run}.get(cmd)
    if not fn:
        sys.exit(__doc__)
    asyncio.run(fn(cfg))


if __name__ == "__main__":
    main()
