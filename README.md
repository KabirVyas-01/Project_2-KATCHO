# 🎮 KATCHO — Real-Time Multiplayer Party Game

**Created by KABIR VYAS**

**KATCHO** is a real-time multiplayer social deduction and memory party game built for mobile and desktop web browsers. Players secretly submit words, memorize a high-speed visual sequence flashed by the Visual Moderator, and take turns deducing who wrote what using a truth-locked verification system.

---

## ✨ Key Features

- **Brand Header**: Prominently displays `KATCHO` and `Created by KABIR VYAS`.
- **Dynamic Word Mode (< 7 Players)**:
  - When fewer than 7 players are in the room, the host can choose:
    - **1 Word Per Player** (Standard mode)
    - **2 Words Per Player (Double Word Mode)**: Each player submits 2 secret words one after the other. Gives smaller groups a richer flash pool (e.g. 4 players = 8 words) and deeper multi-word deduction gameplay!
- **Dual-Mode Networking**:
  - **Local Hotspot / LAN Mode (Mini Militia style)**: Host turns on a mobile hotspot; friends connect and scan the auto-generated QR code to play with **zero internet / mobile data usage**.
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

## 📱 Playing on Wi-Fi Hotspot (Zero Mobile Data)

1. Turn on **Mobile Hotspot** on the Host's laptop or mobile phone.
2. Have all friends connect their phones to that Hotspot / Wi-Fi network.
3. Start the server on the Host device: `python main.py`.
4. Friends can either:
   - Scan the **QR Code** displayed on the host's screen or clicking the 📱 icon.
   - Type the LAN URL (e.g. `http://192.168.43.1:8000`) into their mobile browser.

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
