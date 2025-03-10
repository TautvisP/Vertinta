document.querySelectorAll('.copy-link-button').forEach(button => {
    button.addEventListener('click', function() {
        const link = this.getAttribute('data-link');
        navigator.clipboard.writeText(link).then(() => {
            alert('Nuoroda nukopijuota!');
        });
    });
});

document.querySelectorAll('.open-comment-modal-button').forEach(button => {
    button.addEventListener('click', function() {
        const comment = this.getAttribute('data-comment');
        document.getElementById('commentText').textContent = comment;
        document.getElementById('commentModal').style.display = 'block';
    });
});

document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('commentModal').style.display = 'none';
});

window.addEventListener('click', function(event) {
    if (event.target == document.getElementById('commentModal')) {
        document.getElementById('commentModal').style.display = 'none';
    }
});