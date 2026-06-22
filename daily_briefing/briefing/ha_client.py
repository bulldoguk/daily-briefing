import json

import requests
import websocket


class HomeAssistantClient:
    """Thin wrapper around the HA REST API, plus one WebSocket call.

    REST covers everything except todo items — the todo domain has no REST
    endpoint for reading item contents (HA exposes item lists only via
    service-call response data, which is WebSocket-only). That single call
    is the one deliberate exception to the REST-only pattern used elsewhere
    in this codebase and in jeeves-agent (see daily-briefing SPEC.md).
    """

    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_calendar_events(self, entity_id, start_iso, end_iso):
        resp = requests.get(
            f"{self.base_url}/api/calendars/{entity_id}",
            headers=self.headers,
            params={"start": start_iso, "end": end_iso},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def set_state(self, entity_id, state, attributes=None):
        resp = requests.post(
            f"{self.base_url}/api/states/{entity_id}",
            headers=self.headers,
            json={"state": state, "attributes": attributes or {}},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_todo_items(self, entity_id):
        """Fetch items for a todo list via the WebSocket API (REST has no
        equivalent — see class docstring)."""
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/websocket"

        ws = websocket.create_connection(ws_url, timeout=15)
        try:
            ws.recv()  # auth_required
            ws.send(json.dumps({"type": "auth", "access_token": self.token}))
            auth_resp = json.loads(ws.recv())
            if auth_resp.get("type") != "auth_ok":
                raise RuntimeError(f"WebSocket auth failed: {auth_resp}")

            ws.send(json.dumps({
                "id": 1,
                "type": "call_service",
                "domain": "todo",
                "service": "get_items",
                "target": {"entity_id": entity_id},
                "return_response": True,
            }))
            result = json.loads(ws.recv())
            if not result.get("success"):
                raise RuntimeError(f"todo.get_items failed: {result}")
            return result["result"]["response"][entity_id]["items"]
        finally:
            ws.close()
