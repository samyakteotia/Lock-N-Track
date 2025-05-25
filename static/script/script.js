document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mainForm');
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('fileInfo');
    const passwordContainer = document.getElementById('passwordContainer');
    const hashContainer = document.getElementById('hashContainer');
    const operationRadios = document.querySelectorAll('input[name="operation"]');
    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const fileSize = formatFileSize(file.size);
            fileInfo.innerHTML = `
                <strong>Selected File:</strong> ${file.name}<br>
                <strong>Size:</strong> ${fileSize}
            `;
            fileInfo.style.display = 'block';
        } else {
            fileInfo.style.display = 'none';
        }
    });
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Show/hide password and hash fields based on operation
    operationRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            passwordContainer.style.display = 'none';
            hashContainer.style.display = 'none';
            
            if (this.value === 'encrypt' || this.value === 'decrypt') {
                passwordContainer.style.display = 'block';
            } else if (this.value === 'revert') {
                hashContainer.style.display = 'block';
            }
        });
    });
    
    // Form validation
    form.addEventListener('submit', function(e) {
        const selectedOperation = document.querySelector('input[name="operation"]:checked');
        
        if (!selectedOperation) {
            alert('Please select an operation');
            e.preventDefault();
            return;
        }
        
        const operation = selectedOperation.value;
        
        // Validate file requirement
        if (['encrypt', 'decrypt', 'compress', 'decompress'].includes(operation)) {
            if (!fileInput.files || fileInput.files.length === 0) {
                alert('Please select a file for this operation');
                e.preventDefault();
                return;
            }
        }
        
        // Validate password requirement
        if ((operation === 'encrypt' || operation === 'decrypt') && 
            !document.getElementById('password').value) {
            alert('Password is required for this operation');
            e.preventDefault();
            return;
        }
        
        // Validate hash requirement
        if (operation === 'revert' && !document.getElementById('hash_digest').value) {
            alert('Snapshot hash is required for revert');
            e.preventDefault();
            return;
        }
    });
});