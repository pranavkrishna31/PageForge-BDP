import os
from pymongo import MongoClient
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

mongo_client = MongoClient(MONGO_URI)

db = mongo_client["bookapp"]

# =========================
# USERS
# =========================

users = [

    {
        "Username": "pranavkrishna31",
        "Password": "pranav123",
        "Role": "admin"
    }

]

# =========================
# RESET USERS COLLECTION
# =========================

db.users.delete_many({})

db.users.insert_many(users)

print("Seeded admin users into MongoDB Atlas successfully!")