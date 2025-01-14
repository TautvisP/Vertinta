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

    }

    onImageLoad() {
        const image = document.getElementById('annotatable-image');
        const container = document.getElementById('annotation-container');
        container.style.width = image.naturalWidth + 'px';
        container.style.height = image.naturalHeight + 'px';
    }

    onImageClick(event) {
        console.log('Image clicked');
    
        // Remove any existing new marker, so that only one new marker is displayed at a time
        const existingNewMarker = document.querySelector('.new-marker');
        if (existingNewMarker) {
            console.log('Removing existing new marker');
            existingNewMarker.remove();
        }

        // Calculate coordinates based on the image size and position
        const image = document.getElementById('annotatable-image');
        const rect = image.getBoundingClientRect();
        console.log('Image rect:', rect);
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        console.log('Calculated coordinates:', { x, y });
        document.getElementById('id_x_coordinate').value = x;
        document.getElementById('id_y_coordinate').value = y;
    
        // Create and place new marker
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