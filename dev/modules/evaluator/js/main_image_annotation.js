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

    document.getElementById('edit-annotation').addEventListener('click', function(event) {
        event.preventDefault();
        showEditForm(event);
    });

    document.getElementById('delete-annotation').addEventListener('click', function(event) {
        event.preventDefault();
        deleteAnnotation(event);
    });

    document.querySelector('.close').addEventListener('click', function() {
        document.getElementById('annotationModal').style.display = 'none';
        resetModal();
    });

    window.addEventListener('click', function(event) {
        if (event.target == document.getElementById('annotationModal')) {
            document.getElementById('annotationModal').style.display = 'none';
            resetModal();
        }
    });

    function toggleEditMode(editMode) {
        if (editMode) {
            document.getElementById('annotation-text').style.display = 'none';
            document.getElementById('annotation-edit-text').style.display = 'block';
            document.getElementById('edit-annotation').style.display = 'none';
            document.getElementById('save-annotation').style.display = 'block';
            document.getElementById('delete-annotation').style.display = 'none';
        } else {
            document.getElementById('annotation-text').style.display = 'block';
            document.getElementById('annotation-edit-text').style.display = 'none';
            document.getElementById('edit-annotation').style.display = 'block';
            document.getElementById('save-annotation').style.display = 'none';
            document.getElementById('delete-annotation').style.display = 'block';
        }
    }

    function resetModal() {
        toggleEditMode(false);
        document.getElementById('annotation-edit-text').value = '';
    }

    function showEditForm(event) {
        const annotationId = event.target.closest('.icon-button').dataset.id;
        fetch(`/evaluator/api/annotations/${annotationId}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('annotation-text').style.display = 'none';
                document.getElementById('annotation-edit-text').value = data.annotation_text;
                document.getElementById('annotation-edit-text').style.display = 'block';
                document.getElementById('save-annotation').style.display = 'block';
                document.getElementById('edit-annotation').style.display = 'none';
                document.getElementById('delete-annotation').style.display = 'none';
            });
    }

    function deleteAnnotation(event) {
        const annotationId = event.target.closest('.icon-button').dataset.id;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
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
});

new MainImageAnnotation();