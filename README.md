# Al Aghani Radio Proxy (ESP32)

Live radio proxy for Egyptian Radio Al Aghani (إذاعة الأغاني المصرية 105.8 FM) designed for ESP32 Internet Radio (`ESP32-audioI2S`).

Maspero broadcasts exclusively via Dailymotion live streaming using expiring signed security tokens and fragmented MP4 (`.m4s`) HLS segments. This lightweight proxy dynamically fetches fresh stream tokens, demuxes the stream via FFmpeg, and re-serves it as a clean HTTP/HTTPS ADTS AAC stream that the ESP32 can play continuously.

## 🚀 1-Click Free Cloud Deployment

### Option A: Render (Easiest 1-Click)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/AhmedGamal111/al-aghani-proxy)

Click the button above or open:
👉 **[Deploy to Render](https://render.com/deploy?repo=https://github.com/AhmedGamal111/al-aghani-proxy)**

### Option B: Koyeb (24/7 Never Sleeps)
👉 **[Deploy on Koyeb](https://app.koyeb.com/services/deploy?type=git&repository=AhmedGamal111/al-aghani-proxy&branch=main&name=al-aghani-proxy)**

---

## 📻 ESP32 Arduino Usage

Once deployed, your stream URL will be:
- On Render: `https://al-aghani-proxy.onrender.com/aghani`
- On Koyeb: `https://<your-service-name>.koyeb.app/aghani`

```cpp
#include "Audio.h"

Audio audio;

void setup() {
    Serial.begin(115200);
    // Connect to Wi-Fi...
    
    audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
    audio.setVolume(15);
    
    // Connect to your cloud proxy
    audio.connecttohost("https://al-aghani-proxy.onrender.com/aghani");
}

void loop() {
    audio.loop();
}
```
