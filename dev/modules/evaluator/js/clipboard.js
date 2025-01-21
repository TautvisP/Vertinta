function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            console.log('Text copied to clipboard:', text);
            alert('Vieta nukopijuota į iškarpinę: ' + text);
        }, function(err) {
            console.error('Klaida kopijuojant vietą: ', err);
        });
    } else {
        // Fallback method for different browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        try {
            document.execCommand('copy');
            console.log('Text copied to clipboard using fallback method:', text);
            alert('Vieta nukopijuota į iškarpinę: ' + text);
        } catch (err) {
            console.error('Klaida kopijuojant vietą: ', err);
        }
        document.body.removeChild(textarea);
    }
}

window.copyToClipboard = copyToClipboard;