# run.py
from app import app
from app import db
import csv
from app.models import Book, User, Review  # Assuming you have User and Review models in app.models
app.secret_key = 'tassie'
def import_books():
    with open('books.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_book = Book.query.filter_by(isbn=row['isbn']).first()

            if existing_book:
                # Update the existing record (you can customize this part based on your needs)
                existing_book.title = row['title']
                existing_book.author = row['author']
                existing_book.year = row['year']
            else:
                # Insert a new record only if the isbn doesn't exist
                new_book = Book(isbn=row['isbn'], title=row['title'], author=row['author'], year=row['year'])
                db.session.add(new_book)

        db.session.commit()

    db.session.commit()
if __name__ == "__main__":
    with app.app_context():
        # Create tables based on models
        db.create_all()

        # Import books into the Book table
        import_books()

    # Run the Flask application
    app.run(debug=True)
