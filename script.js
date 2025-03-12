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

// Código para el botón de transcribir
document.getElementById('transcribe-button').addEventListener('click', function () {
    const audioFile = document.getElementById('audio').files[0];
    if (!audioFile) {
        alert('Por favor, selecciona un archivo de audio.');
        return;
    }

    const formData = new FormData();
    formData.append('audio', audioFile);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcription) {
            // Llenar el campo de mensaje con la transcripción
            document.getElementById('mensaje').value = data.transcription;
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al transcribir el audio.');
    });
});
