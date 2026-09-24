"""
Automated Unit Tests for KATCHO (Including 1 vs 2 Words Mode)
"""

import unittest
from game_manager import GameManager, GamePhase
from main import get_local_ip, generate_qr_base64


class TestKatchoGameManager(unittest.TestCase):

    def setUp(self):
        self.gm = GameManager()

    def test_room_creation_and_joining(self):
        room, host = self.gm.create_room("Alice", "p_alice")
        self.assertIsNotNone(room)
        self.assertEqual(len(room.code), 4)
        self.assertEqual(host.name, "Alice")
        self.assertTrue(host.is_host)
        self.assertEqual(room.phase, GamePhase.LOBBY)

        room, bob, err = self.gm.join_room(room.code, "Bob", "p_bob")
        self.assertIsNotNone(bob)
        self.assertEqual(bob.name, "Bob")
        self.assertFalse(bob.is_host)
        self.assertEqual(len(room.players), 2)
        self.assertNotEqual(host.color, bob.color)

    def test_mode_selection_for_under_7_players(self):
        room, host = self.gm.create_room("Alice", "p_alice")
        self.gm.join_room(room.code, "Bob", "p_bob")
        self.gm.submit_secret_words(room.code, "p_alice", ["ALPHA"])
        self.gm.submit_secret_words(room.code, "p_bob", ["BRAVO"])

        # Attempt to start without choosing mode when players < 7
        ok, reason, _ = self.gm.start_reveal_phase(room.code, "p_alice")
        self.assertFalse(ok)
        self.assertEqual(reason, "PROMPT_MODE_SELECTION")

        # Host chooses 2 words mode
        ok_mode, _ = self.gm.set_word_mode(room.code, "p_alice", 2)
        self.assertTrue(ok_mode)
        self.assertEqual(room.words_per_player, 2)
        self.assertTrue(room.mode_chosen_by_host)

    def test_double_word_mode_gameplay_and_deduction(self):
        room, _ = self.gm.create_room("Alice", "p_alice")
        self.gm.join_room(room.code, "Bob", "p_bob")
        self.gm.join_room(room.code, "Charlie", "p_charlie")

        # Set 2 words per player
        self.gm.set_word_mode(room.code, "p_alice", 2)

        # Submit 2 words each
        self.gm.submit_secret_words(room.code, "p_alice", ["APPLE", "ASTRONAUT"])
        self.gm.submit_secret_words(room.code, "p_bob", ["BANANA", "BOAT"])
        self.gm.submit_secret_words(room.code, "p_charlie", ["CHERRY", "CASTLE"])

        # Start reveal
        ok, _, seq = self.gm.start_reveal_phase(room.code, "p_alice")
        self.assertTrue(ok)
        self.assertEqual(len(seq), 6) # 3 players * 2 words = 6 words
        self.assertIn("ASTRONAUT", seq)
        self.assertIn("BOAT", seq)

        self.gm.finish_reveal_phase(room.code)
        self.assertEqual(room.phase, GamePhase.GUESSING)

        room.current_turn_player_id = "p_alice"

        # Alice accuses Bob of BANANA (Bob's 1st word)
        ok_acc, _ = self.gm.make_accusation(room.code, "p_alice", "p_bob", "BANANA")
        self.assertTrue(ok_acc)
        self.assertTrue(room.active_accusation["is_correct"])

        # Bob responds YES
        ok_res, _, res = self.gm.respond_accusation(room.code, "p_bob", True)
        self.assertTrue(ok_res)
        self.assertIn("BANANA", room.players["p_bob"].caught_words)
        self.assertFalse(room.players["p_bob"].is_caught) # Still has BOAT!
        self.assertEqual(room.players["p_alice"].correct_guesses, 1)
        self.assertEqual(room.current_turn_player_id, "p_alice") # Alice keeps turn

        # Alice accuses Bob of BOAT (Bob's 2nd word) -> Bob is now FULLY CAUGHT!
        self.gm.make_accusation(room.code, "p_alice", "p_bob", "BOAT")
        self.gm.respond_accusation(room.code, "p_bob", True)
        self.assertTrue(room.players["p_bob"].is_caught)
        self.assertEqual(room.players["p_bob"].eliminated_by, "Alice")
        self.assertEqual(room.players["p_alice"].correct_guesses, 2)

    def test_single_word_mode_flow(self):
        room, _ = self.gm.create_room("Alice", "p_alice")
        self.gm.join_room(room.code, "Bob", "p_bob")
        self.gm.set_word_mode(room.code, "p_alice", 1)

        self.gm.submit_secret_words(room.code, "p_alice", ["SUN"])
        self.gm.submit_secret_words(room.code, "p_bob", ["MOON"])

        self.gm.start_reveal_phase(room.code, "p_alice")
        self.gm.finish_reveal_phase(room.code)

        room.current_turn_player_id = "p_alice"

        # Alice wrongly accuses Bob of STAR
        self.gm.make_accusation(room.code, "p_alice", "p_bob", "STAR")
        self.gm.respond_accusation(room.code, "p_bob", False)

        # Turn transfers to Bob
        self.assertEqual(room.current_turn_player_id, "p_bob")

        # Bob correctly accuses Alice of SUN -> Game Over, Bob wins!
        self.gm.make_accusation(room.code, "p_bob", "p_alice", "SUN")
        _, _, res = self.gm.respond_accusation(room.code, "p_alice", True)
        self.assertTrue(res["game_over"])
        self.assertEqual(res["winner_name"], "Bob")
        self.assertEqual(room.phase, GamePhase.GAME_OVER)

    def test_play_again_memory_purge(self):
        room, _ = self.gm.create_room("Alice", "p_alice")
        self.gm.join_room(room.code, "Bob", "p_bob")
        self.gm.set_word_mode(room.code, "p_alice", 1)
        self.gm.submit_secret_words(room.code, "p_alice", ["DOG"])
        self.gm.submit_secret_words(room.code, "p_bob", ["CAT"])
        self.gm.start_reveal_phase(room.code, "p_alice")
        self.gm.finish_reveal_phase(room.code)

        room.current_turn_player_id = "p_alice"
        self.gm.make_accusation(room.code, "p_alice", "p_bob", "CAT")
        self.gm.respond_accusation(room.code, "p_bob", True)

        self.gm.play_again_reset(room.code, "p_alice")
        self.assertEqual(room.phase, GamePhase.LOBBY)
        self.assertEqual(len(room.players["p_alice"].secret_words), 0)
        self.assertEqual(len(room.players["p_bob"].secret_words), 0)
        self.assertFalse(room.players["p_bob"].is_caught)


if __name__ == "__main__":
    unittest.main()
