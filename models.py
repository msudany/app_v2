from extensions import db
from flask_login import UserMixin


# Association table for follower relationships
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table for user-category relationships
user_categories = db.Table(
    'user_categories',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# Association table for the Many-to-Many relationship
book_category = db.Table(
    'book_category',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# Association table for the Many-to-Many relationship between User and Author
author_followers = db.Table(
    'author_followers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_preferences = db.Column(db.Text)
    display_name = db.Column(db.String(150), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    profile_pic = db.Column(db.String(250),
                            nullable=False,
                            default="/static/images/default_profile.png"
                            )  # Default avatar

    # Authors followed by the user
    followed_authors = db.relationship(
        'Author',
        secondary=author_followers,
        back_populates='followers',
        overlaps="author_followers"
    )

    # Follower relationship
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('user_followers', lazy='dynamic'), lazy='dynamic'
    )

    # Relationship with categories
    followed_categories = db.relationship(
        'Category', secondary=user_categories,
        backref=db.backref('category_followers', lazy='dynamic'), lazy='dynamic'
    )

    # Check if the current user is following another user
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # Follow a user
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    # Unfollow a user
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # Check if the user is following a category
    def is_following_category(self, category):
        return self.followed_categories.filter(user_categories.c.category_id == category.id).count() > 0

    # Follow a category
    def follow_category(self, category):
        if not self.is_following_category(category):
            self.followed_categories.append(category)

    # Unfollow a category
    def unfollow_category(self, category):
        if self.is_following_category(category):
            self.followed_categories.remove(category)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name

# Author Model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(250), nullable=False, default="/static/images/default_author.png")

    # Books written by the author
    books = db.relationship('Book', backref='author_obj', lazy=True)

    # Users who follow this author
    followers = db.relationship(
        'User',
        secondary=author_followers,
        back_populates='followed_authors',
        overlaps="users_following_authors"
    )

# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    categories = db.relationship(
        'Category', secondary=book_category,
        backref=db.backref('books', lazy='dynamic')
    )
    summary = db.Column(db.Text)
    pages = db.Column(db.Integer)
    reviews = db.relationship('Review', backref='book', lazy=True)
    rating = db.Column(db.Float, default=0)
    cover_image = db.Column(db.String(250),
                            nullable=False,
                            default="/static/images/default_cover.png")  # URL for the book cover image

# Review Model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

# Reading Progress Model
class ReadingProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('reading_progress', lazy=True))  # Add relationship
    pages_read = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50))  # e.g., 'Currently Reading', 'Read', 'Want to Read'

    @property
    def pages_left(self):
        return max(self.book.pages - self.pages_read, 0) if self.book else 0


# Report Model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_id = db.Column(db.Integer, nullable=False)  # Can represent User, Book, or Review
    report_type = db.Column(db.String(50))  # 'User', 'Book', 'Review'
    reason = db.Column(db.Text, nullable=False)

# Publishing Request Model
class PublishingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_title = db.Column(db.String(150), nullable=False)
    book_summary = db.Column(db.Text, nullable=False)
    book_category = db.Column(db.String(100))
    book_pages = db.Column(db.Integer)
    status = db.Column(db.String(50), default='Pending')

