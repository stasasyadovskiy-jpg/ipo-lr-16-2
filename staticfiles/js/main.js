let csrfToken = '';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function loadProducts() {
    const spinner = document.getElementById('spinner');
    const productGrid = document.getElementById('product-grid');
    if (spinner) spinner.style.display = 'flex';
    if (productGrid) productGrid.innerHTML = '';

    fetch('/api/products/')
        .then(response => {
            if (!response.ok) throw new Error('Ошибка загрузки');
            return response.json();
        })
        .then(data => {
            if (spinner) spinner.style.display = 'none';
            renderProducts(data);
        })
        .catch(error => {
            if (spinner) spinner.style.display = 'none';
            showError('Не удалось загрузить товары');
        });
}

function renderProducts(products) {
    const container = document.getElementById('product-grid');
    if (!container) return;

    products.forEach(product => {
        const col = document.createElement('div');
        col.className = 'col-sm-6 col-md-4 col-lg-3 mb-4';
        col.innerHTML = `
            <div class="card product-card h-100">
                <img src="${product.image || '/static/images/no-image.png'}" class="card-img-top" alt="${product.name}">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text flex-grow-1">${product.description ? product.description.substring(0, 80) + '...' : ''}</p>
                    <p class="price">${product.price} руб.</p>
                    <div class="mt-auto">
                        <a href="/catalog/${product.id}/" class="btn btn-outline-primary btn-sm">Подробнее</a>
                        <button class="btn btn-success btn-sm" onclick="addToCart(${product.id})">🛒 В корзину</button>
                    </div>
                </div>
            </div>`;
        container.appendChild(col);
    });
}

function addToCart(productId) {
    csrfToken = getCookie('csrftoken');
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = '/admin/login/?next=/catalog/';
            return;
        }
        showToast('Товар добавлен в корзину');
    })
    .catch(error => {
        showError('Ошибка при добавлении в корзину');
    });
}

function showToast(message) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    const toastEl = document.getElementById('toast-container');
    const toastHTML = `
        <div class="toast align-items-center text-bg-success border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>`;
    toastEl.innerHTML += toastHTML;
    const toast = new bootstrap.Toast(toastEl.lastElementChild);
    toast.show();
}

function showError(message) {
    const container = document.getElementById('product-grid');
    if (container) {
        container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('product-grid')) {
        loadProducts();
    }
});