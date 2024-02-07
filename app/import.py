import csv
from app import db
from app.models import Book, User, Review  

def import_books():
    with open('books.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            book = Book(isbn=row['isbn'], title=row['title'], author=row['author'], year=row['year'])
            db.session.add(book)

    db.session.commit()

if __name__ == "__main__":
    
    db.create_all()
    import_books()
