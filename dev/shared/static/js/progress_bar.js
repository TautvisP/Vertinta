// probably not the right place for this File, but it works for now
// shared/static/js/progress_bar.js

document.addEventListener('DOMContentLoaded', function () {
    const steps = document.querySelectorAll('.progress-bar-step');
    const lines = document.querySelectorAll('.progress-bar-line');
    const prevButton = document.getElementById('prev-step');
    const nextButton = document.getElementById('next-step');
    let currentStep = parseInt(document.querySelector('.progress-bar-current').textContent);

    function updateProgressBar() {
        steps.forEach((step, index) => {
            if (index < currentStep - 1) {
                step.classList.add('progress-bar-completed');
                step.classList.remove('progress-bar-current');
            } else if (index === currentStep - 1) {
                step.classList.add('progress-bar-current');
                step.classList.remove('progress-bar-completed');
            } else {
                step.classList.remove('progress-bar-completed', 'progress-bar-current');
            }
        });

        lines.forEach((line, index) => {
            if (index < currentStep - 1) {
                line.classList.add('progress-bar-completed');
            } else {
                line.classList.remove('progress-bar-completed');
            }
        });
    }

    prevButton.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateProgressBar();
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentStep < steps.length) {
            currentStep++;
            updateProgressBar();
        }
    });

    updateProgressBar();
});