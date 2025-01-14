import csv

from sqlalchemy import insert
from werkzeug.security import generate_password_hash

import models
from models import User, Author, Book, Category, Review, book_category
from extensions import db

def seed_data():
    # Define the paths to the CSV files
    csv_files = {
        "users": "static/processed_data/user(1).csv",
        "authors": "static/processed_data/author(1).csv",
        "books": "static/processed_data/book_final.csv",
        "categories": "static/processed_data/category(1).csv",
        "book_categories": "static/processed_data/book_category(1).csv",
        "reviews": "static/processed_data/Cleaned_Reviews_with_Integer_Book_IDs.csv"
    }

    try:
        # # Seed Users
        # with open(csv_files["users"], 'r') as file:
        #     reader = csv.DictReader(file)
        #     users = []
        #     for row in reader:
        #         existing_user = User.query.filter_by(email=row['email']).first()
        #         if existing_user:
        #             continue
        #
        #         user = User(
        #             id=int(row['id']),
        #             username=row['username'],
        #             email=row['email'],
        #             # password=generate_password_hash("password", method="pbkdf2:sha256"), # Use a hashed password in production
        #             password="password",
        #             profile_preferences=row['profile_preferences'],
        #             display_name=row['display_name'] if row['display_name'] else "Anonymous User",
        #             bio=row['bio'],
        #             gender=row['gender'],
        #             age=int(float(row['age'])) if row['age'] else None,
        #             location=row['location'],
        #             profile_pic=row['profile_pic'] if row['profile_pic'] else "/static/images/default_profile.png"
        #         )
        #         users.append(user)
        #     db.session.bulk_save_objects(users)

        # # Seed Authors
        # with open(csv_files["authors"], 'r') as file:
        #     reader = csv.DictReader(file)
        #     authors = []
        #     for row in reader:
        #         author = Author(
        #             id=int(row['id']),
        #             name=row['name'],
        #             bio=row['bio'],
        #             # profile_pic=row['profile_pic']
        #             profile_pic="/static/images/default_profile.png"
        #         )
        #         authors.append(author)
        #     db.session.bulk_save_objects(authors)

        # # Seed Books
        # with open(csv_files["books"], 'r') as file:
        #     reader = csv.DictReader(file)
        #     books = []
        #     for row in reader:
        #
        #         book = Book(
        #             id=int(row['id']),
        #             title=row['title'],
        #             author_id=int(row['author_id']),
        #             summary=row['summary'],
        #             pages=int(float(row['pages'])) if row['pages'] else 300,
        #             rating=int(float(row['rating'])) if row['rating'] else 0,
        #             cover_image=row['cover_image']
        #         )
        #         books.append(book)
        #     db.session.bulk_save_objects(books)

        # # Seed Categories
        # with open(csv_files["categories"], 'r') as file:
        #     reader = csv.DictReader(file)
        #     categories = []
        #     for row in reader:
        #
        #         category = Category(
        #             id=int(row['id']),
        #             name=row['name']
        #         )
        #         categories.append(category)
        #     db.session.bulk_save_objects(categories)
        #
        # # Seed Book-Category Relationships
        # with open(csv_files["book_categories"], 'r') as file:
        #     reader = csv.DictReader(file)
        #     book_categories = []
        #     for row in reader:
        #         book_category = {
        #             "book_id": int(row['book_id']),
        #             "category_id": int(row['category_id'])
        #         }
        #         book_categories.append(book_category)
        #
        #     # Use SQLAlchemy's insert() to bulk insert the data
        #     if book_categories:
        #         db.session.execute(insert(models.book_category).values(book_categories))
        #         db.session.commit()  # Commit the transaction

        # Seed Reviews
        with open(csv_files["reviews"], 'r') as file:
            reader = csv.DictReader(file)
            reviews = []
            for row in reader:
                review = Review(
                    id=int(row['id']),
                    content=row['content'],
                    rating=int(row['rating']) if row['rating'] else 2,
                    user_id=int(row['user_id']),
                    book_id=int(row['book_id'])
                )
                reviews.append(review)
            db.session.bulk_save_objects(reviews)

        # Commit all changes
        db.session.commit()
        print("All data successfully seeded into the database.")

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")
