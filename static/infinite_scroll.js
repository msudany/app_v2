let currentPage = 2; // First page is already loaded
let isLoading = false;

function loadBooks() {
    if (isLoading) return;

    isLoading = true;
    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    fetch(`/load_books?page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('books-container');
            data.books.forEach(book => {
                const bookElement = document.createElement('div');
                bookElement.classList.add('col');
                bookElement.innerHTML = `
                    <div class="card h-100 shadow-sm">
                        <img src="${book.cover_image}" class="card-img-top" alt="${book.title} Cover">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="/book/${book.id}" class="text-decoration-none">${book.title}</a>
                            </h5>
                            <a href="/author/${book.author.id}" class="text-decoration-none">${book.author.name}</a>
                            <p class="card-text">
                                ${book.categories.map(category => `<span class="badge bg-primary">${category}</span>`).join(' ')}
                            </p>
                        </div>
                    </div>
                `;
                container.appendChild(bookElement);
            });

            // Hide spinner and update the current page
            spinner.style.display = 'none';
            isLoading = false;

            if (data.has_next) {
                currentPage++;
            } else {
                window.removeEventListener('scroll', handleScroll);
            }
        })
        .catch(error => {
            console.error('Error loading books:', error);
            spinner.style.display = 'none';
            isLoading = false;
        });
}

function handleScroll() {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 10) {
        loadBooks();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('scroll', handleScroll);
});
