import pytest
from fastapi.testclient import TestClient
from main import app  
from sql_app import crud
from sql_app.database import get_db

client = TestClient(app)

def test_link_existing_user_driver():
    resp = client.put("/users/link/haoii?discord_id=12345").json()
    assert resp["code"] == 200

def test_link_existing_user_driver_already_linked():
    resp = client.put("/users/link/haoii?discord_id=123").json()
    assert resp["code"] == 400
    assert resp["error"] == 2

def test_link_existing_user_driver_other_disc():
    resp = client.put("/users/link/Ole?discord_id=12345").json()
    assert resp["code"] == 400
    assert resp["error"] == 1

def test_unlink_existing_user_driver():
    resp = client.put("/users/unlink?discord_id=12345").json()
    assert resp["code"] == 200

def test_link_nonexisting_user_driver():
    resp = client.put("/users/link/the_tester?discord_id=54321").json()
    assert resp["code"] == 200

def test_unlink_nonexisting_user_driver():
    resp = client.put("/users/unlink?discord_id=54321").json()
    assert resp["code"] == 200

def test_delete_driver():
    resp = client.post("/users/delete/the_tester").json()
    assert resp["code"] == 200
