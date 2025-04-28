document.getElementById("upload-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    let formData = new FormData(this);
    let response = await fetch("/predict-pneumonia", {
        method: "POST",
        body: formData,
    });

    let data = await response.json();

    if (data.prediction) {
        localStorage.setItem("image_path", data.image_path);
        localStorage.setItem("prediction", data.prediction);
        window.location.href = "result.html";  // Redirect to results page
    } else {
        alert("Error: " + data.error);
    }
});
