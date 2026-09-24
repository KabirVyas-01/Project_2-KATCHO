"""
Integration tests for FastAPI endpoints and WebSockets in KATCHO.
"""

import unittest
from fastapi.testclient import TestClient
from main import app


class TestKatchoServer(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_index_page_serves_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("KATCHO", response.text)
        self.assertIn("Created by KABIR VYAS", response.text)

    def test_lan_info_endpoint(self):
        response = self.client.get("/api/lan-info?port=8000")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("local_ip", data)
        self.assertIn("lan_url", data)
        self.assertIn("qr_data_url", data)
        self.assertTrue(data["qr_data_url"].startswith("data:image/png;base64,"))
        self.assertEqual(data["author"], "KABIR VYAS")

    def test_websocket_create_and_join_flow(self):
        with self.client.websocket_connect("/ws/NEW/p_host") as ws_host:
            ws_host.send_json({"action": "create_room", "name": "HostPlayer"})
            resp = ws_host.receive_json()
            self.assertEqual(resp["type"], "state_update")
            room_code = resp["state"]["room_code"]
            self.assertTrue(len(room_code) >= 4)
            self.assertTrue(resp["state"]["is_host"])

            with self.client.websocket_connect(f"/ws/{room_code}/p_guest") as ws_guest:
                init_resp = ws_guest.receive_json()
                self.assertEqual(init_resp["type"], "state_update")

                ws_guest.send_json({"action": "join_room", "room_code": room_code, "name": "GuestPlayer"})
                resp_guest = ws_guest.receive_json()
                self.assertEqual(resp_guest["type"], "state_update")
                self.assertEqual(resp_guest["state"]["total_players"], 2)

                # Set word mode to 1
                ws_host.send_json({"action": "set_word_mode", "words_per_player": 1})

                # Submit words
                ws_host.send_json({"action": "submit_word", "words": ["DIAMOND"]})
                ws_guest.send_json({"action": "submit_word", "words": ["EMERALD"]})

                resp_after_submit = ws_guest.receive_json()
                self.assertEqual(resp_after_submit["type"], "state_update")


if __name__ == "__main__":
    unittest.main()
