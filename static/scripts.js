// static/scripts.js
document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const darkModeToggle = document.getElementById("darkModeToggle");
  const uploadAudioButton = document.getElementById("uploadAudio");
  const fileInput = document.getElementById("fileInput");
  const uploadForm = document.getElementById("uploadForm");
  const uploadMessage = document.getElementById("uploadMessage");
  const transcribeFilesButton = document.getElementById("transcribeFiles");
  const fileList = document.getElementById("fileList");

  darkModeToggle.addEventListener("change", function () {
    body.classList.toggle("dark-mode", this.checked);
    console.log(this.checked ? "Dark mode enabled" : "Dark mode disabled");
  });

  uploadAudioButton.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", function (event) {
    if (fileInput.files.length > 0) {
      uploadMessage.textContent = "Files selected, ready to upload.";
      uploadMessage.className = "alert alert-info";
      uploadMessage.style.display = "block";
      transcribeFilesButton.disabled = false; // Enable the button after files are selected
    }
  });

  uploadForm.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const formData = new FormData(uploadForm);

    fetch("/clear_uploads")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Clear uploads failed: ${response.statusText}`);
        }
        return response.json();
      })
      .then(() => {
        fetch("/", {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Upload failed: ${response.statusText}`);
            }
            return response.json();
          })
          .then(() => {
            uploadMessage.textContent = "Files uploaded successfully";
            uploadMessage.className = "alert alert-success";
            uploadMessage.style.display = "block";
            transcribeFilesButton.disabled = false;
            updateFileList(fileInput.files);
          })
          .catch((error) => {
            console.error(error);
            uploadMessage.textContent = "Upload failed";
            uploadMessage.className = "alert alert-danger";
            uploadMessage.style.display = "block";
          });
      })
      .catch((error) => {
        console.error(error);
        uploadMessage.textContent = "Failed to clear uploads directory";
        uploadMessage.className = "alert alert-danger";
        uploadMessage.style.display = "block";
      });
  });

  transcribeFilesButton.addEventListener("click", function () {
    transcribeFilesButton.disabled = true;
    uploadAudioButton.disabled = true;
    uploadMessage.textContent = "Transcribing files...";
    uploadMessage.className = "alert alert-info";
    uploadMessage.style.display = "block";
    fetch("/process")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Transcribe files failed: ${response.statusText}`);
        }
        return response.json();
      })
      .then(() => {
        uploadMessage.textContent =
          "Transcription completed. Downloading files...";
        uploadMessage.className = "alert alert-success";
        uploadMessage.style.display = "block";
        window.location.href = "/download";
        uploadAudioButton.disabled = false;
      })
      .catch((error) => {
        console.error(error);
        uploadMessage.textContent = "Transcription failed";
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
