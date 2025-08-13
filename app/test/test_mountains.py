from fastapi.testclient import TestClient

from app.main import app

RIDGE_SLUG = "chernogora"
PEAK_SLUG = "bliznitsa"
ROUTE_SLUG = "bliznitsa-iz-vostochnogo-tsirka"

client = TestClient(app)


def test_read_ridges():
    response = client.get("/mountains/ridges")
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["peaks_list"]


def test_read_ridge():
    response = client.get(f"/mountains/ridge/{RIDGE_SLUG}")
    assert response.status_code == 200
    data = response.json()

    assert data
    assert data["slug"]
    assert data["peaks_list"]


def test_read_ridge_peaks():
    response = client.get(f"/mountains/ridge/peaks/{RIDGE_SLUG}")
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["name"]


def test_read_peaks():
    response = client.get("/mountains/peaks")
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["name"]


def test_search_peaks():
    response = client.get("/mountains/peaks/search", params={"q": "hov"})
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["name"]


def test_read_peak_routes():
    response = client.get(f"/mountains/peak/routes/{PEAK_SLUG}")
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["name"]


def test_read_peak():
    response = client.get(f"/mountains/peak/{PEAK_SLUG}")
    assert response.status_code == 200
    data = response.json()

    assert data["slug"]
    assert data["name"]


def test_read_routes():
    response = client.get("/mountains/routes")
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["name"]
    assert item["difficulty"]


def test_search_routes():
    response = client.get("/mountains/routes/search", params={"q": "bliz"})
    assert response.status_code == 200
    data = response.json()

    assert len(data)
    item = data[0]
    assert item["slug"]
    assert item["name"]
    assert item["difficulty"]


def test_read_route():
    response = client.get(f"/mountains/route/{ROUTE_SLUG}")
    assert response.status_code == 200
    data = response.json()

    assert data
    assert data["slug"]
    assert data["peak_id"]
    assert data["sections_list"]
