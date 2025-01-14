from sqlalchemy import func

from extensions import db
from models import Book, Category, Review


from sqlalchemy import or_

def recommend_books(user, page=1, per_page=10):
    """
    Recommend books to the user based on their preferences and behavior.

    Args:
        user (User): The current user object.
        page (int): The current page for pagination.
        per_page (int): Number of books to return per page.

    Returns:
        Pagination: A paginated result of recommended books.
    """
    query = Book.query

    # Collect all filter conditions
    conditions = []

    # Factor 1: Books in followed categories
    if user.followed_categories:
        category_ids = [category.id for category in user.followed_categories]
        conditions.append(Book.categories.any(Category.id.in_(category_ids)))
        print(f"Categories Filter Applied: {category_ids}")

    # Factor 2: Books by followed authors
    if user.followed_authors:
        author_ids = [author.id for author in user.followed_authors]
        conditions.append(Book.author_id.in_(author_ids))
        print(f"Authors Filter Applied: {author_ids}")

    # Factor 3: Books reviewed by followed users
    followed_user_ids = [u.id for u in user.followed]
    if followed_user_ids:
        reviewed_books = db.session.query(Review.book_id).filter(Review.user_id.in_(followed_user_ids)).all()
        reviewed_book_ids = [r.book_id for r in reviewed_books]
        conditions.append(Book.id.in_(reviewed_book_ids))
        print(f"Followed Users' Reviewed Books: {reviewed_book_ids}")

    # Factor 4: Books similar to highly rated books
    highly_rated_books = db.session.query(Review.book_id).filter(
        Review.user_id == user.id, Review.rating >= 4
    ).all()
    highly_rated_book_ids = [r.book_id for r in highly_rated_books]
    if highly_rated_book_ids:
        conditions.append(Book.id.in_(highly_rated_book_ids))
        print(f"Highly Rated Books: {highly_rated_book_ids}")

    # Apply filters using OR logic
    if conditions:
        query = query.filter(or_(*conditions))
    else:
        print("No filters applied. Returning random books.")
        query = Book.query  # Fallback to random books

    # Sort by relevance or random
    query = query.order_by(func.random())

    # Paginate results
    paginated_books = query.paginate(page=page, per_page=per_page, error_out=False)
    print(f"Recommended Books: {[book.title for book in paginated_books.items]}")
    return paginated_books


