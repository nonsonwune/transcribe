document.addEventListener("DOMContentLoaded", function () {
  const body = document.body;
  const darkModeToggle = document.getElementById("darkModeToggle");
  const uploadAudioButton = document.getElementById("uploadAudio");
  const fileInput = document.getElementById("fileInput");
  const uploadForm = document.getElementById("uploadForm");
  const uploadMessage = document.getElementById("uploadMessage");
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
      updateFileList(fileInput.files);
      uploadMessage.textContent = "Files selected, ready to upload.";
      uploadMessage.className = "alert alert-info";
      uploadMessage.style.display = "block";
      // Directly submit the form when files are selected
      uploadForm.submit();
    }
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
