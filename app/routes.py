from flask import render_template, redirect, url_for, request, session, flash
from app import app, db
from app.models import User, Book, Review
import requests
from sqlalchemy import text
from flask import flash, get_flashed_messages
from sqlalchemy.exc import IntegrityError
GOOGLE_BOOKS_API_KEY = "AIzaSyAIOpqRMwT2J2RdZng11cII6YxvzGKy1tI"

# Define routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists in the database
        sql_check_user = text("SELECT * FROM \"user\" WHERE username ILIKE :username")
        existing_user = db.session.execute(sql_check_user, {'username': username}).fetchone()

        if existing_user:
            flash('Username already exists. Choose another one.', 'error')
            return render_template('register.html', error='Username already exists. Choose another one.')

        # Create a new user and add it to the database
        sql_create_user = text("INSERT INTO \"user\" (username, password_hash) VALUES (:username, :password)")
        db.session.execute(sql_create_user, {'username': username, 'password': password})
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_username = request.form.get('login_username')
        login_password = request.form.get('login_password')

        # Authenticate the user
        sql_authenticate_user = text("SELECT * FROM \"user\" WHERE username ILIKE :username AND password_hash = :password")
        user = db.session.execute(sql_authenticate_user, {'username': login_username, 'password': login_password}).fetchone()

        if user:
            session['username'] = login_username
            flash('Login successful!', 'success')
            return redirect(url_for('search'))
        else:
            flash('Invalid login credentials', 'error')
            return render_template('register.html', error='Invalid login credentials')

    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_input = request.form.get('search_input')

        # Perform search in the database based on the search_input
        sql_search_books = text(
            "SELECT * FROM book "
            "WHERE isbn ILIKE :search_input "
            "OR title ILIKE :search_input "
            "OR author ILIKE :search_input"
        )
        search_results = db.session.execute(sql_search_books, {'search_input': f'%{search_input}%'}).fetchall()
        return render_template('search.html', search_results=search_results)

    return render_template('search.html')


@app.route('/book/<isbn>')
def book(isbn):
    if 'username' not in session:
        return redirect(url_for('login'))
    average_user_rating = request.args.get('average_user_rating')

    # Fetch book details from the database based on ISBN
    book = Book.query.filter_by(isbn=isbn).first()

    if not book:
        # Handle case when the book with given ISBN is not found
        return render_template('book_not_found.html')

    # Fetch Google Books details
    google_books_info = get_google_books_info(isbn)
    print(google_books_info)
    reviews = Review.query.filter_by(book_id=book.id).all()
    print(reviews)
    average_user_rating = round(sum(review.rating for review in reviews) / len(reviews), 2) if reviews else None
    print(average_user_rating)
    return render_template('book.html', book=book, google_books_info=google_books_info, average_user_rating=average_user_rating)


def get_google_books_info(isbn):
    google_books_info = []

    # Make a request to the Google Books API
    google_books_url = 'https://www.googleapis.com/books/v1/volumes'
    params = {'key': GOOGLE_BOOKS_API_KEY, 'q': f'isbn:{isbn}'}

    try:
        response = requests.get(google_books_url, params=params)
        data = response.json()
       
        if 'items' in data and data['items']:
            book_info = data['items'][0]['volumeInfo']
            
            # Check for the existence of 'averageRating' and 'ratingsCount' fields
            average_rating = book_info.get('averageRating', 'N/A')
            ratings_count = book_info.get('ratingsCount', 'N/A')
            thumbnail = book_info.get('imageLinks', {}).get('thumbnail', 'N/A')
            publish_date = book_info.get('publishedDate', 'N/A')
            isbn_10 = None
            isbn_13 = None
            for identifier in book_info.get('industryIdentifiers', []):
                if identifier['type'] == 'ISBN_10':
                    isbn_10 = identifier['identifier']
                elif identifier['type'] == 'ISBN_13':
                    isbn_13 = identifier['identifier']

            google_books_info.append({
                'title': book_info.get('title', 'N/A'),
                'authors': book_info.get('authors', ['N/A']),
                'average_rating': average_rating,
                'ratings_count': ratings_count,
                'description': book_info.get('description', 'N/A'),
                'thumbnail': thumbnail,
                'publish_date': publish_date,
                'isbn_10': isbn_10,
                'isbn_13': isbn_13
            })
        else:
            google_books_info.append({'error': 'No data available'})

    except requests.RequestException as e:
        print(f"Error fetching Google Books info: {e}")
        google_books_info.append({'error': 'Error fetching Google Books info'})

    return google_books_info



@app.route('/submit_review/<isbn>', methods=['POST'])
def submit_review(isbn):
    if 'username' not in session:
        return redirect(url_for('login'))

    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')

    # Fetch the book from the database based on ISBN
    book = Book.query.filter_by(isbn=isbn).first()

    if not book:
        return render_template('book_not_found.html')

    # Get the user from the session
    username = session['username']
    user = User.query.filter_by(username=username).first()

    if not user:
        return render_template('login.html', error='Invalid user')

    # Check if the user has already reviewed this book
    existing_review = Review.query.filter_by(user_id=user.id, book_id=book.id).first()
    if existing_review:
        flash('You have already submitted a review for this book.', 'error')
        return redirect(url_for('book', isbn=isbn))

    # Create a new review and add it to the database
    new_review = Review(rating=rating, comment=comment, user_id=user.id, book_id=book.id)
    
    try:
        db.session.add(new_review)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Error submitting review. Please try again later.', 'error')
        return redirect(url_for('book', isbn=isbn))

    flash('Review submitted successfully!', 'success')
    reviews = Review.query.filter_by(book_id=book.id).all()
    average_user_rating = round(sum(review.rating for review in reviews) / len(reviews), 2) if reviews else None
    return redirect(url_for('book', isbn=isbn, average_user_rating=average_user_rating))
