const fileInput = document.getElementById("file-input");
const preview = document.getElementById("preview");
const dropText = document.getElementById("drop-text");
const btnAnalyze = document.getElementById("btn-analyze");

fileInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = "block";
        dropText.style.display = "none";
    };
    reader.readAsDataURL(file);
});

document.body.addEventListener("htmx:responseError", function (e) {
    const container = document.getElementById("form-container");
    container.innerHTML = `<div class="error">${e.detail.xhr.responseText}</div>`;
});

document.body.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.id === "confirmation-container") {
        document.getElementById("form-container").innerHTML = "";
    }
});