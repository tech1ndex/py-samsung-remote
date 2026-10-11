from flask import Flask, jsonify, render_template_string
from samsungtvws import SamsungTVWS
from samsungtvws.exceptions import (
    ConnectionFailure,
    HttpApiError,
    MessageError,
    ResponseError,
    UnauthorizedError,
)
from websocket import WebSocketException

from samsung_remote.settings import settings

TV_ERRORS = (
    ConnectionFailure,
    HttpApiError,
    MessageError,
    ResponseError,
    UnauthorizedError,
    WebSocketException,
    OSError,
)

KEYS = {
    "power": "KEY_POWER",
    "volup": "KEY_VOLUP",
    "voldown": "KEY_VOLDOWN",
    "mute": "KEY_MUTE",
    "up": "KEY_UP",
    "down": "KEY_DOWN",
    "left": "KEY_LEFT",
    "right": "KEY_RIGHT",
    "enter": "KEY_ENTER",
    "back": "KEY_RETURN",
    "home": "KEY_HOME",
    "source": "KEY_SOURCE",
}

app = Flask(__name__)

PAGE = """
<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Samsung TV Remote</title>
<style>
  body { font-family: -apple-system, sans-serif; background:#111; color:#fff; margin:0; padding:16px; }
  .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; max-width:420px; margin:auto; }
  button { font-size:20px; padding:22px 0; border:0; border-radius:14px; background:#2a2a2e; color:#fff; }
  button:active { background:#0a84ff; }
  .wide { grid-column: span 3; }
</style>
<div class="grid">
  <button onclick="k('power')">⏻</button><button onclick="k('source')">Source</button><button onclick="k('mute')">Mute</button>
  <button onclick="k('volup')">Vol +</button><button onclick="k('up')">▲</button><button onclick="k('home')">Home</button>
  <button onclick="k('left')">◀</button><button onclick="k('enter')">OK</button><button onclick="k('right')">▶</button>
  <button onclick="k('voldown')">Vol &minus;</button><button onclick="k('down')">▼</button><button onclick="k('back')">Back</button>
</div>
<script>
  function k(name){ fetch('/key/'+name, {method:'POST'}); if(navigator.vibrate) navigator.vibrate(10); }
</script>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/key/<name>")
def key(name):
    if name not in KEYS:
        return jsonify(error="unknown key"), 404
    try:
        tv = SamsungTVWS(
            host=settings.host,
            port=settings.port,
            name="PyRemote",
            timeout=5,
        )
        tv.send_key(KEYS[name])
        return jsonify(ok=True)
    except TV_ERRORS as e:
        return jsonify(error=str(e)), 500


def main():
    app.run(host=settings.server_host, port=settings.server_port)


if __name__ == "__main__":
    main()
