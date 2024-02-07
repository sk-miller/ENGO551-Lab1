# Book Review Web Application

Welcome to the Book Review Web Application! This Flask-based web application allows users to register, log in, search for books, view book details, and submit reviews. The project also includes a script to import book data from a CSV file into the database.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Requirements](#requirements)

## Features
1. **User Registration and Authentication:**
   - Users can register with unique usernames and passwords.
   - Existing usernames are checked to avoid duplication.

2. **Book Search:**
   - Users can search for books by ISBN, title, or author.
   - Search results are displayed with book details.

3. **Book Details:**
   - Users can view detailed information about a specific book.
   - Information includes book details from the local database and additional data fetched from the Google Books API.

4. **User Reviews:**
   - Users can submit reviews for books, including ratings and comments.
   - Average user rating is calculated and displayed for each book.

5. **Import Books:**
   - The project includes a script (`import_books`) to read book data from a CSV file ('books.csv') and populate the database.

## Installation
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/book-review-web-app.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the database URI in `app/__init__.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = "your_database_uri_here"
   ```

## Usage
1. Run the application:
   ```bash
   python run.py
   ```
   The application will be accessible at `http://127.0.0.1:5000/` in your web browser.

2. Register a new user or use existing credentials to log in.

3. Explore the different features, such as book search, book details, and submitting reviews.

## File Structure
- **app/__init__.py:** Initializes the Flask application and sets up the SQLAlchemy database.
- **app/routes.py:** Defines the routes and functionalities of the application.
- **app/models.py:** Contains SQLAlchemy models for User, Book, and Review.
- **import_books.py:** A script to import book data from 'books.csv' into the database.
- **run.py:** Runs the Flask application, creates tables, and imports books.
- **README.md:** The file you are currently reading.

## Requirements
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Requests