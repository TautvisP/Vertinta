import { Component } from './osom.build.js';

/**
 * @description Image Annotation
 **/
export default class ImageAnnotation extends Component {
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

        document.getElementById('annotatable-image').addEventListener('load', () => {
            this.onImageLoad();
        });

        document.getElementById('annotatable-image').addEventListener('click', (event) => {
            this.onImageClick(event);
        });

        document.querySelectorAll('.existing-marker').forEach((marker) => {
            marker.addEventListener('click', (event) => {
                this.onMarkerClick(event, marker);
            });
        });

        document.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });

        window.addEventListener('click', (event) => {
            this.onWindowClick(event);
        });

        document.getElementById('edit-annotation').addEventListener('click', (event) => {
            this.showEditForm(event);
        });

        document.getElementById('save-annotation').addEventListener('click', (event) => {
            this.editAnnotation(event);
        });

        document.getElementById('delete-annotation').addEventListener('click', (event) => {
            this.deleteAnnotation(event);
        });

        document.getElementById('annotation-form').addEventListener('submit', (event) => {
            this.setCoordinates(event);
        });
    }

    getCookie(name) {
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

    setCoordinates(event) {
        const x = document.getElementById('id_x_coordinate').value;
        const y = document.getElementById('id_y_coordinate').value;
        console.log('Coordinates before submit:', { x, y });
        if (!x || !y) {
            event.preventDefault();
            alert('Please click on the image to set the coordinates.');
        }
    }

    showEditForm(event) {
        const annotationId = event.target.dataset.id;
        fetch(`/evaluator/api/annotations/${annotationId}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('annotation-text').style.display = 'none';
                document.getElementById('annotation-edit-text').value = data.annotation_text;
                document.getElementById('annotation-edit-text').style.display = 'block';
                document.getElementById('annotation-edit-image').style.display = 'block';
                document.getElementById('save-annotation').style.display = 'block';
                document.getElementById('edit-annotation').style.display = 'none';
                document.getElementById('id_x_coordinate').value = data.x_coordinate;
                document.getElementById('id_y_coordinate').value = data.y_coordinate;
            });
    }

    editAnnotation(event) {
        const annotationId = event.target.dataset.id;
        const formData = new FormData(document.getElementById('annotation-edit-form'));
        const csrftoken = this.getCookie('csrftoken');
        fetch(`/evaluator/api/annotations/${annotationId}/edit/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Annotation updated successfully');
                location.reload();
            } else {
                alert('Error updating annotation');
            }
        });
    }

    deleteAnnotation(event) {
        const annotationId = event.target.dataset.id;
        const csrftoken = this.getCookie('csrftoken');
        fetch(`/evaluator/api/annotations/${annotationId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Annotation deleted successfully');
                location.reload();
            } else {
                alert('Error deleting annotation');
            }
        });
    }

    onImageLoad() {
        const image = document.getElementById('annotatable-image');
        const container = document.getElementById('annotation-container');
        container.style.width = image.naturalWidth + 'px';
        container.style.height = image.naturalHeight + 'px';
    }

    onImageClick(event) {
        console.log('Image clicked');
    
        const existingNewMarker = document.querySelector('.new-marker');
        if (existingNewMarker) {
            console.log('Removing existing new marker');
            existingNewMarker.remove();
        }

        const image = document.getElementById('annotatable-image');
        const rect = image.getBoundingClientRect();
        console.log('Image rect:', rect);
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        console.log('Calculated coordinates:', { x, y });
        document.getElementById('id_x_coordinate').value = x;
        document.getElementById('id_y_coordinate').value = y;
        console.log('Coordinates set:', { x, y });
    
        const marker = document.createElement('div');
        marker.className = 'marker new-marker';
        marker.style.left = x + '%';
        marker.style.top = y + '%';
        marker.innerHTML = '<span class="marker-number">+</span>';
        console.log('Appending new marker:', marker);
        document.getElementById('annotation-container').appendChild(marker);
    }

    onMarkerClick(event, marker) {
        const annotationId = marker.getAttribute('data-id');
        this.fetchAnnotationDetails(annotationId);
    }

    fetchAnnotationDetails(annotationId) {
        fetch(`/evaluator/api/annotations/${annotationId}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('annotation-text').innerText = data.annotation_text;
                if (data.annotation_image) {
                    document.getElementById('annotation-image').src = data.annotation_image;
                    document.getElementById('annotation-image').style.display = 'block';
                } else {
                    document.getElementById('annotation-image').style.display = 'none';
                }
                document.getElementById('annotationModal').style.display = 'block';
                document.getElementById('edit-annotation').dataset.id = annotationId;
                document.getElementById('delete-annotation').dataset.id = annotationId;
                document.getElementById('save-annotation').dataset.id = annotationId;
                document.getElementById('id_x_coordinate').value = data.x_coordinate;
                document.getElementById('id_y_coordinate').value = data.y_coordinate;
            });
    }

    closeModal() {
        document.getElementById('annotationModal').style.display = 'none';
    }

    onWindowClick(event) {
        const modal = document.getElementById('annotationModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}