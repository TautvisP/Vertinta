document.addEventListener('DOMContentLoaded', function() {
    // Copy link buttons
    document.querySelectorAll('.copy-link-button').forEach(button => {
        button.addEventListener('click', function() {
            const link = this.getAttribute('data-link');
            navigator.clipboard.writeText(link).then(() => {
                alert('Nuoroda nukopijuota!');
            });
        });
    });

    // Open comment modal
    document.querySelectorAll('.open-comment-modal-button').forEach(button => {
        button.addEventListener('click', function() {
            const comment = this.getAttribute('data-comment');
            document.getElementById('commentText').textContent = comment;
            document.getElementById('commentModal').style.display = 'block';
        });
    });

    // Close comment modal - make sure this selector is precise
    document.querySelectorAll('#commentModal .close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            document.getElementById('commentModal').style.display = 'none';
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('commentModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});