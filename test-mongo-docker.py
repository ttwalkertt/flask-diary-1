from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Replace 'localhost' with the Docker container's IP if it's not on the host machine
mongo_host = "localhost"
mongo_port = 27017  # Default MongoDB port

try:
    # Connect to MongoDB
    client = MongoClient(mongo_host, mongo_port, serverSelectionTimeoutMS=5000)  # 5-second timeout
    
    # Ping the server to check the connection
    client.admin.command('ping')
    
    print("MongoDB is running and accessible!")

except ServerSelectionTimeoutError:
    print("Failed to connect to MongoDB. Ensure the container is running.")

