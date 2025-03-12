document.getElementById('openModal').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('uploadModal').style.display = 'block';
});
document.querySelectorAll('.close').forEach(closeButton => {
    closeButton.addEventListener('click', function() {
        document.getElementById('uploadModal').style.display = 'none';
        document.getElementById('editCommentModal').style.display = 'none';
    });
});
window.addEventListener('click', function(event) {
    if (event.target == document.getElementById('uploadModal')) {
        document.getElementById('uploadModal').style.display = 'none';
    }
    if (event.target == document.getElementById('editCommentModal')) {
        document.getElementById('editCommentModal').style.display = 'none';
    }
});

// Setup drop area for file upload
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

// Edit comment functionality
document.querySelectorAll('.edit-comment-button').forEach(button => {
    button.addEventListener('click', function() {
        const documentId = this.getAttribute('data-id');
        const comment = this.getAttribute('data-comment');
        document.getElementById('editDocumentId').value = documentId;
        document.getElementById('editComment').value = comment;
        document.getElementById('editCommentModal').style.display = 'block';
    });
});

document.getElementById('editCommentForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const updateUrl = document.getElementById('editCommentModal').getAttribute('data-update-url');
    fetch(updateUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload();
        } else {
            alert('Error updating comment');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating comment');
    });
});