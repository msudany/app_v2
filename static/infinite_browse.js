let currentPage = 1;
let isLoading = false;

function loadRecommendations() {
    if (isLoading) return;

    isLoading = true;
    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    fetch(`/browse?page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recommendations-container');

            // Append recommended books
            data.books.forEach(book => {
                const bookElement = document.createElement('div');
                bookElement.classList.add('col');
                bookElement.innerHTML = `
                    <div class="card h-100 shadow-sm">
                        <img src="${book.cover_image}" class="card-img-top" alt="${book.title}">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="/book/${book.id}" class="text-decoration-none">${book.title}</a>
                            </h5>
                            <p><strong>Author:</strong> <a href="/author/${book.author.id}" class="text-decoration-none">${book.author.name}</a></p>
                            <p><strong>Rating:</strong> ${book.rating}/5</p>
                            <p>${book.categories.map(cat => `<span class="badge bg-primary">${cat}</span>`).join(' ')}</p>
                        </div>
                    </div>
                `;
                container.appendChild(bookElement);
            });

            // Update the state
            spinner.style.display = 'none';
            isLoading = false;

            if (data.has_next) {
                currentPage++;
            } else {
                window.removeEventListener('scroll', handleScroll);
            }
        })
        .catch(error => {
            console.error('Error loading recommendations:', error);
            spinner.style.display = 'none';
            isLoading = false;
        });
}

function handleScroll() {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 10) {
        loadRecommendations();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadRecommendations();
    window.addEventListener('scroll', handleScroll);
});
