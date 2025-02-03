import os
import logging
import gridfs
from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
CORS(app)

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Setup Logging
LOG_FILE = "app.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["life_events_db"]
collection = db["events"]
fs = gridfs.GridFS(db)

logging.info("Flask API started. Connected to MongoDB.")

# Route to create a new event
@app.route("/events", methods=["POST"])
def create_event():
    data = request.json
    event_id = collection.insert_one(data).inserted_id
    logging.info(f"Event created: {event_id} - {data['title']}")
    return jsonify({"message": "Event stored", "event_id": str(event_id)}), 201

# Route to retrieve an event by ID
@app.route("/events/<event_id>", methods=["GET"])
def get_event(event_id):
    logging.info(f"Retrieving event ID: {event_id}")
    event = collection.find_one({"_id": ObjectId(event_id)})
    if event:
        event["_id"] = str(event["_id"])
        logging.info(f"Event found: {event}")
        return jsonify(event), 200
    logging.warning(f"Event not found: {event_id}")
    return jsonify({"error": "Event not found"}), 404

# Route to add a conversation turn to an event
@app.route("/events/<event_id>/conversation", methods=["POST"])
def add_conversation_turn(event_id):
    data = request.json
    question = data.get("question")
    response = data.get("response")

    event = collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        logging.warning(f"Conversation turn failed: Event not found ({event_id})")
        return jsonify({"error": "Event not found"}), 404

    q_and_a = event.get("q_and_a", [])
    next_turn = len(q_and_a) + 1
    q_and_a.append({"turn": next_turn, "question": question, "response": response})

    collection.update_one({"_id": ObjectId(event_id)}, {"$set": {"q_and_a": q_and_a}})
    logging.info(f"Conversation turn added to event {event_id} - Turn {next_turn}")
    return jsonify({"message": "Turn added", "turn": next_turn}), 200

# Route to upload an image
@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        logging.warning("Image upload failed: No file provided.")
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_id = fs.put(file, filename=file.filename)
    logging.info(f"Image uploaded: {file.filename} (ID: {file_id})")
    return jsonify({"message": "Image stored", "file_id": str(file_id)}), 201

# Route to retrieve an image by ID
@app.route("/image/<file_id>", methods=["GET"])
def get_image(file_id):
    try:
        file_data = fs.get(ObjectId(file_id))
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], file_data.filename)
        with open(output_path, "wb") as f:
            f.write(file_data.read())
        logging.info(f"Image retrieved: {file_id} ({file_data.filename})")
        return send_file(output_path, mimetype="image/jpeg")
    except gridfs.errors.NoFile:
        logging.error(f"Image not found: {file_id}")
        return jsonify({"error": "File not found"}), 404

# Route to search events by keyword
@app.route("/events/search", methods=["GET"])
def search_events():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify({"error": "Keyword required"}), 400

    query = {
        "$or": [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"summary": {"$regex": keyword, "$options": "i"}},
            {"tags": {"$in": [keyword]}}
        ]
    }

    results = list(collection.find(query))
    for event in results:
        event["_id"] = str(event["_id"])

    return jsonify(results), 200

# Route to retrieve API logs
@app.route("/logs", methods=["GET"])
def get_logs():
    level_filter = request.args.get("level", "").upper()
    limit = int(request.args.get("limit", 100))

    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "Log file not found"}), 404

    try:
        logs = []
        with open(LOG_FILE, "r") as f:
            for line in reversed(f.readlines()):
                if level_filter and level_filter not in line:
                    continue
                logs.append(line.strip())
                if len(logs) >= limit:
                    break
        return jsonify({"logs": logs}), 200
    except Exception as e:
        logging.error(f"Error reading logs: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to retrieve logs"}), 500

# Error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"error": "An unexpected error occurred"}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

# Instructions for running the API
# Run the API with:
# $ python api.py
# The API will be available at http://localhost:5000.
# You can test the API using the provided Postman collection.
# The API logs are stored in app.log.
# The MongoDB database is named life_events_db and the collection is events.
# The GridFS bucket is used to store images.
# The uploads folder is used to store images temporarily.
# The API provides the following endpoints:
# POST /events: Create a new event.
# GET /events/<event_id>: Retrieve an event by ID.
# POST /events/<event_id>/conversation: Add a conversation turn to an event.
# POST /upload: Upload an image.
# GET /image/<file_id>: Retrieve an image by ID.
# GET /events/search: Search events by keyword.
# GET /logs: Retrieve API logs.
# The API uses logging to log events and errors.
# The API handles exceptions and logs them.
# The API uses CORS to allow cross-origin requests.
