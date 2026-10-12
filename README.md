# Al Aghani Radio Proxy (ESP32)

Live radio proxy for Egyptian Radio Al Aghani (إذاعة الأغاني المصرية 105.8 FM) designed for ESP32 Internet Radio (`ESP32-audioI2S`).

Maspero broadcasts exclusively via Dailymotion live streaming using expiring signed security tokens and fragmented MP4 (`.m4s`) HLS segments. This lightweight proxy dynamically fetches fresh stream tokens, demuxes the stream via FFmpeg, and re-serves it as a clean HTTP/HTTPS ADTS AAC stream that the ESP32 can play continuously.

## Files
- `alagahni.py`: The Python proxy server
- `Dockerfile`: Container definition with Python 3.12 and FFmpeg
- `.dockerignore` / `.gitignore`: Ignored build artifacts

## Free 24/7 Cloud Deployment (Koyeb - Recommended)
1. Push this folder to a GitHub repository:
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git branch -M main
   git push -u origin main
   ```
2. Go to [koyeb.com](https://www.koyeb.com) and create a free account (Sign in with GitHub).
3. Click **Create Web Service** -> Select **GitHub**.
4. Choose your repository.
5. Koyeb automatically detects the `Dockerfile`.
6. Click **Deploy**.
7. Copy your public URL:
   `https://<your-app-name>.koyeb.app/aghani`

## ESP32 Arduino Usage
```cpp
#include "Audio.h"

Audio audio;

void setup() {
    // Connect Wi-Fi...
    audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
    audio.setVolume(15);
    audio.connecttohost("https://<your-app-name>.koyeb.app/aghani");
}

void loop() {
    audio.loop();
}
```
