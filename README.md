# 🗃️ cringe-onefile-coding-projects

> A grab-bag of one-file scripts, weekend hacks, and half-finished experiments — in Python, Go, Arduino/C++, Bash, and raw JS. Quality varies wildly. Use at your own risk, mostly for learning/CTF/fun.

## 📁 Full Index

| File | Category | Language | What it does | Status / Notes |
|---|---|---|---|---|
| [`crack.py`](crack.py) | 🔐 Security | Python | Generates random fake `sk-...` OpenAI-style API keys and hits the OpenAI API in a loop to see if any happen to be valid. | Educational only — brute-forcing API keys like this is pointless/abusive against a real API; don't run against production endpoints. |
| [`wifi.py`](wifi.py) | 🔐 Security | Python | Scans nearby Wi-Fi networks via `pywifi` and lays groundwork for password-guessing against an AP. | Rough/incomplete; for lab use on networks you own only. |
| [`wifi2.py`](wifi2.py) | 🔐 Security | Python | Second pass at Wi-Fi scanning/connecting, using the `wifi` module instead of `pywifi`. | Simpler, Windows/Linux branch logic is unfinished. |
| [`Top_1m_Passwords.txt`](Top_1m_Passwords.txt) | 🔐 Security (data) | Wordlist | Top 1,000,000 common passwords — dictionary file for CTF/cracking exercises. | Pairs with `wifi.py`/`wifi2.py`. |
| [`aitelebot.py`](aitelebot.py) | 🤖 Bots & Automation | Python | Telegram bot (via `python-telegram-bot`) that turns a user's text message into a stylized image using PIL. | Proof-of-concept scaffold. |
| [`discord_test.py`](discord_test.py) | 🤖 Bots & Automation | Python | Discord bot that DMs a specific user a live internet speed test (download/upload/ping) on a loop. | Has a bot token placeholder; minor syntax bug in the speedtest string build. |
| [`webhook_stuff.py`](webhook_stuff.py) | 🤖 Bots & Automation | Python | Keeps a Flask "I'm alive" server running in a thread while continuously generating random `prnt.sc/xxxxx` URLs and POSTing them to a Discord webhook. | Looks like a screenshot-link scraping/spam experiment; reads webhook URL from `config.json`. |
| [`instagram-automater.py`](instagram-automater.py) | 🤖 Bots & Automation | Python | Tkinter desktop GUI for uploading/posting to Instagram via `instagrapi`, with login session caching to a temp dir. | Most complete/polished script in the repo. |
| [`chromee.py`](chromee.py) | 🤖 Bots & Automation | Python | Walks the entire filesystem for `.exe` files and launches whichever ones run cleanly — effectively a "generate fake activity / jam the machine" script using `pyautogui` + `tkinter`. | Labelled as a "powershell backup program" in a comment; opens arbitrary executables, use with real caution. |
| [`googlesheetdataget`](googlesheetdataget) | 🤖 Bots & Automation | JavaScript (browser snippet) | Takes a public Google Sheets URL, pulls the sheet ID out of it, and fetches cell data from the (legacy) Sheets "feeds" JSON API to display on a page. | No file extension; relies on the old deprecated Sheets feeds API. |
| [`youtube.py`](youtube.py) | 🎬 Media Downloaders | Python | Downloads every video in a YouTube playlist via `pytube`. | Depends on `pytube`, which breaks often as YouTube changes. |
| [`s_video.py`](s_video.py) | 🎬 Media Downloaders | Python | Downloads a single YouTube video (highest available resolution) via `pytube`. | Same `pytube` caveat as above. |
| [`displayer.py`](displayer.py) | 🔧 Hardware / IoT | Python | Drives a Raspberry Pi SPI OLED display (SSD1306/SH1106 via `luma.oled`) to render a pair of animated robot "eyes." | Needs real GPIO/SPI wiring to run — not testable off-device. |
| [`neocolab_automater.ino`](neocolab_automater.ino) | 🔧 Hardware / IoT | Arduino/C++ (ESP32) | Turns an ESP32 into a Bluetooth "typewriter" keyboard (`BleKeyboard`) controllable from a phone/browser over Wi-Fi via a built-in web page. | Has hardcoded Wi-Fi SSID/password in source — scrub before sharing publicly. |
| [`emoproxy.go`](emoproxy.go) | 🔧 Hardware / IoT | Go | Local reverse proxy/MITM that intercepts and logs calls between an "Emo" robot and its cloud backend (`living.ai` API/TTS/resource servers), disabling TLS verification. | Reverse-engineering/interception tool for a specific consumer robot. |
| [`data2video.py`](data2video.py) | 🧪 Experimental | Python | Converts any file into a giant binary string and back into bytes — a raw bit-level encode/decode round-trip. | Despite the filename, doesn't actually touch video; just a binary-serialization toy. |
| [`b2v.py`](b2v.py) | 🧪 Experimental | Python | Queries the Wordnik API for random words matching a part-of-speech pattern and stitches them into a nonsense "sentence" — pitched as a random app-idea generator. | Needs a Wordnik API key to run. |
| [`rotatingcube.py`](rotatingcube.py) | 🧪 Experimental | Python | Renders a rotating 3D wireframe cube as ASCII/block characters directly in the terminal, using Bresenham line drawing. | Pure terminal-graphics fun, no dependencies. |
| [`alarm.sh`](alarm.sh) | 🧪 Experimental | Bash | Terminal countdown alarm clock — counts down from 90 minutes, beeps every 15 "minutes" via `paplay`, then beeps twice at zero. | Linux desktop (PulseAudio/`paplay`) only. |
| [`AquaMesh_Digital_Twin (2).zip`](<AquaMesh_Digital_Twin (2).zip>) | 🌊 Full Mini-Project | HTML/CSS/JS (zipped web app) | A local-first, offline "digital twin" dashboard for urban flood sensing: animated isometric scene, simulated telemetry/event log, scenario controls (rainfall, drain blockage, sensor faults, etc.), node inspector, and CSV export. Ships with a `run_windows.bat` and a plain `python -m http.server` option. | The most "finished" thing in the repo — no build step, no cloud account needed, designed to later hook up to a real Raspberry Pi sensor feed. |
| [`p1ia54.pdf`](p1ia54.pdf) | 📄 Unrelated Attachment | PDF | Not code — a scanned language-learning book, *Three Languages Speaking Course (English–Hindi–Manipuri)*. | Looks like a stray upload, unrelated to any script here. |
| [`xlarge-5b4315c2d98798b04c977d2c1f88e723.webp`](xlarge-5b4315c2d98798b04c977d2c1f88e723.webp) | 📄 Unrelated Attachment | Image | Not code — a screenshot of a Blender add-on's right-click context-menu feature ("Context menu integration") for restoring snapshots. | Likely a reference/inspiration image, unrelated to any script here. |

## 🗂️ Categories at a glance

- **🔐 Security** — `crack.py`, `wifi.py`, `wifi2.py`, `Top_1m_Passwords.txt`
- **🤖 Bots & Automation** — `aitelebot.py`, `discord_test.py`, `webhook_stuff.py`, `instagram-automater.py`, `chromee.py`, `googlesheetdataget`
- **🎬 Media Downloaders** — `youtube.py`, `s_video.py`
- **🔧 Hardware / IoT** — `displayer.py`, `neocolab_automater.ino`, `emoproxy.go`
- **🧪 Experimental / Just-for-fun** — `data2video.py`, `b2v.py`, `rotatingcube.py`, `alarm.sh`
- **🌊 Full mini-project** — `AquaMesh_Digital_Twin (2).zip`
- **📄 Non-code attachments** — `p1ia54.pdf`, `xlarge-5b4315c2d98798b04c977d2c1f88e723.webp`

## ⚠️ A note on the security scripts

`crack.py`, `wifi.py`, and `wifi2.py` are kept here for CTF practice and learning purposes only. Don't point them at networks or accounts you don't own or have explicit permission to test.

## 📜 License

MIT License — see `LICENSE` for details.
