from werkzeug.security import generate_password_hash
from models import db, User, Book, Category, Author
from run import app


def seed_data():
    # Seed Users
    if not User.query.filter_by(username="reader1").first():
        reader1 = User(
            username="reader1",
            email="reader1@example.com",
            password=generate_password_hash("password", method='pbkdf2:sha256'),
        )
        db.session.add(reader1)

    if not User.query.filter_by(username="reader2").first():
        reader2 = User(
            username="reader2",
            email="reader2@example.com",
            password=generate_password_hash("password", method='pbkdf2:sha256'),
        )
        db.session.add(reader2)

    if not User.query.filter_by(username="reader2").first():
        reader2 = User(
            username="reader2",
            email="reader2@example.com",
            password=generate_password_hash("password", method='pbkdf2:sha256'),
        )
        db.session.add(reader2)

    if not User.query.filter_by(username="reader3").first():
        reader2 = User(
            username="reader3",
            email="reader3@example.com",
            password=generate_password_hash("password", method='pbkdf2:sha256'),
        )
        db.session.add(reader2)

        # Seed Categories
        category_names = ["Fiction", "Romance", "Thriller", "Mystery", "Science Fiction", "Fantasy"]
        category_objects = {}

        for name in category_names:
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name)
                db.session.add(category)
            category_objects[name] = category

        # Commit categories
        db.session.commit()

        # Seed Authors
        authors_data = [
            {"name": "Author One", "bio": "A prolific writer of fiction.",
             "profile_pic": "/static/images/author_one.png"},
            {"name": "Author Two", "bio": "Known for thrilling tales.", "profile_pic": "/static/images/author_two.png"},
            {"name": "Author Three", "bio": "A celebrated mystery novelist.",
             "profile_pic": "/static/images/author_three.png"}
        ]

        author_objects = {}
        for author_data in authors_data:
            author = Author.query.filter_by(name=author_data["name"]).first()
            if not author:
                author = Author(**author_data)
                db.session.add(author)
            author_objects[author.name] = author

        # Commit authors
        db.session.commit()

        # Seed Books
        books_data = [
            {
                "title": "Book One",
                "author_name": "Author One",
                "summary": "A fascinating fiction book.",
                "pages": 300,
                "categories": ["Fiction", "Romance"],
                "cover_image": "http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg"
            },
            {
                "title": "Book Two",
                "author_name": "Author Two",
                "summary": "An edge-of-your-seat thriller.",
                "pages": 250,
                "categories": ["Thriller", "Mystery"],
                "cover_image": "http://images.amazon.com/images/P/1234567890.01.LZZZZZZZ.jpg"
            },
            {
                "title": "Book Three",
                "author_name": "Author Three",
                "summary": "A captivating mystery novel.",
                "pages": 400,
                "categories": ["Mystery", "Fiction"],
                "cover_image": "http://images.amazon.com/images/P/9876543210.01.LZZZZZZZ.jpg"
            }
        ]

        for book_data in books_data:
            # Check if the book already exists
            book = Book.query.filter_by(title=book_data["title"]).first()
            if not book:
                book = Book(
                    title=book_data["title"],
                    author_id=author_objects[book_data["author_name"]].id,
                    summary=book_data["summary"],
                    pages=book_data["pages"],
                    cover_image=book_data["cover_image"]
                )
                # Add categories to the book
                for category_name in book_data["categories"]:
                    book.categories.append(category_objects[category_name])

                db.session.add(book)
    # Commit all changes
    db.session.commit()
