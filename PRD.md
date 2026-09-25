# Product Requirements Document (PRD) — KATCHO

## 1. Executive Summary
- **Product Name:** KATCHO
- **Author & Creator:** KABIR VYAS
- **Product Type:** Real-Time Multiplayer Social Deduction & Memory Party Game
- **Platform:** Progressive Web App (PWA) / Responsive Web (Mobile, Tablet, Desktop) & Local Offline LAN/Hotspot
- **Core Technology Stack:**
  - **Backend:** Python 3, FastAPI, WebSockets (`/ws/{room_code}/{player_id}`), Uvicorn, QR Code generation (PIL)
  - **Frontend:** Vanilla JavaScript (ES6+), WebSockets Client, Web Audio API Synthesizer, CSS3 Custom Properties, Responsive Flex/Grid
  - **PWA:** Web App Manifest (`manifest.json`), Service Worker (`service-worker.js`), LocalStorage offline caching

---

## 2. Product Vision & Goals
- **Objective:** Provide a fast, hilarious, high-engagement party deduction experience that runs seamlessly in any web browser without user registration or app store downloads.
- **Key Differentiator:** Combines **memory retention** (word flash) with **social bluffing & deduction** and a cryptographic **Truth-Locked Verification System** where lying is impossible.
- **Offline Capability:** 100% playable over a local Wi-Fi or mobile hotspot without cellular internet.

---

## 3. User Personas
1. **The Game Host (Organizer):**
   - Wants to start a room in 3 seconds, configure rules (1 vs 2 words mode), and share a 4-letter room PIN or QR code with friends in the room or online.
2. **The Guest Player:**
   - Joins on their phone via QR code scan or PIN, submits secret words, watches the flash sequence, and makes deductions during their turn.
3. **The Offline Group:**
   - Friends hanging out outdoors or at campus with no Wi-Fi/mobile data, connecting directly to the host's mobile hotspot.

---

## 4. Game Rules & Complete Lifecycle

### Phase 1: Lobby & Secret Word Lock-In (`LOBBY`)
- Players join the room using a 4-letter code.
- Dynamic Word Mode:
  - **Default:** 1 Word per player.
  - **Double Word Mode:** Available for matches with fewer than 7 players (each player enters 2 secret words).
- Each player enters and locks their secret word(s).
- Words are trimmed, capitalized, validated (2–25 characters), and stored privately in memory.
- The host starts the reveal sequence once all players are ready (minimum 2 players).

### Phase 2: Visual Moderator Word Flash (`REVEAL`)
- The server collects all submitted words and randomizes their order.
- The words flash sequentially on the presentation stage (3 seconds per word) with visual pop animations and color palettes.
- The sequence runs through 2 full loops.
- **Anti-Cheat Lock:** The private scratchpad is **automatically disabled and locked** during the word flashes so players cannot cheat by typing words in real time.

### Phase 3: Guessing & Deduction (`GUESSING`)
- The visual moderator ends, and the scratchpad is automatically unlocked.
- A random starting player receives the active turn.
- **Actions available to the active turn player:**
  1. **Accuse Target Player:** Select an active player and type a suspected secret word.
  2. **Pass Turn:** Randomly transfer the turn to another active player.
  3. **Call Unanimous Draw:** Trigger a vote where all players must agree to end in a draw.
- **Truth-Locked Verification:**
  - When accused, the target player receives an immutable prompt with a single verified action:
    - If the word matches: `✅ YES! (That is my word)` → Target is caught/eliminated, guesser keeps their turn.
    - If the word does NOT match: `❌ NO! (Not my word)` → Guesser loses turn, turn passes to the accused.

### Phase 4: Match Victory / Game Over (`GAME_OVER`)
- When only 1 uncaught player remains (or unanimous draw is accepted), the match ends.
- Victory fanfare audio is triggered.
- A complete **Reveal Table** unmasks all players, secret words, deduction accuracy scores, and elimination history.
- Host/players can click **"Play Again"** to start a new round with the same players.

---

## 5. Non-Functional Requirements & Security
1. **Real-Time Latency:** WebSocket broadcast state synchronization < 50ms.
2. **Anti-Cheat:**
   - Server-authoritative state (secret words are never sent in state payloads during Lobby, Reveal, or Guessing).
   - Scratchpad input locked during Phase 2.
   - Truth-locked responses validated by backend.
3. **PWA Installability:** Passes Lighthouse PWA criteria with offline app shell caching.
4. **Data Privacy:** Zero user account tracking or persistent database storage; all room data is auto-purged from server memory upon game reset or disconnect.
