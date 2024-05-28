document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const darkModeToggle = document.getElementById("darkModeToggle");
  const uploadAudioButton = document.getElementById("uploadAudio");
  const fileInput = document.getElementById("fileInput");
  const uploadForm = document.getElementById("uploadForm");
  const uploadMessage = document.getElementById("uploadMessage");
  const processFilesButton = document.getElementById("processFiles");
  const fileList = document.getElementById("fileList");

  darkModeToggle.addEventListener("change", function () {
    body.classList.toggle("dark-mode", this.checked);
    console.log(this.checked ? "Dark mode enabled" : "Dark mode disabled"); // Debugging line
  });

  uploadAudioButton.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", function (event) {
    if (fileInput.files.length > 0) {
      uploadMessage.textContent = "Uploading...";
      uploadMessage.className = "alert alert-info";
      uploadMessage.style.display = "block";
      event.preventDefault();
      submitFormAsynchronously();
      uploadForm.submit();
    }
  });

  uploadForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData(uploadForm);

    fetch("/clear_uploads")
      .then((response) => response.json())
      .then(() => {
        fetch("/", {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then(() => {
            uploadMessage.textContent = "Files uploaded successfully";
            uploadMessage.className = "alert alert-success";
            uploadMessage.style.display = "block";
            processFilesButton.disabled = false;
            updateFileList(fileInput.files);
          })
          .catch((error) => {
            uploadMessage.textContent = "Upload failed";
            uploadMessage.className = "alert alert-danger";
            uploadMessage.style.display = "block";
          });
      })
      .catch((error) => {
        uploadMessage.textContent = "Failed to clear uploads directory";
        uploadMessage.className = "alert alert-danger";
        uploadMessage.style.display = "block";
      });
  });

  processFilesButton.addEventListener("click", function () {
    processFilesButton.disabled = true;
    uploadAudioButton.disabled = true;
    uploadMessage.textContent = "Processing files...";
    uploadMessage.className = "alert alert-info";
    uploadMessage.style.display = "block";
    fetch("/process")
      .then((response) => response.json())
      .then(() => {
        uploadMessage.textContent =
          "Processing completed. Downloading files...";
        uploadMessage.className = "alert alert-success";
        uploadMessage.style.display = "block";
        window.location.href = "/download";
        uploadAudioButton.disabled = false;
      })
      .catch((error) => {
        uploadMessage.textContent = "Processing failed";
        uploadMessage.className = "alert alert-danger";
        uploadMessage.style.display = "block";
        uploadAudioButton.disabled = false;
      });
  });

  function updateFileList(files) {
    fileList.innerHTML = "";
    Array.from(files).forEach((file) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item";
      listItem.textContent = file.name;
      fileList.appendChild(listItem);
    });
  }
});
