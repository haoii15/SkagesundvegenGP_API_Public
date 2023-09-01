import pytest
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_team_insert_driver_as_first_driver():
    # client.put("/users/unlink?discord_id=54321")
    # client.put("/users/unlink?discord_id=12345")
    # client.put("/teams/")

    resp = client.post("/teams/testers?discord_id=12345").json()
    assert resp["code"] == 400, resp
    assert resp["error"] == 1, resp

    resp = client.put("/users/link/haoii?discord_id=12345").json()
    resp = client.post("/teams/testers?discord_id=12345").json()
    assert resp["code"] == 200, resp

    resp = client.post("/teams/wrong?discord_id=12345").json()
    assert resp["code"] == 400, resp

    driver = client.get("/users/haoii").json()["detail"]
    team = client.get("/teams/testers").json()["detail"]
    assert team["driver_1"] == driver["driver_id"]
    assert team["team_id"] == driver["team"]

    resp = client.put("/users/link/FLovas?discord_id=54321").json()
    resp = client.put("/teams/join/testers?discord_id=54321").json()
    assert resp["code"] == 200, resp

    driver = client.get("/users/FLovas").json()["detail"]
    team = client.get("/teams/testers").json()["detail"]
    assert driver["team"] == team["team_id"], driver
    assert driver["driver_id"] == team["driver_2"], driver
    assert team["seed"] != None, team

    resp = client.put("/users/link/Ole?discord_id=123").json()
    resp = client.put("/teams/join/testers?discord_id=123").json()
    assert resp["code"] == 400, resp

    resp = client.put("/teams/leave/12345").json()
    assert resp["code"] == 200, resp
    resp = client.put("/teams/leave/54321").json()
    assert resp["code"] == 200, resp

    client.put("/users/unlink?discord_id=123")
    client.put("/users/unlink?discord_id=54321")
    client.put("/users/unlink?discord_id=12345")
    driver = client.get("/users/haoii").json()["detail"]
    assert driver["team"] == None, driver
    assert driver["discord_id"] == None, driver
    driver = client.get("/users/FLovas").json()["detail"]
    assert driver["team"] == None, driver
    assert driver["discord_id"] == None, driver
    team = client.get("/teams/testers").json()
    assert team["code"] == 400, team