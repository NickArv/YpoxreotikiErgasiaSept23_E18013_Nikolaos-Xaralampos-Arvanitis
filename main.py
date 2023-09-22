from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
from datetime import datetime, timedelta
from bson.json_util import ObjectId, dumps
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response , session
import json
import uuid
import time
from array import *
import collections
from collections import defaultdict

# Encoder to export object-id for the elements inside mongodb
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

# Initiate Flask App
app = Flask(__name__)
app.json_encoder = MyEncoder
app.config['JSON_SORT_KEYS'] = True

# Set the secret key for sessions
app.secret_key = '12345'

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017")
db = client["UnipiLibrary"]
users = db["users"]
book = db["books"]
reservations = db["reservations"]
admin_credentials = db["admins"]



# Encoder to export book-ISBN for the elements inside mongodb
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)
# Session for simple users
users_sessions = {}


# Create sessions for simple users
def create_session(user_title):
    user_uuid = str(uuid.uuid1())  # 37 characters wide string
    users_sessions[user_uuid] = (user_title, time.time())
    return user_uuid


def is_session_valid(user_uuid):
    return user_uuid in users_sessions


# Session for Administrators
admins_sessions = {}


# Create sessions for Admins
def create_admin_session(admin_title):
    admin_uuid = str(int(uuid.uuid1()))  # 39 digit number displayed as string
    admins_sessions[admin_uuid] = (admin_title, time.time())
    return admin_uuid


def admin_session_valid(admin_uuid):
    return admin_uuid in admins_sessions



# User Creation
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("Bad JSON content", status=400, mimetype='application/json')

    if not data.get("email") or not data.get("password") or not data.get("title"):
        return Response("Incomplete information", status=400, mimetype="application/json")

    # Check if a user with the same email exists
    existing_user = users.find_one({"email": data["email"]})

    if existing_user:
        return Response("User with this email already exists", status=400, mimetype="application/json")

    # Create a new user document
    user = {
        "email": data['email'],
        "Firsttitle": data.get('Firsttitle'),
        "Lasttitle": data.get('Lasttitle'),
        "DateBirth": data.get('DateBirth'),
        "password": data['password'],
        "author": "Simple User"
    }

    # Insert the new user data into MongoDB
    result = users.insert_one(user)

    if result.inserted_id:
        return jsonify("User created successfully."), 201
    else:
        return Response("Failed to create user", status=500, mimetype='application/json')


# Login in us User
@app.route('/login', methods=['POST'])
def login():
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content ", status=500, mimetype='application/json')

    if data is None:
        return Response("bad request", status=500, mimetype='application/json')

    if not "email" in data or not "password" in data:
        return Response("Information incomplete", status=400, mimetype="application/json")

    # Use count_documents to count documents matching the query
    user_count = users.count_documents(
        {'$and': [{"email": data["email"]}, {"password": data["password"]}, {"author": "Simple User"}]})

    if user_count != 0:
        user_uuid = create_session(data['email'])
        res = {"uuid": user_uuid, "email": data['email']}
        global user_email
        user_email = data['email']

        # Set user as logged in
        session['user_logged_in'] = True

        return Response(json.dumps(res), status=200, mimetype='application/json')
    else:
        return Response("Wrong email or password.", status=400, mimetype='application/json')

def is_user_logged_in():
    # Check if the 'user_email' key is in the session
    return 'user_email' in session

# User Logout
@app.route('/logout', methods=['POST'])
def logout():
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("Bad JSON content", status=500, mimetype='application/json')

    if data is None:
        return Response("Bad request", status=500, mimetype='application/json')

    # Get the user's UUID from the request
    user_uuid = data.get('uuid')

    if user_uuid:
        # Check if the user is in the user_sessions dictionary
        if user_uuid in users_sessions:
            # Clear the user's session by removing the session data
            session.clear()
            # Remove the user's session from the user_sessions dictionary
            del users_sessions[user_uuid]
            return Response("User logged out successfully", status=200, mimetype='application/json')
        else:
            return Response("User not found or already logged out", status=400, mimetype='application/json')
    else:
        return Response("Invalid request data", status=400, mimetype='application/json')


# Search for a book
@app.route('/getbook', methods=['GET'])
def get_book(book=None):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    uuid = request.headers.get('Authorization')
    if is_session_valid(uuid) == False:
        return Response("User was not authedicated ", status=401, mimetype='application/json')
    if is_session_valid(uuid) == True:
        print(
            "You can search a book with the following  options: \n 1:Search via the title of the book \n 2:Search via the book's author \n 3:Search via the book Publish day \n 4:Search via the book ISBN \n or you can view everything")
        # User choice(user input)
        # Check if user applies more that one fields during search (only one available at a time!)
        if "title" in data and "ISBN" in data and "author" in data:
            return Response("Please search with one of the three options every time at once: title or ISBN or author",
                            status=400, mimetype="application/json")
        if "title" in data and "ISBN" in data:
            return Response("Please search with one of the three options every time at once: title or ISBN or author",
                            status=400, mimetype="application/json")
        if "ISBN" in data and "author" in data:
            return Response("Please search with one of the three options every time at once: title or ISBN or author",
                            status=400, mimetype="application/json")
        if "title" in data and "author" in data:
            return Response("Please search with one of the three options every time at once: title or ISBN or author",
                            status=400, mimetype="application/json")
        # Search by title
        if "title" in data:
            book = book.find({"title": data["title"]})
            if book != None:
                book = []
                for i in book:
                    book.append(i)
                return jsonify(book)
            if book == None:
                return Response("No book found with that title", status=400, mimetype='application/json')
        # Search by author
        if "author" in data:
            book = book.find({"author": data["author"]})
            if book != None:
                book = []
                for i in book:
                    book.append(i)
                return jsonify(book)
            if book == None:
                return Response("No book found by this author", status=400, mimetype='application/json')
        # Search by ISBN
        if "ISBN" in data:
            book = book.find_one({"ISBN": ObjectId(data["ISBN"])})
            if book != None:
                book = {'title': book["title"], 'description': book["description"], 'price': book["price"],
                           'author': book["author"], 'ISBN': str(book["ISBN"])}
                return Response(json.dumps(book), status=200, mimetype='application/json')
            if book == None:
                return Response("No book found by that ID", status=400, mimetype="application/json")
        if "title" in data and "ISBN" in data and "author" in data:
            return Response(
                json.dumps("Plase search with one of the three options every time at once: title or ISBN or author"),
                status=400, mimetype="application/json")
            # Search by Published day
        if "Publish" in data:
                book = book.find({"Publish": data["Publish"]})
                if book != None:
                    book = []
                    for i in book:
                        book.append(i)
                    return jsonify(book)
                if book == None:
                    return Response("No book found with this published day", status=400, mimetype='application/json')

    # Create a route to fetch and display all available books
    @app.route('/viewBooks', methods=['GET'])
    def view_books():
        books_list = []  # Initialize an empty list to store book information


        all_books = db['Books'].find({})

        # Loop through the retrieved books and append them to the books_list
        for book in all_books:
            book_info = dict(title=book['title'], author=book['author'], ISBN=book['ISBN'], Publish=book['Publish'],
                             NumberPG=book['NumberPG'])

            books_list.append(book_info)

        # Check if any books were found
        if len(books_list) > 0:
            return jsonify(books_list)  # Return the list of books as JSON response
        else:
            return Response("No books found in the database", status=404, mimetype='application/json')

# Display book details based on a unique ISBN
@app.route('/viewBookISBN/<string:ISBN>', methods=['GET'])
def view_book(ISBN):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    # Search for the book in the database using the provided ISBN
    book = db['Books'].find_one({'ISBN': ISBN})

    if book:
        # If the book is found, return its details
        book_info = {
            'title': book['title'],
            'author': book['author'],
            'ISBN': book['ISBN'],
            'available_for_reservation': book['available_for_reservation'],
            'reservation_days': book['reservation_days'],
            'summary': book['summary']
        }
        return jsonify(book_info)
    else:
        # If the book is not found, return an error message
        return Response("The book was not found with the given ISBN.", status=404, mimetype='application/json')



#  booking a book by ISBN
@app.route('/reserveBook', methods=['POST'])
def reserve_book(ISBN):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    # Parse user-provided data from the request
    data = request.json
    if not data:
        return Response("Bad request. Please provide user information in JSON format.", status=400, mimetype='application/json')

    # Extract user information
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    reservation_days = data.get('reservation_days', 3)  # Default to 3 days if not specified

    # Check if the ISBN exists in the database
    book = db['Books'].find_one({'ISBN': ISBN})
    if not book:
        return Response(f"Book with ISBN {ISBN} not found.", status=404, mimetype='application/json')

    # Check if the book is available for the specified days
    if not is_book_available_for_days(ISBN, reservation_days):
        return Response(f"Book with ISBN {ISBN} is not available for {reservation_days} days.", status=400, mimetype='application/json')

    # Check if the book is currently available
    if not is_book_available(ISBN):
        return Response(f"Book with ISBN {ISBN} is currently unavailable.", status=400, mimetype='application/json')

    # Generate a unique reservation code using UUID
    reservation_code = str(uuid.uuid4())  # Generate a random UUID as the reservation code

    # Calculate the reservation end date based on the current date
    reservation_end_date = datetime.now() + datetime.timedelta(days=reservation_days)

    # Create a reservation record
    reservation = {
        'reservation_code': reservation_code,
        'ISBN': ISBN,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'reservation_end_date': reservation_end_date
    }

    # Store the reservation in the database
    db['Reservations'].insert_one(reservation)

    # Mark the book as unavailable
    mark_book_as_unavailable(ISBN)

    # Return a success response
    return Response(f"Book reserved successfully. Reservation Code: {reservation_code}", status=200, mimetype='application/json')

# Function to check if a book is available for the specified days
def is_book_available_for_days(ISBN, reservation_days):
    # Get the book's available days from the database
    book = db['Books'].find_one({'ISBN': ISBN})
    if not book:
        return False

    available_days = book.get('available_days', 0)

    # Check if the book can be reserved for the specified duration
    return available_days >= reservation_days

# Function to check if a book is currently available
def is_book_available(ISBN):
    book = db['Books'].find_one({'ISBN': ISBN})
    if not book:
        return False

    return book.get('is_available', False)

# Function to mark a book as unavailable
def mark_book_as_unavailable(ISBN):
    db['Books'].update_one({'ISBN': ISBN}, {'$set': {'is_available': False}})

# Function to mark a book as available
def mark_book_as_available(ISBN):
    db['Books'].update_one({'ISBN': ISBN}, {'$set': {'is_available': True}})

# Endpoint to display reservations for a specific user
@app.route('/userReservations/<string:user_email>', methods=['GET'])
def user_reservations(user_email):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    reservations = db['Reservations'].find({"user_email": user_email})

    if reservations.count() == 0:
        return Response("No reservations found for this user", status=404, mimetype='application/json')

    reservation_list = []
    for reservation in reservations:
        book = db['Books'].find_one({"ISBN": reservation['book_ISBN']})
        if book:
            reservation_info = {
                "book_title": book['title'],
                "book_author": book['author'],
                "reservation_date": reservation['reservation_date'],
                "return_date": reservation['return_date'],
                "status": reservation['status'],
            }
            reservation_list.append(reservation_info)

    return jsonify(reservation_list)

# Create a route to fetch and display reservation details by reservation code
@app.route('/getReservation/<string:reservation_code>', methods=['GET'])
def get_reservation(reservation_code):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    # Query the database to find the reservation by its unique code
    reservation = reservations.find_one({"code": reservation_code})

    # Check if the reservation exists
    if reservation is None:
        return Response("Reservation not found", status=404, mimetype='application/json')

    # Calculate the return date based on the reservation date and number of days
    reservation_date = datetime.strptime(reservation['reservation_date'], '%Y-%m-%d')
    return_date = reservation_date + timedelta(days=reservation['days_to_return'])

    # Construct the reservation details
    reservation_details = {
        "title": reservation['book_title'],
        "author": reservation['book_author'],
        "publish_date": reservation['book_publish_date'],
        "ISBN": reservation['book_ISBN'],
        "reservation_date": reservation['reservation_date'],
        "return_date": return_date.strftime('%Y-%m-%d'),
        "days_to_return": reservation['days_to_return']
    }

    return jsonify(reservation_details)  # Return the reservation details as JSON response

# Return a reserved book by unique reservation code
@app.route('/returnBook/<string:reservation_code>', methods=['POST'])
def return_book(reservation_code):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    # Check if the reservation code exists in the database
    reservation = db['Reservations'].find_one({'reservation_code': reservation_code})

    if not reservation:
        return Response(f"Reservation with code {reservation_code} not found.", status=404, mimetype='application/json')

    # Extract ISBN and reservation end date from the reservation
    ISBN = reservation['ISBN']
    reservation_end_date = reservation['reservation_end_date']

    # Check if the book is already returned
    if 'return_date' in reservation:
        return Response(f"Book with ISBN {ISBN} is already returned.", status=400, mimetype='application/json')

    # Calculate the current date
    current_date = datetime.now()

    # Check if the book is overdue
    if current_date > reservation_end_date:
        return Response(f"Book with ISBN {ISBN} is overdue. Please return it immediately.", status=400, mimetype='application/json')

    # Update the reservation record with the return date
    reservation['return_date'] = current_date

    # Mark the book as available in the database
    mark_book_as_available(ISBN)

    # Update the reservation record in the database
    db['Reservations'].update_one({'reservation_code': reservation_code}, {'$set': reservation})

    # Return a success response
    return Response(f"Book with ISBN {ISBN} returned successfully.", status=200, mimetype='application/json')

# Delete user account by user ID
@app.route('/deleteUser/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not is_user_logged_in():
        return Response("Unauthorized. Please log in .", status=401, mimetype='application/json')
    # Check if the user ID exists in the database
    user = db['Users'].find_one({'user_id': user_id})

    if not user:
        return Response(f"User with ID {user_id} not found.", status=404, mimetype='application/json')

    # Delete the user record from the database
    db['Users'].delete_one({'user_id': user_id})

    # Return a success response
    return Response(f"User with ID {user_id} has been deleted successfully.", status=200, mimetype='application/json')



########### ADMIN SECTION ################


# Function to check administrator credentials
def is_valid_admin(email, password):
    return email == admin_credentials['email'] and password == admin_credentials['password']
# Admin login route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if not data:
        return Response("Bad request. Please provide administrator credentials in JSON format.", status=400, mimetype='application/json')

    email = data.get('email', '')
    password = data.get('password', '')

    if email in admin_credentials and admin_credentials[email] == password:
        # Set the admin session when login is successful
        session['admin_logged_in'] = True
        return Response("Administrator login successful.", status=200, mimetype='application/json')
    else:
        return Response("Invalid administrator credentials. Please try again.", status=401, mimetype='application/json')


# Administrator logout route
@app.route('/admin/logout', methods=['GET'])
def admin_logout():
    # Clear the session for the admin user
    session.clear()

    # Redirect the admin to the login page or any other page
    return redirect ('/admin/login')

# Define a function to check if the admin is logged in
def is_admin_logged_in():
    return session.get('admin_logged_in', False)


# Administrator route to add a new book
@app.route('/admin/add_book', methods=['POST'])
def add_book():
    if not is_admin_logged_in():
        return Response("Unauthorized. Please log in as an administrator.", status=401, mimetype='application/json')

    data = request.json
    if not data:
        return Response("Bad request. Please provide book details in JSON format.", status=400, mimetype='application/json')

    # Extract book details from the JSON request
    title = data.get('title', '')
    author = data.get('author', '')
    publish_date = data.get('publish_date', '')
    ISBN = data.get('ISBN', '')
    summary = data.get('summary', '')
    num_pages = data.get('num_pages', 0)  # Default to 0 pages if not specified
    loan_days = data.get('loan_days', 7)  # Default to 7 days if not specified

    # Create a new Book object
    new_book = book(title, author, publish_date, ISBN, summary, num_pages, loan_days)

    # Add the new book to the database
    db["books"].append(new_book)

    return Response("Book added successfully.", status=200, mimetype='application/json')

# Administrator route to update loan days of a book by ISBN
@app.route('/admin/update_loan_days/<string:ISBN>', methods=['POST'])
def update_loan_days(ISBN):
    if not is_admin_logged_in():
        return Response("Unauthorized. Please log in as an administrator.", status=401, mimetype='application/json')

    data = request.json
    if not data:
        return Response("Bad request. Please provide new loan days in JSON format.", status=400, mimetype='application/json')

    new_loan_days = data.get('loan_days', 7)  # Default to 7 days if not specified

    # Check if the book with the provided ISBN exists in the database
    found_book = None
    for book in db["books"]:
        if book.ISBN == ISBN:
            found_book = book
            break

    if found_book is None:
        return Response(f"Book with ISBN {ISBN} not found.", status=404, mimetype='application/json')

    # Check if the book is currently available for reservation
    if not is_book_available(ISBN):
        return Response(f"Book with ISBN {ISBN} is currently unavailable for updating loan days.", status=400, mimetype='application/json')

    # Update the loan days of the book
    found_book.loan_days = new_loan_days

    return Response(f"Loan days for book with ISBN {ISBN} updated successfully.", status=200, mimetype='application/json')


def is_book_reserved(ISBN):
    # Check if there are any reservations for the book with the given ISBN
    reservation = db['Reservations'].find_one({'ISBN': ISBN})

    # If a reservation is found, the book is reserved; otherwise, it's not
    return reservation is not None


# Administrator route to delete a book by ISBN
@app.route('/admin/delete_book/<string:ISBN>', methods=['DELETE'])
def delete_book(ISBN):
    if not is_admin_logged_in():
        return Response("Unauthorized. Please log in as an administrator.", status=401, mimetype='application/json')

    # Check if the book with the provided ISBN exists in the database
    found_book = None
    for book in db["books"]:
        if book.ISBN == ISBN:
            found_book = book
            break

    if found_book is None:
        return Response(f"Book with ISBN {ISBN} not found.", status=404, mimetype='application/json')

    # Check if the book is currently reserved by any user
    if is_book_reserved(ISBN):
        return Response(f"Book with ISBN {ISBN} is currently reserved and cannot be deleted.", status=400, mimetype='application/json')

    # Delete the book from the database
    db["books"].remove(found_book)

    return Response(f"Book with ISBN {ISBN} deleted successfully.", status=200, mimetype='application/json')

# Search books route for administrators
@app.route('/admin/searchBooks', methods=['GET'])
def admin_search_books():
    # Check if the admin is logged in
    if not session.get('admin_logged_in'):
        return Response("Unauthorized. Please log in as an administrator.", status=401, mimetype='application/json')

    # Get search criteria from the request
    title = request.args.get('title', '').strip()
    author = request.args.get('author', '').strip()
    ISBN = request.args.get('ISBN', '').strip()

    # Create a query to search books based on criteria
    query = {}

    if title:
        query['title'] = {'$regex': title, '$options': 'i'}  # Case-insensitive title search

    if author:
        query['author'] = {'$regex': author, '$options': 'i'}  # Case-insensitive author search

    if ISBN:
        query['ISBN'] = ISBN  # ISBN search

    query['available'] = True  # Only show available books

    # Search for books in the database based on the query
    books = db['books'].find(query)

    # Prepare the response data
    result = []
    for book in books:
        book_info = {
            'ISBN': book['ISBN'],
            'title': book['title'],
            'author': book['author'],
            'Publish': book['Publish']
        }
        result.append(book_info)

    return jsonify(result)

# Display book details route for administrators
@app.route('/admin/bookDetails/<string:ISBN>', methods=['GET'])
def admin_book_details(ISBN):
    # Check if the admin is logged in
    if not session.get('admin_logged_in'):
        return Response("Unauthorized. Please log in as an administrator.", status=401, mimetype='application/json')

    # Find the book in the database based on ISBN
    book = db['books'].find_one({'ISBN': ISBN})

    if not book:
        return Response(f"Book with ISBN {ISBN} not found.", status=404, mimetype='application/json')

    # Check if the book is reserved by a user
    is_reserved = is_book_reserved(ISBN)
    user_info = None

    if is_reserved:
        # Get user information who reserved the book
        reservation = db['Reservations'].find_one({'ISBN': ISBN})
        if reservation:
            user_info = {
                'first_name': reservation['first_name'],
                'last_name': reservation['last_name'],
                'email': reservation['email'],
                'phone': reservation['phone']
            }

    # Prepare the response data
    book_details = {
        'ISBN': book['ISBN'],
        'title': book['title'],
        'author': book['author'],
        'Publish': book['Publish'],
        'Summary': book['Summary'],
        'NumberPG': book['NumberPG'],
        'days_available_for_rent': book['days_available_for_rent'],
        'is_reserved': is_reserved,
        'user_info': user_info
    }

    return jsonify(book_details)



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)