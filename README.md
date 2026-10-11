```text
                                                                      _       
 ___  __ _ _ __ ___  ___ _   _ _ __   __ _   _ __ ___ _ __ ___   ___ | |_ ___ 
/ __|/ _` | '_ ` _ \/ __| | | | '_ \ / _` | | '__/ _ \ '_ ` _ \ / _ \| __/ _ \
\__ \ (_| | | | | | \__ \ |_| | | | | (_| | | | |  __/ | | | | | (_) | ||  __/
|___/\__,_|_| |_| |_|___/\__,_|_| |_|\__, | |_|  \___|_| |_| |_|\___/ \__\___|
                                     |___/                                    
```

A small Flask app that serves a mobile-friendly web remote for a Samsung Smart TV on your
local network. Open it on your phone, tap a button, and the keypress is relayed to the TV
over the SamsungTV WebSocket API.

## Configuration

All settings are read from the environment with a `TV_` prefix, or from a `.env` file in the
project root. Real environment variables take precedence over `.env`.

| Variable           | Default           | Description                                        |
|--------------------|-------------------|----------------------------------------------------|
| `TV_HOST`          | `10.0.0.2`        | IP address of the Samsung TV                       |
| `TV_PORT`          | `8001`            | TV WebSocket port (`8001` plain, `8002` TLS)       |
| `TV_SERVER_HOST`   | `0.0.0.0`         | Interface the web server binds to                  |
| `TV_SERVER_PORT`   | `5001`            | Port the web server listens on                     |

Example `.env`:

```dotenv
TV_HOST=10.0.0.2
TV_PORT=8001
TV_SERVER_PORT=5001
```

> **Note:** `TV_SERVER_HOST` / `TV_SERVER_PORT` only apply when running locally. In Docker the
> bind address is fixed at `0.0.0.0:5001` by the Gunicorn `CMD` — map it with `-p` instead.

## Usage

### Docker

Build the image:

```bash
make docker
# or
docker build -t py-samsung-remote .
```

Run it:

```bash
docker run -d \
--name py-samsung-remote \
--restart unless-stopped \
-p 5001:5001 \
-e TV_HOST="10.0.0.2" \
-e TV_PORT=8001 \
py-samsung-remote:latest
```

Using an env file instead:

```bash
docker run -d --name py-samsung-remote --restart unless-stopped \
  -p 5001:5001 --env-file .env py-samsung-remote:latest
```

To expose it on a different host port, remap rather than changing `TV_SERVER_PORT`:

```bash
docker run --rm -p 8080:5001 -e TV_HOST="10.0.0.2" py-samsung-remote:latest
```

`make run` builds the image and runs it in the foreground on port 5001 using `.env`.

### Local development

```bash
make install                       # poetry install with dev, tests, and linter groups
poetry run samsung-remote          # start the Flask dev server
```

Or run the module directly:

```bash
TV_HOST=10.0.0.2 poetry run python src/samsung_remote/main.py
```

Then open `http://localhost:5001` on any device on the same network.

```bash
make lint   # mypy + ruff
make test   # pytest
```

## API

The web UI is a single page served at `/`; every button posts to the key endpoint.

| Method | Path          | Description                                       |
|--------|---------------|---------------------------------------------------|
| `GET`  | `/`           | The remote control page                           |
| `POST` | `/key/<name>` | Send a key to the TV                              |

`POST /key/<name>` returns `{"ok": true}` on success, `404` with `{"error": "unknown key"}`
for an unrecognised key name, and `500` with the error message if the TV cannot be reached.

```bash
curl -X POST http://localhost:5001/key/volup
curl -X POST http://localhost:5001/key/power
```

Supported key names: `power`, `volup`, `voldown`, `mute`, `up`, `down`, `left`, `right`,
`enter`, `back`, `home`, `source`.

## Notes

The TV must have **Remote Control / IP Control** enabled in its network settings. The first
time the app connects, the TV may show an on-screen prompt asking you to allow the device
named `PyRemote` — accept it, or the key requests will fail.

There is no authentication on the web UI, so only expose it on a trusted network.
