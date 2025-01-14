document.addEventListener('DOMContentLoaded', () => {
    const loadMoreButtons = document.querySelectorAll('.load-more');

    loadMoreButtons.forEach(button => {
        button.addEventListener('click', function () {
            const categoryId = this.dataset.categoryId;
            const currentPage = parseInt(this.dataset.page, 10);

            // Disable the button to prevent multiple clicks
            this.disabled = true;
            this.textContent = 'Loading...';

            fetch(`/category_books/${categoryId}?page=${currentPage}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById(`category-${categoryId}`);

                    // Append new books to the category container
                    data.books.forEach(book => {
                        const bookElement = document.createElement('div');
                        bookElement.classList.add('col-md-4', 'mb-4');
                        bookElement.innerHTML = `
                            <div class="card h-100 shadow-sm">
                                <img src="${book.cover_image}" alt="${book.title} Cover" class="card-img-top">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <a href="/book/${book.id}" class="text-decoration-none">${book.title}</a>
                                    </h5>
                                    <p class="card-text"><strong>Author:</strong> ${book.author.name}</p>
                                    <p class="card-text"><strong>Rating:</strong> ${book.rating}/5</p>
                                </div>
                            </div>
                        `;
                        container.appendChild(bookElement);
                    });

                    // Update the button state
                    if (data.has_next) {
                        this.dataset.page = currentPage + 1; // Increment the page
                        this.disabled = false;
                        this.textContent = 'Load More';
                    } else {
                        this.remove(); // Remove the button if no more books are available
                    }
                })
                .catch(error => {
                    console.error('Error loading books:', error);
                    this.disabled = false;
                    this.textContent = 'Load More';
                });
        });
    });
});
