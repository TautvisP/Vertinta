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

        document.getElementById('openModal').addEventListener('click', () => {
            this.openModal();
        });

        document.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });

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