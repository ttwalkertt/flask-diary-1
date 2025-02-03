import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"
TEST_IMAGES = [f"test-image-{i}.jpg" for i in range(1, 6)]

def test_create_event():
    """Test creating a new life event."""
    event_data = {
        "title": "Test Event",
        "date_of_event": "2025-02-03",
        "location": "Test Location",
        "story_type": "Test Type",
        "importance_rating": 5,
        "participants": [{"name": "Alice", "relationship": "Friend"}],
        "q_and_a": [],
        "summary": "This is a test event.",
        "tags": ["test", "event"]
    }
    response = requests.post(f"{BASE_URL}/events", json=event_data)
    assert response.status_code == 201, f"Unexpected response: {response.text}"
    event_id = response.json()["event_id"]
    print(f"✅ Created event with ID: {event_id}")
    return event_id

def test_get_event(event_id):
    """Test retrieving a life event."""
    response = requests.get(f"{BASE_URL}/events/{event_id}")
    assert response.status_code == 200, f"Unexpected response: {response.text}"
    print(f"✅ Retrieved event: {json.dumps(response.json(), indent=2)}")

def test_add_conversation_turn(event_id):
    """Test adding conversation turns."""
    for i in range(1, 4):
        data = {"question": f"Test Question {i}?", "response": f"Test Response {i}."}
        response = requests.post(f"{BASE_URL}/events/{event_id}/conversation", json=data)
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        print(f"✅ Added conversation turn {i}")

def test_upload_images():
    """Test uploading multiple images."""
    image_ids = []
    for img in TEST_IMAGES:
        with open(img, "rb") as f:
            response = requests.post(f"{BASE_URL}/upload", files={"file": f})
            assert response.status_code == 201, f"Unexpected response: {response.text}"
            file_id = response.json()["file_id"]
            image_ids.append(file_id)
            print(f"✅ Uploaded image {img}, File ID: {file_id}")
        time.sleep(1)  # Small delay to avoid rapid-fire requests
    return image_ids

def test_get_images(image_ids):
    """Test retrieving uploaded images."""
    for file_id in image_ids:
        response = requests.get(f"{BASE_URL}/image/{file_id}")
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        print(f"✅ Retrieved image with File ID: {file_id}")

def test_search_events():
    """Test searching for events."""
    response = requests.get(f"{BASE_URL}/events/search?q=test")
    assert response.status_code == 200, f"Unexpected response: {response.text}"
    results = response.json()
    print(f"✅ Found {len(results)} events matching 'test'")

def test_get_logs():
    """Test retrieving logs."""
    response = requests.get(f"{BASE_URL}/logs?limit=10")
    assert response.status_code == 200, f"Unexpected response: {response.text}"
    logs = response.json()["logs"]
    print(f"✅ Retrieved logs:\n" + "\n".join(logs))

# ------ RUN TESTS ------
if __name__ == "__main__":
    print("\n🛠 Running API tests...\n")
    
    event_id = test_create_event()
    time.sleep(1)  # Ensure event is written before retrieval
    test_get_event(event_id)
    test_add_conversation_turn(event_id)

    image_ids = test_upload_images()
    time.sleep(2)  # Ensure images are stored before retrieval
    test_get_images(image_ids)

    test_search_events()
    test_get_logs()

    print("\n✅ All tests completed successfully!")