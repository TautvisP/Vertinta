document.addEventListener('DOMContentLoaded', function() {

    if (document.getElementById('reject-form')) {
        window.showRejectForm = function() {
            document.getElementById('reject-form').style.display = 'block';
        };
        
        window.hideRejectForm = function() {
            document.getElementById('reject-form').style.display = 'none';
        };
    }
    
});