document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const button = document.querySelector('button');
    const fileInput = document.querySelector('input[type="file"]');

    if (!form) return;

    form.addEventListener('submit', (e) => {
        const file = fileInput.files[0];

        if (!file) {
            alert("Please upload an ultrasound image for analysis.");
            e.preventDefault();
            return;
        }

        button.innerHTML = "⏳ Processing...";
        button.style.backgroundColor = "#006666";
        button.style.cursor = "wait";
        button.disabled = true;
    });

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        const allowedTypes = ["image/jpeg", "image/png"];

        if (file && !allowedTypes.includes(file.type)) {
            alert("Invalid file type. Please upload JPG or PNG.");
            this.value = "";
            return;
        }

        if (file && file.size > 5 * 1024 * 1024) {
            alert("File size must be less than 5MB.");
            this.value = "";
        }
    });
});