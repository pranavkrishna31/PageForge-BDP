from faker import Faker
import random
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

fake = Faker()

genres = [
    "Classics",
    "Fiction",
    "Science",
    "Romance",
    "History",
    "Fantasy",
    "Thriller"
]

# =========================
# BOOK TITLES
# =========================

titles = [
    "The Great Gatsby", "To Kill a Mockingbird", "1984", "Pride and Prejudice", "The Hobbit",
    "The Catcher in the Rye", "Moby Dick", "Harry Potter and the Sorcerer's Stone", "War and Peace",
    "Brave New World", "Crime and Punishment", "The Lord of the Rings", "The Kite Runner",
    "Anna Karenina", "Fahrenheit 451", "Jane Eyre", "Animal Farm", "Dracula", "The Da Vinci Code",
    "Wuthering Heights", "Sense and Sensibility", "Little Women", "The Alchemist", "Don Quixote",
    "Rebecca", "Frankenstein", "The Road", "Great Expectations", "Gone Girl", "Dune", "Beloved",
    "Les Misérables", "The Shining", "Emma", "Catch-22", "Lolita", "The Color Purple",
    "The Scarlett Letter", "Persuasion", "The Sun Also Rises", "White Teeth", "Heart of Darkness",
    "Ulysses", "A Tale of Two Cities", "Slaughterhouse-Five", "Gulliver's Travels", "Middlemarch",
    "Madame Bovary", "The Book Thief", "Bridget Jones's Diary", "Ender's Game", "Watership Down",
    "The Secret Garden", "Life of Pi", "The Goldfinch", "Atonement", "Cloud Atlas", "Oliver Twist",
    "Room", "Gone with the Wind", "Memoirs of a Geisha", "Twilight", "The Lovely Bones",
    "Eat, Pray, Love", "Eragon", "The Help", "The Girl with the Dragon Tattoo", "Outlander",
    "Ready Player One", "The Time Traveler's Wife", "A Prayer for Owen Meany", "It", "Norwegian Wood",
    "The Hunger Games", "The Pillars of the Earth", "Her Fearful Symmetry", "The Fault in Our Stars",
    "The Remains of the Day", "American Gods", "Shantaram", "A Game of Thrones", "Good Omens",
    "The Wind-Up Bird Chronicle", "Never Let Me Go", "The Name of the Rose", "Jonathan Strange & Mr Norrell",
    "The Handmaid's Tale", "Midnight's Children", "Siddhartha", "Zen and the Art of Motorcycle Maintenance",
    "Atlas Shrugged", "On the Road", "The Little Prince", "The Stand", "Infinite Jest",
    "The Bell Jar", "Lord of the Flies", "All the Light We Cannot See"
]

# =========================
# GENERATE BOOKS
# =========================

books = []

for i in range(1, 101):

    books.append({

        "BookID": i,

        "Title": titles[(i - 1) % len(titles)],

        "Author": fake.name(),

        "Genre": random.choice(genres),

        "Description": fake.paragraph(nb_sentences=2),

        "Price": round(random.uniform(199, 499), 2),

        "RatingMean": 0.0,

        "ReviewCount": 0,

        "StockAvailable": random.randint(1, 40),

        "ReorderPoint": random.randint(2, 10),

        "ClickCount": 0,

        "ShowCount": 0,

        "DetailViews": 0

    })

# =========================
# RESET BOOK COLLECTION
# =========================

db.books.delete_many({})

db.books.insert_many(books)

print("Seeded 100 books into MongoDB Atlas successfully!")