document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const darkModeToggle = document.getElementById("darkModeToggle");
  const uploadAudioButton = document.getElementById("uploadAudio");
  const fileInput = document.getElementById("fileInput");
  const uploadForm = document.getElementById("uploadForm");
  const uploadMessage = document.getElementById("uploadMessage");
  const fileList = document.getElementById("fileList");
  const transcribeFilesButton = document.getElementById("transcribeFiles");
  const downloadFilesButton = document.getElementById("downloadFiles");

  darkModeToggle.addEventListener("change", function () {
    body.classList.toggle("dark-mode", this.checked);
    console.log(this.checked ? "Dark mode enabled" : "Dark mode disabled");
  });

  uploadAudioButton.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", function (event) {
    if (fileInput.files.length > 0) {
      updateFileList(fileInput.files);
      uploadMessage.textContent = "Files selected, ready to upload.";
      uploadMessage.className = "alert alert-info";
      uploadMessage.style.display = "block";
      transcribeFilesButton.style.display = "block"; // Show the transcribe button
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
        return fetch("/", {
          method: "POST",
          body: formData,
        });
      })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        return response.json();
      })
      .then(() => {
        uploadMessage.textContent =
          "Files uploaded successfully. Ready to transcribe.";
        uploadMessage.className = "alert alert-success";
        uploadMessage.style.display = "block";
        transcribeFilesButton.style.display = "block"; // Show the transcribe button
      })
      .catch((error) => {
        console.error(error);
        uploadMessage.textContent = "Upload failed.";
        uploadMessage.className = "alert alert-danger";
        uploadMessage.style.display = "block";
      });
  });

  transcribeFilesButton.addEventListener("click", function () {
    transcribeFilesButton.disabled = true;
    uploadMessage.textContent = "Transcription in progress...";
    uploadMessage.className = "alert alert-info";
    uploadMessage.style.display = "block";

    fetch("/process")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Transcription failed: ${response.statusText}`);
        }
        return response.json();
      })
      .then(() => {
        uploadMessage.textContent = "Transcription completed.";
        uploadMessage.className = "alert alert-success";
        uploadMessage.style.display = "block";
        downloadFilesButton.style.display = "block"; // Show the download button
      })
      .catch((error) => {
        console.error(error);
        uploadMessage.textContent = "Transcription failed.";
        uploadMessage.className = "alert alert-danger";
        uploadMessage.style.display = "block";
        transcribeFilesButton.disabled = false;
      });
  });

  downloadFilesButton.addEventListener("click", function () {
    window.location.href = "/download";
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
