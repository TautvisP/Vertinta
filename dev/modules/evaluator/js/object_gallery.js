import { Component } from './osom.build.js';

/**
 * @description Object Gallery
 **/
export default class ObjectGallery extends Component {
    /**
     * Constructor
     * @returns {void}
     **/
    constructor(elm, data, events, params = {}) {
        super(elm, data, events, params);
        this.init();
    }

    init() {
        this.attach(this.elm);

        const openModalBtn = document.getElementById('openModal');
        if (openModalBtn) {
            const newOpenBtn = openModalBtn.cloneNode(true);
            openModalBtn.parentNode.replaceChild(newOpenBtn, openModalBtn);
            newOpenBtn.addEventListener('click', () => {
                this.openModal();
            });
        }

        const closeBtn = document.querySelector('#myModal .close');
        if (closeBtn) {
            // Remove any existing listeners to prevent duplicates
            const newCloseBtn = closeBtn.cloneNode(true);
            closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
            newCloseBtn.addEventListener('click', () => {
                this.closeModal();
            });
        }

        window.addEventListener('click', (event) => {
            this.onWindowClick(event);
        });

        this.activateEventsHandling();
        this.setupDropAreas();
        this.setupDeleteButtons();
    }

    openModal() {
        const modal = document.getElementById('myModal');
        modal.style.display = 'block';
    }

    closeModal() {
        const modal = document.getElementById('myModal');
        modal.style.display = 'none';
    }

    onWindowClick(event) {
        const modal = document.getElementById('myModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    setupDropAreas() {
        const dropAreas = document.querySelectorAll('.drop');
        dropAreas.forEach(dropArea => {
            const fileInput = dropArea.querySelector('input[type="file"]');
            
            const newDropArea = dropArea.cloneNode(true);
            dropArea.parentNode.replaceChild(newDropArea, dropArea);
            const newFileInput = newDropArea.querySelector('input[type="file"]');
            
            newDropArea.addEventListener('dragover', (event) => {
                event.preventDefault();
                newDropArea.classList.add('dragover');
            });

            newDropArea.addEventListener('dragleave', () => {
                newDropArea.classList.remove('dragover');
            });

            newDropArea.addEventListener('drop', (event) => {
                event.preventDefault();
                newDropArea.classList.remove('dragover');
                const files = event.dataTransfer.files;
                newFileInput.files = files;
                if (files.length > 0) {
                    newDropArea.querySelector('p').textContent = files[0].name;
                }
            });

            newDropArea.addEventListener('click', (event) => {
                newFileInput.click();
                event.stopPropagation();
            });

            newFileInput.addEventListener('click', (event) => {
                event.stopPropagation();
            });

            newFileInput.addEventListener('change', () => {
                const files = newFileInput.files;
                if (files.length > 0) {
                    newDropArea.querySelector('p').textContent = files[0].name;
                }
            });
        });
    }

    setupDeleteButtons() {
        document.querySelectorAll('.icon-button').forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const form = this.closest('form');
                const url = form.action;
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload();
                    } else {
                        alert('Error deleting image');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting image');
                });
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    new ObjectGallery('gallery-container', {}, ['click']);
});