import os

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from models import db, Book, Review, ReadingProgress, User, Category, book_category, Author
from run import app

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Route
@app.route('/')
def home():
    books = Book.query.all()

    return render_template('home.html', books=books)

# Book Details
@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    user_review = None
    already_in_library = False

    if current_user.is_authenticated:
        # Check if the user has already reviewed this book
        user_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()

        # Check if the book is already in the user's library
        already_in_library = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first() is not None

    # Get all reviews with user display names
    reviews_with_usernames = []
    for review in book.reviews:
        user = User.query.get(review.user_id)
        reviews_with_usernames.append({
            "content": review.content,
            "rating": review.rating,
            "user_display_name": user.display_name if user else "Unknown User"
        })

    return render_template(
        'book_details.html',
        book=book,
        user_review=user_review,
        reviews=reviews_with_usernames,
        already_in_library=already_in_library
    )

# Add Review
@app.route('/review/<int:book_id>', methods=['POST'])
@login_required
def review(book_id):
    # Check if the user has already reviewed the book
    existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()

    if existing_review:
        # Update existing review
        existing_review.rating = int(request.form['rating'])
        existing_review.content = request.form['content']
        flash('Your review has been updated!', 'success')
    else:
        # Add a new review
        new_review = Review(
            rating=int(request.form['rating']),
            content=request.form['content'],
            user_id=current_user.id,
            book_id=book_id
        )
        db.session.add(new_review)
        flash('Your review has been added!', 'success')

    db.session.commit()
    return redirect(url_for('book_details', book_id=book_id))


# Library Route
@app.route('/library', methods=['GET', 'POST'])
@login_required
def library():
    if request.method == 'POST':
        # Handle progress update
        book_id = int(request.form.get('book_id'))
        pages_read = int(request.form.get('pages_read'))

        progress = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if not progress:
            flash('You need to add this book to your library first.', 'danger')
            return redirect(url_for('library'))

        if progress.status != 'Currently Reading':
            flash('You can only update progress for books in the "Currently Reading" shelf.', 'warning')
            return redirect(url_for('library'))

        book = Book.query.get_or_404(book_id)
        if pages_read > book.pages:
            flash(f"The book has only {book.pages} pages.", 'warning')
        else:
            progress.pages_read = pages_read
            db.session.commit()
            flash('Reading progress updated!', 'success')

    # Fetch library data for the user
    progress_entries = ReadingProgress.query.filter_by(user_id=current_user.id).all()
    return render_template('library.html', progress=progress_entries)


# Add Book to Library
@app.route('/add_to_library/<int:book_id>', methods=['POST'])
@login_required
def add_to_library(book_id):
    status = request.form['status']

    # Check if the book is already in the user's library
    existing_entry = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if existing_entry:
        # Update the status if the book already exists
        existing_entry.status = status
        db.session.commit()
        flash(f'Book moved to "{status}" shelf.', 'success')
    else:
        # Add the book to the library
        progress = ReadingProgress(user_id=current_user.id, book_id=book_id, status=status)
        db.session.add(progress)
        db.session.commit()
        flash(f'Book added to your library as "{status}".', 'success')

    return redirect(url_for('library'))


# Profile Route
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update user details
        current_user.display_name = request.form['display_name']
        current_user.bio = request.form['bio']
        current_user.location = request.form['location']

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic and allowed_file(profile_pic.filename):
                # Secure the file name and save it
                filename = secure_filename(profile_pic.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_pic.save(filepath)

                # Update user's profile picture path
                current_user.profile_pic = f'/static/uploads/{filename}'

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)

# View Other Users' Profiles Route
@app.route('/user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    library = ReadingProgress.query.filter_by(user_id=user.id).all()
    is_following = current_user.is_following(user)
    followed_categories = user.followed_categories
    print(f"User {user.id} Profile Pic: {user.profile_pic}")  # Debug
    return render_template(
        'user_profile.html',
        user=user,
        library=library,
        is_following=is_following,
        followed_categories=followed_categories
    )

@app.route('/author/<int:author_id>')
def author_profile(author_id):
    author = Author.query.get_or_404(author_id)

    # Fetch books by the author
    books = Book.query.filter_by(author_id=author.id).all()

    # Determine popular categories
    category_counts = {}
    for book in books:
        for category in book.categories:
            category_counts[category.name] = category_counts.get(category.name, 0) + 1
    popular_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    # Check if the current user follows this author
    is_following = current_user.is_authenticated and author in current_user.followed_authors

    return render_template(
        'author_profile.html',
        author=author,
        books=books,
        popular_categories=popular_categories,
        is_following=is_following
    )

@app.route('/follow_author/<int:author_id>', methods=['POST'])
@login_required
def follow_author(author_id):
    author = Author.query.get_or_404(author_id)

    if author in current_user.followed_authors:
        current_user.followed_authors.remove(author)
        db.session.commit()
        flash(f'You unfollowed {author.name}.', 'info')
    else:
        current_user.followed_authors.append(author)
        db.session.commit()
        flash(f'You followed {author.name}.', 'success')

    return redirect(url_for('author_profile', author_id=author_id))

# Following Users Route
@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {user.display_name}!', 'success')
    return redirect(url_for('view_user', user_id=user_id))

# Unfollowing Users Route
@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You have unfollowed {user.display_name}.', 'info')
    return redirect(url_for('view_user', user_id=user_id))

# Search Route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('home'))

    # Filters
    min_pages = request.args.get('min_pages', type=int)
    max_pages = request.args.get('max_pages', type=int)
    category_id = request.args.get('category', type=int)
    min_rating = request.args.get('rating', type=int)

    # Query for books by title or categories
    books_query = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) |
        (Book.id.in_(
            db.session.query(book_category.c.book_id)
            .join(Category, book_category.c.category_id == Category.id)
            .filter(Category.name.ilike(f'%{query}%'))
        ))
    )

    # Apply optional filters
    if min_pages:
        books_query = books_query.filter(Book.pages >= min_pages)
    if max_pages:
        books_query = books_query.filter(Book.pages <= max_pages)
    if category_id:
        books_query = books_query.join(book_category).filter(book_category.c.category_id == category_id)
    if min_rating:
        books_query = books_query.filter(Book.rating >= min_rating)

    books = books_query.all()

    # Query for authors
    authors = Author.query.filter(Author.name.ilike(f'%{query}%')).all()

    # Query for categories
    categories = Category.query.filter(Category.name.ilike(f'%{query}%')).all()

    # Query for users
    users = User.query.filter(User.display_name.ilike(f'%{query}%')).all()

    # Fetch all categories for filter dropdown
    all_categories = Category.query.all()

    return render_template(
        'search_results.html',
        query=query,
        books=books,
        authors=authors,
        categories=categories,
        users=users,
        all_categories=all_categories
    )

@app.route('/move_to_read/<int:book_id>', methods=['POST'])
@login_required
def move_to_read(book_id):
    progress = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if not progress:
        flash('Book not found in your library.', 'danger')
        return redirect(url_for('library'))

    if progress.pages_read < progress.book.pages:
        flash('You cannot mark this book as completed until you finish reading it.', 'warning')
        return redirect(url_for('library'))

    progress.status = 'Read'
    db.session.commit()
    flash('Book moved to Read shelf!', 'success')
    return redirect(url_for('library'))

@app.route('/categories')
def categories():
    # Fetch all categories
    all_categories = Category.query.all()

    # If the user is logged in, fetch their followed categories
    followed_categories = current_user.followed_categories.all() if current_user.is_authenticated else []

    return render_template(
        'categories.html',
        categories=all_categories,
        followed_categories=followed_categories
    )


# Following a Category Route
@app.route('/follow_category/<int:category_id>', methods=['POST'])
@login_required
def follow_category(category_id):
    category = Category.query.get_or_404(category_id)
    if current_user.is_following_category(category):
        current_user.unfollow_category(category)
        db.session.commit()
        flash(f'You unfollowed the category "{category.name}".', 'info')
    else:
        current_user.follow_category(category)
        db.session.commit()
        flash(f'You followed the category "{category.name}".', 'success')

    # Redirect back to the specific category with an anchor tag
    return redirect(url_for('categories'))

@app.route('/browse')
def browse():
    return render_template('home.html')

@app.route('/authors')
def authors():
    authors = Author.query.all()  # Ensure this retrieves authors
    return render_template('authors.html', authors=authors)
