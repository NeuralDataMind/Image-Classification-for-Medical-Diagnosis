// Log message to check if JS is working
console.log("Upload page loaded");

// Select elements
const fileInput = document.querySelector('input[type="file"]');
const uploadBox = document.querySelector('.upload-box');
const successMessage = document.createElement("p"); // Create a message element

// Success message styling
successMessage.innerHTML = "✅ Image uploaded successfully!";
successMessage.style.display = "none"; // Initially hidden
successMessage.style.fontSize = "1rem";
successMessage.style.color = "#4CAF50"; // Soft green color matching the theme
successMessage.style.fontWeight = "bold";
successMessage.style.marginTop = "10px";

// Insert success message after the upload box
uploadBox.parentNode.insertBefore(successMessage, uploadBox.nextSibling);

// Listen for file selection
fileInput.addEventListener("change", function (event) {
    let file = event.target.files[0];

    if (file) {
        console.log("Selected file:", file.name);

        // Hide upload box and show success message
        uploadBox.style.display = "none";  
        successMessage.style.display = "block";  
    }
});
