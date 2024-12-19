// not working as of yet, needs further fixing

/**
 * @description Image Annotation
 **/


export default class ImageAnnotation {
    /**
     * Constructor
     * @returns {void}
     **/
    constructor() {
        this.init();
    }

    init() {
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
        const container = document.getElementById('image-container');
        container.style.width = image.naturalWidth + 'px';
        container.style.height = image.naturalHeight + 'px';
    }

    onImageClick(event) {
        // Remove any existing new marker, so that only one new marker is displayed at a time
        const existingNewMarker = document.querySelector('.new-marker');
        if (existingNewMarker) {
            existingNewMarker.remove();
        }

        // Calculate coordinates
        const rect = event.target.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        document.getElementById('id_x_coordinate').value = x;
        document.getElementById('id_y_coordinate').value = y;

        // Create and place new marker
        const marker = document.createElement('div');
        marker.className = 'marker new-marker';
        marker.style.left = x + '%';
        marker.style.top = y + '%';
        marker.innerHTML = '<span class="marker-number">+</span>';
        document.querySelector('.annotation-container').appendChild(marker);
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