import ImageAnnotation from './image_annotation.js';

class MainImageAnnotation {
    /**
    * Constructor
    * @returns {void}
    **/
    constructor() {
        new ImageAnnotation('annotation-container', {}, ['click']);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const dropAreas = document.querySelectorAll('.drop');
    dropAreas.forEach(dropArea => {
        const fileInput = dropArea.querySelector('input[type="file"]');

        dropArea.addEventListener('dragover', (event) => {
            event.preventDefault();
            dropArea.classList.add('dragover');
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('dragover');
        });

        dropArea.addEventListener('drop', (event) => {
            event.preventDefault();
            dropArea.classList.remove('dragover');
            const files = event.dataTransfer.files;
            fileInput.files = files;
            dropArea.querySelector('p').textContent = files[0].name;
        });

        dropArea.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            const files = fileInput.files;
            if (files.length > 0) {
                dropArea.querySelector('p').textContent = files[0].name;
            }
        });
    });
});

new MainImageAnnotation();