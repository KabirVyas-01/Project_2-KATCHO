# 🎮 KATCHO — Real-Time Multiplayer Party Game

**Created by KABIR VYAS**

**KATCHO** is a real-time multiplayer social deduction and memory party game built for mobile and desktop web browsers. Players secretly submit words, memorize a high-speed visual sequence flashed by the Visual Moderator, and take turns deducing who wrote what using a truth-locked verification system.

---

## KATCHO's live url link: https://katcho.onrender.com


## ✨ Key Features

- **Brand Header**: Prominently displays `KATCHO` and `Created by KABIR VYAS`.
- **Dynamic Word Mode (< 7 Players)**:
  - When fewer than 7 players are in the room, the host can choose:
    - **1 Word Per Player** (Standard mode)
    - **2 Words Per Player (Double Word Mode)**: Each player submits 2 secret words one after the other. Gives smaller groups a richer flash pool (e.g. 4 players = 8 words) and deeper multi-word deduction gameplay!
- **Dual-Mode Networking**:
  - **Local Hotspot / LAN Wi-Fi Portal (Mini Militia style)**: Host turns on mobile hotspot (or shared Wi-Fi). Friends open the game and active rooms on the network are automatically discovered on the **Hotspot / LAN Portal Radar** — tap once to join with **zero mobile data / internet**, no QR codes or link sharing needed!
  - **Online Room Mode (Skribbl.io style)**: 4-letter alphanumeric room codes for hosting and joining over the web.
- **Skribbl.io-Inspired Layout**:
  - **Top Stage**: Clean presentation board for Lobby info, 2-Pass synchronized Word Flash sequence, live public announcements, and victory reveal table.
  - **Player Roster**: Distinct vibrant colors assigned to each player, active turn ring, alive/caught status, and score badges.
  - **Private Scratchpad**: Personal on-device notes `<textarea>` that auto-saves to `localStorage` and is never sent over the network.
  - **Truth-Locked Verification**: Server-enforced truth system where accused players see ONLY a "YES" button (if correct) or ONLY a "NO" button (if wrong).
  - **Victory Reveal Table**: Post-game summary showing:
    1. Player Name & Avatar
    2. Original Secret Words
    3. Status (Winner / Caught / Draw)
    4. Correct Guesses Count
    5. Eliminated By (who caught them)
  - **Audio Synthesizer**: Built-in Web Audio API sound effects (ticks, chimes, buzzers, victory fanfare) with no external audio file dependencies.

---

## 🚀 Quickstart & Installation

### 1. Requirements
- Python 3.10 or higher
- Modern web browser on mobile or PC (Chrome, Safari, Firefox, Edge)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Server
```bash
python main.py
```
By default, the server starts on port `8000` and displays:
- **Local URL**: `http://localhost:8000`
- **LAN / Hotspot URL**: `http://<YOUR_LOCAL_IP>:8000`

---

## 📱 Playing on Wi-Fi Hotspot / LAN (Mini Militia Portal — Zero Mobile Data)

You can play KATCHO locally without an active internet connection using a mobile hotspot or shared Wi-Fi network.

### 💻 Option A: Hosting from a Laptop
1. Turn on **Mobile Hotspot** on the Host's laptop (e.g., in Windows: Settings > Network & Internet > Mobile hotspot).
2. Have all players connect their phones or laptops to that laptop's Hotspot Wi-Fi network.
3. Start the server on the laptop by running: `python main.py`.
4. The terminal will display your **LAN / Hotspot URL** (e.g., `http://192.168.137.1:8000`).
5. **Host:** Open your browser and go to `http://localhost:8000` to create a room.
6. **Players:** Open your browser and go to the host's **LAN / Hotspot URL**. Active rooms are automatically discovered on the **Hotspot / LAN Portal Radar**. Tap **Join**!

### 📱 Option B: Hosting from a Mobile Phone
1. Turn on **Mobile Hotspot** on the Host's phone (Mobile cellular data can be **OFF**).
2. Have all players connect their devices to your phone's Hotspot network.
3. Use a Python environment app on your phone (like Termux on Android or a-Shell on iOS) to run: `python main.py`.
4. The terminal will output your **LAN / Hotspot URL** (e.g., `http://192.168.43.1:8000`).
5. **Host & Players:** Open your web browser and navigate to that URL.
6. Active rooms will appear on the **Hotspot / LAN Portal Radar**. Tap **Join** to enter the lobby instantly!

---
 
## Offline Hotspot / LAN Mode: Why It's Still Pending
 
The goal is a "Mini Militia" experience: friends join the same Wi-Fi hotspot, tap a room, and play with **zero mobile data**. It sounds small, but a browser game is not a native app, and several problems stack up.
 
### 1. Someone has to be the server
Online play runs on a hosted server. Offline play needs one player's device to *be* the server. Katcho's backend is Python, and phones can't run it normally. Today the host would need a laptop, or a phone with Termux or a-Shell, which is far too much setup for a casual party game.
 
### 2. Browsers can't discover rooms on their own
Native apps find nearby games using UDP broadcast or mDNS. A web page has no access to either. That means a true auto-discovery "radar" isn't possible from the browser alone: a player must already know the host's address before the page can show any rooms.
 
### 3. The address changes every time
Hotspots hand out different IPs depending on the device (Android, iPhone, and Windows all differ), so there's no fixed link to share. Typing `192.168.x.x:8000` on a phone in a noisy room is a poor experience.
 
### 4. The online site can't talk to a local host
The live site is served over HTTPS. Browsers block an HTTPS page from calling an insecure `http://192.168...` server (mixed content), so the hosted site can't simply scan for or connect to a LAN host. Offline play has to be served by the host itself.
 
### 5. No HTTPS on a local network
Pages served from a plain local IP aren't a "secure context", so features such as the service worker and PWA install **don't work** there. The offline experience can't be an installed app unless extra certificate work is done.
 
### 6. Networks and firewalls get in the way
- The host's firewall often blocks incoming connections until the user allows Python on private networks.
- Many college and café Wi-Fi networks use client isolation, so devices can't see each other at all. Only a personal hotspot is reliable.
- Hotspot behavior differs between Android, iOS, and Windows.
  
### 7. Everything must work with no internet
No CDN scripts, no web fonts, no remote assets. Every file has to be served by the host. Sound is already handled (it's synthesized, not downloaded), but the rest of the frontend must be audited and bundled.
 
---

## 🕹️ Game Rules & State Flow

1. **Phase 1: Lobby & Secret Word Entry**
   - Players enter their name (saved in `localStorage`).
   - If player count < 7, host is prompted to choose **1 Word** or **2 Words (Double Word)** mode.
   - Players submit their secret word(s) (automatically trimmed & capitalized).
   - Once all players have locked in their words, the host clicks **Begin Reveal Sequence**.

2. **Phase 2: Visual Moderator (Word Flash)**
   - All submitted words are randomized.
   - Words flash one by one on the Top Stage for 1.0 second each in vibrant colors.
   - The sequence runs once, and then immediately repeats a second time.

3. **Phase 3: Guessing & Turn Resolution**
   - Active player selects a target player and types a suspected word.
   - Accused player receives an interactive modal on their screen with ONLY the truthful button:
     - If guess is correct: Accused sees ONLY **"YES"**. Word is marked caught. When all words of a player are caught, they are fully eliminated. Guesser keeps their turn!
     - If guess is wrong: Accused sees ONLY **"NO"**. Turn transfers directly to the accused.
   - **Pass Turn**: Active player can randomly pass the turn to someone else.
   - **Call Draw**: Active player can call a vote. If all players agree, game ends in a draw.

4. **Phase 4: Victory & Reset**
   - Last uncaught player wins the game!
   - Victory reveal table displays all original secret words, deduction points, and elimination history.
   - Server purges words from memory. Click **Play Again** to start a new round with the same players.

---

## 🧪 Running Automated Tests

```bash
python test_game.py
python test_server.py
```
