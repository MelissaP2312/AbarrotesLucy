// Código para el carrusel de productos
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
const productContainer = document.querySelector('.product-container');
let scrollPosition = 0;

const cardWidth = document.querySelector('.product-card').offsetWidth + 10;

// Mover al siguiente conjunto de tarjetas
nextBtn.addEventListener('click', () => {
    if (scrollPosition < (productContainer.scrollWidth - productContainer.offsetWidth)) {
        scrollPosition += cardWidth * 4;
        productContainer.style.transform = `translateX(-${scrollPosition}px)`;
    }
});

// Mover al conjunto anterior de tarjetas
prevBtn.addEventListener('click', () => {
    if (scrollPosition > 0) {
        scrollPosition -= cardWidth * 4;
        productContainer.style.transform = `translateX(-${scrollPosition}px)`;
    }
});
