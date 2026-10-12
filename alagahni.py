#!/usr/bin/env python3
"""
Al Aghani radio proxy for ESP32-audioI2S.

Maspero streams its channels through Dailymotion live, and the HLS link carries
a signed token that expires. This script asks Dailymotion for a fresh link every
time the ESP32 connects, pulls the audio with ffmpeg, and re-serves it as a plain
HTTP AAC (ADTS) stream, so the ESP32 never has to deal with HTTPS, HLS, or tokens.

Requirements: Python 3.8+, ffmpeg on PATH. No pip packages.

Run:    python alagahni.py
Test:   open  http://<this-machine-ip>:8080/aghani  in VLC or browser
ESP32:  audio.connecttohost("http://<this-machine-ip>:8080/aghani");
"""
import json
import os
import subprocess
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Taken from the .m3u8 URL: .../dm/4/x8n6dyz/live-aac-128.m3u8
VIDEO_ID = "x8n6dyz"
EMBEDDER = "https://www.maspero.eg/stream/13"
PORT = int(os.environ.get("PORT", 8080))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def resolve_audio_hls() -> str:
    """Resolve the direct signed AAC audio sub-stream URL from Dailymotion."""
    # 1. Ask Dailymotion for metadata and session cookies
    meta_url = (
        f"https://www.dailymotion.com/player/metadata/video/{VIDEO_ID}"
        f"?embedder={urllib.parse.quote(EMBEDDER, safe='')}&referer="
    )
    req = urllib.request.Request(meta_url, headers={"Referer": EMBEDDER, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=10) as resp:
        meta = json.load(resp)
        cookies = resp.headers.get_all("Set-Cookie") or []

    if "error" in meta:
        raise RuntimeError(f"Dailymotion error: {meta['error']}")

    cookie_dict = {}
    for c in cookies:
        part = c.split(";")[0]
        if "=" in part:
            k, v = part.split("=", 1)
            cookie_dict[k.strip()] = v.strip()
    cookie_header = "; ".join(f"{k}={v}" for k, v in cookie_dict.items())

    master_url = None
    for item in meta.get("qualities", {}).get("auto", []):
        if "mpegURL" in item.get("type", ""):
            master_url = item["url"]
            break

    if not master_url:
        raise RuntimeError("No HLS master URL found in Dailymotion metadata")

    # 2. Fetch master m3u8 using the Dailymotion session cookies
    mreq = urllib.request.Request(
        master_url,
        headers={
            "User-Agent": UA,
            "Referer": "https://www.dailymotion.com/",
            "Origin": "https://www.dailymotion.com",
            "Cookie": cookie_header,
        },
    )
    with urllib.request.urlopen(mreq, timeout=10) as mresp:
        m3u8_text = mresp.read().decode("utf-8", errors="ignore")

    # 3. Extract direct audio subplaylist (AAC 128k or fallback)
    audio_url = None
    fallback_url = None
    for line in m3u8_text.splitlines():
        if "TYPE=AUDIO" in line and 'URI="' in line:
            start = line.find('URI="') + 5
            end = line.find('"', start)
            uri = line[start:end]
            if "live-aac-128" in uri:
                audio_url = uri
                break
            elif not fallback_url:
                fallback_url = uri

    target = audio_url or fallback_url or master_url
    return target.split("#")[0]


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "audio/aac")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path not in ("/", "/aghani"):
            self.send_error(404)
            return

        print(f"Resolving audio stream for {self.client_address[0]}...", flush=True)
        try:
            audio_url = resolve_audio_hls()
        except Exception as exc:
            print(f"Resolve failed: {exc}", flush=True)
            self.send_error(502, "Could not resolve stream")
            return

        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5",
            "-i", audio_url,
            "-vn", "-c:a", "copy",
            "-f", "adts", "pipe:1",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.send_response(200)
        self.send_header("Content-Type", "audio/aac")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        print(f"Client connected: {self.client_address[0]}", flush=True)
        try:
            while True:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            proc.kill()
            print(f"Client disconnected: {self.client_address[0]}", flush=True)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Serving Al Aghani on port {PORT}: /aghani and /", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()