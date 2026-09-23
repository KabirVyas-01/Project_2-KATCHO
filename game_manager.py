"""
KATCHO - Real-Time Multiplayer Party Game
Game Manager: State transitions, Room lifecycle, Dynamic Word Modes (1 vs 2 words), and Truth-Locked Verification.
Created for: KABIR VYAS
"""

import random
import string
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict

PLAYER_COLORS = [
    "#FF4757",  # Bright Coral Red
    "#2ED573",  # Vibrant Green
    "#1E90FF",  # Sky Blue
    "#FFA502",  # Vivid Orange
    "#9B59B6",  # Royal Purple
    "#00D2D3",  # Neon Cyan
    "#FF6B81",  # Flamingo Pink
    "#70A1FF",  # Soft Cobalt
    "#20BF6B",  # Emerald Green
    "#FA8231",  # Sunset Orange
    "#8854D0",  # Deep Violet
    "#3867D6",  # Royal Blue
    "#E84393",  # Prune Rose
    "#00CEC9",  # Robin's Egg
    "#F39C12",  # Bright Amber
    "#4CD137",  # Lime Burst
]


class GamePhase(str, Enum):
    LOBBY = "LOBBY"          # Entering names, choosing word mode, submitting secret words
    REVEAL = "REVEAL"        # Word flash sequence (2 synchronized loops)
    GUESSING = "GUESSING"    # Real-time social deduction and turn guessing
    GAME_OVER = "GAME_OVER"  # Match ended, victory reveal table shown


@dataclass
class Player:
    id: str
    name: str
    secret_words: List[str] = field(default_factory=list)
    caught_words: List[str] = field(default_factory=list)
    is_host: bool = False
    is_caught: bool = False
    color: str = "#1E90FF"
    correct_guesses: int = 0
    eliminated_by: Optional[str] = None
    is_connected: bool = True
    joined_at: float = field(default_factory=time.time)

    def to_public_dict(self, words_required: int = 1, include_secret_words: bool = False) -> Dict[str, Any]:
        has_submitted = len(self.secret_words) >= words_required
        data = {
            "id": self.id,
            "name": self.name,
            "is_host": self.is_host,
            "is_caught": self.is_caught,
            "color": self.color,
            "has_submitted_word": has_submitted,
            "submitted_words_count": len(self.secret_words),
            "words_required": words_required,
            "caught_words": list(self.caught_words),
            "correct_guesses": self.correct_guesses,
            "eliminated_by": self.eliminated_by,
            "is_connected": self.is_connected,
        }
        if include_secret_words:
            data["secret_words"] = list(self.secret_words)
        return data


class Room:
    def __init__(self, code: str, host_id: str):
        self.code: str = code
        self.host_id: str = host_id
        self.players: Dict[str, Player] = {}
        self.phase: GamePhase = GamePhase.LOBBY
        self.words_per_player: int = 1
        self.mode_chosen_by_host: bool = False
        self.word_sequence: List[str] = []
        self.current_turn_player_id: Optional[str] = None
        self.active_accusation: Optional[Dict[str, Any]] = None
        self.active_draw_vote: Optional[Dict[str, Any]] = None
        self.winner_id: Optional[str] = None
        self.is_draw: bool = False
        self.recent_announcement: Optional[Dict[str, Any]] = None
        self.announcements_history: List[Dict[str, Any]] = []
        self.created_at: float = time.time()
        self.last_activity: float = time.time()

    def touch(self):
        self.last_activity = time.time()

    def get_connected_players(self) -> List[Player]:
        return [p for p in self.players.values() if p.is_connected]

    def get_uncaught_players(self) -> List[Player]:
        # Uncaught means player still has at least 1 word not yet caught
        return [
            p for p in self.players.values()
            if p.is_connected and not p.is_caught and len(p.caught_words) < len(p.secret_words)
        ]

    def add_announcement(self, text: str, category: str = "info", highlight: str = ""):
        ann = {
            "text": text,
            "category": category,
            "highlight": highlight,
            "timestamp": time.time(),
        }
        self.recent_announcement = ann
        self.announcements_history.append(ann)
        if len(self.announcements_history) > 30:
            self.announcements_history.pop(0)

    def to_state_dict(self, for_player_id: Optional[str] = None) -> Dict[str, Any]:
        show_all_secrets = (self.phase == GamePhase.GAME_OVER)
        
        players_data = []
        for p in self.players.values():
            include_secrets = show_all_secrets or (for_player_id is not None and p.id == for_player_id)
            players_data.append(p.to_public_dict(
                words_required=self.words_per_player,
                include_secret_words=include_secrets
            ))

        # Readiness tracking
        total_players = len(self.players)
        submitted_ready_players = sum(
            1 for p in self.players.values() if len(p.secret_words) >= self.words_per_player
        )
        total_words_submitted = sum(len(p.secret_words) for p in self.players.values())
        total_words_required = total_players * self.words_per_player

        turn_player_name = None
        if self.current_turn_player_id and self.current_turn_player_id in self.players:
            turn_player_name = self.players[self.current_turn_player_id].name

        safe_accusation = None
        if self.active_accusation:
            safe_accusation = {
                "guesser_id": self.active_accusation["guesser_id"],
                "guesser_name": self.active_accusation["guesser_name"],
                "target_id": self.active_accusation["target_id"],
                "target_name": self.active_accusation["target_name"],
                "guessed_word": self.active_accusation["guessed_word"],
                "resolved": self.active_accusation["resolved"],
            }
            if for_player_id == self.active_accusation["target_id"]:
                safe_accusation["truth_answer"] = self.active_accusation["is_correct"]

        safe_draw = None
        if self.active_draw_vote:
            initiator = self.players.get(self.active_draw_vote["initiator_id"])
            safe_draw = {
                "initiator_id": self.active_draw_vote["initiator_id"],
                "initiator_name": initiator.name if initiator else "Unknown",
                "total_needed": len(self.players),
                "votes_count": len(self.active_draw_vote["votes"]),
                "my_vote": self.active_draw_vote["votes"].get(for_player_id) if for_player_id else None,
            }

        winner_name = None
        if self.winner_id and self.winner_id in self.players:
            winner_name = self.players[self.winner_id].name

        return {
            "room_code": self.code,
            "phase": self.phase.value,
            "host_id": self.host_id,
            "is_host": (for_player_id == self.host_id),
            "words_per_player": self.words_per_player,
            "mode_chosen_by_host": self.mode_chosen_by_host,
            "prompt_mode_selection": (len(self.players) < 7 and not self.mode_chosen_by_host),
            "players": players_data,
            "total_players": total_players,
            "submitted_count": submitted_ready_players,
            "total_words_submitted": total_words_submitted,
            "total_words_required": total_words_required,
            "current_turn_player_id": self.current_turn_player_id,
            "current_turn_player_name": turn_player_name,
            "is_my_turn": (for_player_id is not None and for_player_id == self.current_turn_player_id),
            "word_sequence": self.word_sequence if self.phase in (GamePhase.REVEAL, GamePhase.GAME_OVER) else [],
            "active_accusation": safe_accusation,
            "active_draw_vote": safe_draw,
            "winner_id": self.winner_id,
            "winner_name": winner_name,
            "is_draw": self.is_draw,
            "recent_announcement": self.recent_announcement,
        }


class GameManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def _generate_room_code(self) -> str:
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        for _ in range(100):
            code = "".join(random.choices(chars, k=4))
            if code not in self.rooms:
                return code
        return "".join(random.choices(chars, k=5))

    def _assign_player_color(self, room: Room) -> str:
        used_colors = {p.color for p in room.players.values()}
        for color in PLAYER_COLORS:
            if color not in used_colors:
                return color
        return random.choice(PLAYER_COLORS)

    def create_room(self, host_name: str, host_id: str) -> Tuple[Room, Player]:
        room_code = self._generate_room_code()
        room = Room(code=room_code, host_id=host_id)
        
        color = PLAYER_COLORS[0]
        host_player = Player(
            id=host_id,
            name=host_name.strip()[:20] or "Host",
            is_host=True,
            color=color,
        )
        room.players[host_id] = host_player
        self.rooms[room_code] = room
        room.add_announcement(f"🎉 Room {room_code} created by {host_player.name}!", "success")
        return room, host_player

    def join_room(self, room_code: str, player_name: str, player_id: str) -> Tuple[Optional[Room], Optional[Player], str]:
        room_code = room_code.strip().upper()
        room = self.rooms.get(room_code)
        if not room:
            return None, None, f"Room '{room_code}' does not exist."

        if player_id in room.players:
            player = room.players[player_id]
            player.name = player_name.strip()[:20] or player.name
            player.is_connected = True
            room.touch()
            return room, player, "Reconnected."

        if room.phase != GamePhase.LOBBY:
            return None, None, "Game is already in progress. Please wait for the next round or join a new room."

        color = self._assign_player_color(room)
        clean_name = player_name.strip()[:20] or f"Player {len(room.players) + 1}"
        
        player = Player(
            id=player_id,
            name=clean_name,
            is_host=(len(room.players) == 0 or room.host_id == player_id),
            color=color,
        )
        if player.is_host:
            room.host_id = player.id

        room.players[player_id] = player
        room.touch()
        room.add_announcement(f"👋 {player.name} joined the room!", "info")
        return room, player, "Joined successfully."

    def get_room(self, room_code: str) -> Optional[Room]:
        return self.rooms.get(room_code.strip().upper())

    def set_word_mode(self, room_code: str, player_id: str, words_per_player: int) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."

        if room.host_id != player_id:
            return False, "Only the host can set the word mode."

        if room.phase != GamePhase.LOBBY:
            return False, "Mode can only be changed in the Lobby."

        if words_per_player not in (1, 2):
            return False, "Mode must be 1 or 2 words per player."

        room.words_per_player = words_per_player
        room.mode_chosen_by_host = True
        
        # If reduced to 1 word, trim existing submitted words if any
        if words_per_player == 1:
            for p in room.players.values():
                if len(p.secret_words) > 1:
                    p.secret_words = p.secret_words[:1]

        room.touch()
        mode_label = "2 Words Per Player (Double Word Mode)" if words_per_player == 2 else "1 Word Per Player"
        room.add_announcement(f"⚙️ Host configured game mode: {mode_label}!", "success")
        return True, f"Word mode set to {words_per_player} word(s)."

    def submit_secret_words(self, room_code: str, player_id: str, words: List[str]) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."
        
        if room.phase != GamePhase.LOBBY:
            return False, "Words can only be submitted during the Lobby phase."

        player = room.players.get(player_id)
        if not player:
            return False, "Player not found."

        clean_words = []
        for w in words:
            cw = str(w).strip().upper()
            if not cw:
                continue
            if len(cw) < 2:
                return False, f"Word '{cw}' must be at least 2 characters long."
            if len(cw) > 25:
                return False, f"Word '{cw}' cannot exceed 25 characters."
            if cw in clean_words:
                return False, "Please submit distinct secret words (no duplicates)."
            clean_words.append(cw)

        if len(clean_words) < room.words_per_player:
            return False, f"Please submit {room.words_per_player} secret word(s)."

        player.secret_words = clean_words[:room.words_per_player]
        room.touch()
        count_str = f"{len(player.secret_words)} secret word{'s' if len(player.secret_words) > 1 else ''}"
        room.add_announcement(f"🔒 {player.name} locked in their {count_str}!", "info")
        return True, "Secret words locked in."

    def submit_single_secret_word(self, room_code: str, player_id: str, word: str, word_index: int = 0) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."

        player = room.players.get(player_id)
        if not player:
            return False, "Player not found."

        cw = word.strip().upper()
        if len(cw) < 2:
            return False, "Word must be at least 2 characters long."
        if len(cw) > 25:
            return False, "Word cannot exceed 25 characters."

        # Update word at index
        while len(player.secret_words) <= word_index:
            player.secret_words.append("")
        
        # Check duplicate
        for idx, existing in enumerate(player.secret_words):
            if idx != word_index and existing == cw:
                return False, "You cannot use the same secret word twice."

        player.secret_words[word_index] = cw
        player.secret_words = [w for w in player.secret_words if w]
        room.touch()
        return True, f"Word #{word_index + 1} saved."

    def start_reveal_phase(self, room_code: str, player_id: str) -> Tuple[bool, str, List[str]]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found.", []

        if room.host_id != player_id:
            return False, "Only the host can start the reveal.", []

        if len(room.players) < 2:
            return False, "At least 2 players are required to start the game.", []

        # If less than 7 players and mode hasn't been chosen yet, require host choice
        if len(room.players) < 7 and not room.mode_chosen_by_host:
            return False, "PROMPT_MODE_SELECTION", []

        # Verify all players have submitted all required words
        missing_players = [
            p.name for p in room.players.values()
            if len(p.secret_words) < room.words_per_player
        ]
        if missing_players:
            req = f"{room.words_per_player} word(s)"
            return False, f"Waiting for {', '.join(missing_players)} to submit {req}.", []

        # Collect and shuffle all submitted words
        all_words = []
        for p in room.players.values():
            all_words.extend(p.secret_words[:room.words_per_player])

        random.shuffle(all_words)
        room.word_sequence = all_words
        room.phase = GamePhase.REVEAL
        room.touch()
        room.add_announcement(f"✨ Visual Moderator started! {len(all_words)} total words flashing...", "warning")
        return True, "Reveal phase started.", room.word_sequence

    def finish_reveal_phase(self, room_code: str) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."

        if room.phase != GamePhase.REVEAL:
            return False, "Not in reveal phase."

        room.phase = GamePhase.GUESSING
        connected_players = [p.id for p in room.players.values() if p.is_connected]
        if connected_players:
            room.current_turn_player_id = random.choice(connected_players)
        else:
            room.current_turn_player_id = room.host_id

        starter = room.players.get(room.current_turn_player_id)
        starter_name = starter.name if starter else "Someone"
        room.touch()
        room.add_announcement(f"🎯 Guessing phase begun! First turn goes to {starter_name}!", "success")
        return True, "Guessing phase active."

    def make_accusation(self, room_code: str, guesser_id: str, target_id: str, guessed_word: str) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."

        if room.phase != GamePhase.GUESSING:
            return False, "Accusations are only allowed during the Guessing phase."

        if room.current_turn_player_id != guesser_id:
            return False, "It is not your turn to accuse."

        if room.active_accusation and not room.active_accusation.get("resolved"):
            return False, "Another accusation is currently being verified."

        if guesser_id == target_id:
            return False, "You cannot accuse yourself."

        guesser = room.players.get(guesser_id)
        target = room.players.get(target_id)
        if not guesser or not target:
            return False, "Guesser or target player not found."

        clean_word = guessed_word.strip().upper()
        if not clean_word:
            return False, "Please specify a word to accuse."

        # Truth-locked check:
        # Match if clean_word is in target's secret words AND has not been caught yet
        uncaught_target_words = [w for w in target.secret_words if w not in target.caught_words]
        is_correct = clean_word in uncaught_target_words

        room.active_accusation = {
            "guesser_id": guesser.id,
            "guesser_name": guesser.name,
            "target_id": target.id,
            "target_name": target.name,
            "guessed_word": clean_word,
            "is_correct": is_correct,
            "resolved": False,
            "timestamp": time.time(),
        }
        room.touch()
        room.add_announcement(
            f"⚡ {guesser.name} accused {target.name} of writing '{clean_word}'!",
            "warning",
            highlight=clean_word
        )
        return True, "Accusation submitted to target for truth-locked verification."

    def respond_accusation(self, room_code: str, responder_id: str, response_value: bool) -> Tuple[bool, str, Dict[str, Any]]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found.", {}

        if not room.active_accusation or room.active_accusation.get("resolved"):
            return False, "No pending accusation to answer.", {}

        if room.active_accusation["target_id"] != responder_id:
            return False, "Only the accused player can answer.", {}

        guesser_id = room.active_accusation["guesser_id"]
        target_id = room.active_accusation["target_id"]
        guessed_word = room.active_accusation["guessed_word"]
        actual_is_correct = room.active_accusation["is_correct"]

        # Server-enforced Truth Lock:
        response_value = actual_is_correct

        room.active_accusation["resolved"] = True
        guesser = room.players.get(guesser_id)
        target = room.players.get(target_id)
        guesser_name = guesser.name if guesser else "Guesser"
        target_name = target.name if target else "Target"

        result_payload = {
            "guesser_id": guesser_id,
            "guesser_name": guesser_name,
            "target_id": target_id,
            "target_name": target_name,
            "guessed_word": guessed_word,
            "is_correct": actual_is_correct,
            "game_over": False,
            "winner_name": None,
        }

        if actual_is_correct:
            # Correct Guess!
            if guesser:
                guesser.correct_guesses += 1

            if target:
                if guessed_word not in target.caught_words:
                    target.caught_words.append(guessed_word)

                # Check if all of target's words are caught
                if len(target.caught_words) >= len(target.secret_words):
                    if not target.is_caught:
                        target.is_caught = True
                        target.eliminated_by = guesser_name
                    room.add_announcement(
                        f"💥 BINGO! {target_name} answered YES! '{guessed_word}' was their word. {target_name} is FULLY CAUGHT!",
                        "success"
                    )
                else:
                    remaining = len(target.secret_words) - len(target.caught_words)
                    room.add_announcement(
                        f"💥 BINGO! {target_name} answered YES to '{guessed_word}'! ({remaining} secret word remaining)",
                        "success"
                    )

            # Guesser retains turn!
            room.current_turn_player_id = guesser_id

            # Check Victory Condition:
            uncaught = room.get_uncaught_players()
            if len(uncaught) == 1:
                winner = uncaught[0]
                room.winner_id = winner.id
                room.phase = GamePhase.GAME_OVER
                result_payload["game_over"] = True
                result_payload["winner_name"] = winner.name
                room.add_announcement(f"🏆 {winner.name} is the LAST UNCAUGHT PLAYER and WINS THE GAME!", "victory")
            elif len(uncaught) == 0:
                top_player = max(room.players.values(), key=lambda p: p.correct_guesses)
                room.winner_id = top_player.id
                room.phase = GamePhase.GAME_OVER
                result_payload["game_over"] = True
                result_payload["winner_name"] = top_player.name
                room.add_announcement(f"🏆 Game Over! {top_player.name} wins by deduction points!", "victory")

        else:
            # Wrong Guess!
            room.add_announcement(
                f"❌ {target_name} answered NO to '{guessed_word}'. Turn passes to {target_name}!",
                "error"
            )
            room.current_turn_player_id = target_id

        room.active_accusation = None
        room.touch()
        return True, "Accusation resolved.", result_payload

    def pass_turn(self, room_code: str, player_id: str) -> Tuple[bool, str, Optional[str]]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found.", None

        if room.phase != GamePhase.GUESSING:
            return False, "Can only pass turn during Guessing phase.", None

        if room.current_turn_player_id != player_id:
            return False, "It is not your turn to pass.", None

        other_players = [p.id for p in room.players.values() if p.id != player_id and p.is_connected]
        if not other_players:
            return False, "No other players to pass to.", None

        next_player_id = random.choice(other_players)
        room.current_turn_player_id = next_player_id
        
        current_p = room.players.get(player_id)
        next_p = room.players.get(next_player_id)
        c_name = current_p.name if current_p else "Player"
        n_name = next_p.name if next_p else "Next Player"

        room.touch()
        room.add_announcement(f"⏭️ {c_name} passed turn! Turn randomly given to {n_name}.", "info")
        return True, "Turn passed successfully.", next_player_id

    def call_draw(self, room_code: str, player_id: str) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."

        if room.phase != GamePhase.GUESSING:
            return False, "Can only call draw during Guessing phase."

        if room.current_turn_player_id != player_id:
            return False, "Only the active player can call a draw vote."

        if room.active_draw_vote:
            return False, "A draw vote is already in progress."

        caller = room.players.get(player_id)
        caller_name = caller.name if caller else "Player"

        room.active_draw_vote = {
            "initiator_id": player_id,
            "votes": {player_id: True},
            "timestamp": time.time(),
        }
        room.touch()
        room.add_announcement(f"🤝 {caller_name} called a vote for DRAW! All players must agree.", "warning")
        
        if len(room.players) == 1:
            room.is_draw = True
            room.phase = GamePhase.GAME_OVER
            room.active_draw_vote = None
            room.add_announcement("🤝 Game ended in a DRAW!", "victory")

        return True, "Draw vote initiated."

    def vote_draw(self, room_code: str, player_id: str, agree: bool) -> Tuple[bool, str, bool]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found.", False

        if not room.active_draw_vote:
            return False, "No active draw vote.", False

        voter = room.players.get(player_id)
        voter_name = voter.name if voter else "Player"

        if not agree:
            room.active_draw_vote = None
            room.touch()
            room.add_announcement(f"❌ {voter_name} disagreed to draw. Game continues!", "error")
            return True, "Draw rejected.", False

        room.active_draw_vote["votes"][player_id] = True
        room.touch()

        total_players = len(room.players)
        agreed_count = sum(1 for v in room.active_draw_vote["votes"].values() if v)

        if agreed_count >= total_players:
            room.is_draw = True
            room.phase = GamePhase.GAME_OVER
            room.active_draw_vote = None
            room.add_announcement("🤝 UNANIMOUS! All players agreed to a DRAW!", "victory")
            return True, "Draw unanimously accepted!", True

        return True, f"Voted agree ({agreed_count}/{total_players}).", False

    def play_again_reset(self, room_code: str, player_id: str) -> Tuple[bool, str]:
        room = self.get_room(room_code)
        if not room:
            return False, "Room not found."

        if room.phase != GamePhase.GAME_OVER:
            return False, "Game is not over yet."

        # Purge all secret words and caught words from RAM
        for player in room.players.values():
            player.secret_words.clear()
            player.caught_words.clear()
            player.is_caught = False
            player.correct_guesses = 0
            player.eliminated_by = None

        room.phase = GamePhase.LOBBY
        room.word_sequence = []
        room.mode_chosen_by_host = False
        room.current_turn_player_id = None
        room.active_accusation = None
        room.active_draw_vote = None
        room.winner_id = None
        room.is_draw = False
        room.announcements_history.clear()
        room.touch()
        room.add_announcement("🔄 Match reset! Host can configure mode and players submit new secret words.", "success")
        return True, "Room reset to lobby."

    def player_disconnect(self, room_code: str, player_id: str):
        room = self.get_room(room_code)
        if not room:
            return
        
        player = room.players.get(player_id)
        if player:
            player.is_connected = False
            room.touch()

    def remove_empty_rooms(self, max_idle_seconds: float = 3600):
        now = time.time()
        to_delete = [
            code for code, r in self.rooms.items()
            if (now - r.last_activity > max_idle_seconds and not any(p.is_connected for p in r.players.values()))
        ]
        for code in to_delete:
            del self.rooms[code]
