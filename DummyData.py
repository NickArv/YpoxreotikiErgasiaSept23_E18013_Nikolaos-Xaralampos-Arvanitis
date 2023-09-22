from pymongo import MongoClient

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB connection string
db = client["UnipiLibrary"]
books = db["books"]  # Update with your collection name
admin_credentials = db["admins"]
users = db["users"]


# Define dummy data

dummy_users = [
    {
        'username': 'user1',
        'password': 'password1',
        'email': 'user1@example.com',
        'role': 'user',
    },
    {
        'username': 'user2',
        'password': 'password2',
        'email': 'user2@example.com',
        'role': 'user',
    },
    {
        'username': 'user3',
        'password': 'password3',
        'email': 'user3@example.com',
        'role': 'user',
    },
]



dummy_books = [
    {
        "title": "Sample Book 1",
        "author": "Author 1",
        "Publish": "2023-09-13",
        "ISBN": "1234567890",
        "Summary": "This is a sample book 1.",
        "NumberPG": 200,
        "days_available_for_rent": 7,
        "is_available": True,
    },
    {
        "title": "Sample Book 2",
        "author": "Author 2",
        "Publish": "2023-09-14",
        "ISBN": "9876543210",
        "Summary": "This is a sample book 2.",
        "NumberPG": 250,
        "days_available_for_rent": 14,
        "is_available": True,
    },
]

dummy_admins = [
    {
        'username': 'admin1',
        'password': 'password1',
        'email': 'admin1@example.com',
        'role': 'admin',
    },
    {
        'username': 'admin2',
        'password': 'password2',
        'email': 'admin2@example.com',
        'role': 'admin',
    },
    {
        'username': 'admin3',
        'password': 'password3',
        'email': 'admin3@example.com',
        'role': 'admin',
    },
]

# Insert dummy data into the database
for book_data in dummy_books:
    books.insert_one(book_data)

for admin_data in dummy_admins:
    admin_credentials.insert_one(admin_data)

for user_data in dummy_users:
    users.insert_one(user_data)

print("Dummy data inserted successfully.")