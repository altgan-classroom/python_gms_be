"""Read-after-write check against a running stack: a row created by one request must be
visible to every later request. Run: python3 scripts/check_read_after_write.py"""
import json
import time
import urllib.request

AUTH = "http://localhost:5004/api/v1.1"
LOCATION_ID = 43


def call(method, url, token=None, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as res:
        return json.load(res)


token = call("POST", f"{AUTH}/auth/login", body={"email": "owner@demo.gym", "password": "Test@1234"})["data"]["access_token"]
rooms_url = f"{AUTH}/admin/locations/{LOCATION_ID}/rooms"

# Touch every worker thread first so each holds a session from before the write.
for _ in range(20):
    call("GET", rooms_url, token)

name = f"check-{time.time_ns()}"
assert call("POST", rooms_url, token, {"location_id": LOCATION_ID, "name": name})["status"] == "CREATED"

misses = 0
room_id = None
for _ in range(20):
    data = call("GET", rooms_url, token)["data"] or []
    room_id = next((r["room_id"] for r in data if r["name"] == name), None) or room_id
    if not any(r["name"] == name for r in data):
        misses += 1

if room_id:
    call("DELETE", f"{rooms_url}/{room_id}", token)
print(f"{misses}/20 list calls did not see the room created just before them")
assert misses == 0, "stale read"
