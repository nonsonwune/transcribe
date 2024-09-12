<<<<<<< HEAD
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
=======
$(document).ready(function () {
  // Check the session for dark mode preference
  $.ajax({
    url: "/get_dark_mode",
    type: "GET",
    success: function (response) {
      if (response.dark_mode === "true") {
        $("#darkModeToggle").prop("checked", true);
        $("body").addClass("dark-mode");
      } else {
        $("#darkModeToggle").prop("checked", false);
        $("body").removeClass("dark-mode");
      }
    },
>>>>>>> sankofa
  });

  $("#darkModeToggle").on("change", function () {
    $.ajax({
      url: "/set_dark_mode",
      type: "POST",
      data: { dark_mode: $(this).is(":checked") ? "true" : "false" },
      success: function (response) {
        if (response.dark_mode === "true") {
          $("body").addClass("dark-mode");
        } else {
          $("body").removeClass("dark-mode");
        }
      },
    });
  });

<<<<<<< HEAD
  fileInput.addEventListener("change", function (event) {
    if (fileInput.files.length > 0) {
      updateFileList(fileInput.files);
      uploadMessage.textContent = "Files selected, ready to upload.";
      uploadMessage.className = "alert alert-info";
      uploadMessage.style.display = "block";
      transcribeFilesButton.style.display = "block"; // Show the transcribe button
=======
  let files;
  let sessionId;

  $("#audioFile").on("change", function () {
    files = this.files;
    $("#fileName").text(files.length > 0 ? files[0].name : "");
    $("#transcribeButton").prop("disabled", files.length === 0);
  });

  $("#uploadForm").on("submit", function (e) {
    e.preventDefault();
    if (!files) {
      alert("Please select a file first.");
      return;
>>>>>>> sankofa
    }

    let formData = new FormData();
    $.each(files, function (i, file) {
      formData.append("files", file);
    });

    $("#statusMessage").text("Checking status...").show();
    $.ajax({
      url: "/check_status",
      type: "GET",
      success: function (response) {
        if (response.transcription_in_progress) {
          alert("A transcription is already in progress.");
          return;
        }

        $("#statusMessage")
          .text("Your audio recording is being transcribed, please wait....")
          .show();
        $("#transcribeButton").prop("disabled", true);
        $("#transcribeButton").text("Transcribing").show();
        $(".lds-circle").show(); // Show the spinner

        $.ajax({
          url: "/",
          type: "POST",
          data: formData,
          contentType: false,
          processData: false,
          success: function (response) {
            $("#statusMessage").text("Transcribing...").show();
            sessionId = response.session_id;
            $("#sessionId").val(sessionId);
            $("#statusMessage").text("Preparing download link...").show();
            downloadFiles(sessionId);
          },
          error: function (response) {
            $("#statusMessage").text("Failed to upload files.");
            $("#transcribeButton").prop("disabled", false);
            $("#transcribeButton").text("Transcribe").show();
            $(".lds-circle").hide(); // Hide the spinner on error
          },
        });
<<<<<<< HEAD
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
=======
      },
    });
  });

  function downloadFiles(sessionId) {
    $.ajax({
      url: "/download?session_id=" + sessionId,
      type: "GET",
      success: function () {
        $("#statusMessage")
          .text("Transcription complete. You can download the files now.")
          .show();
        $("#downloadLink").show();
        $(".lds-circle").hide(); // Hide the spinner on success
        $("#transcribeButton").prop("disabled", false);
        $("#transcribeButton").text("Transcribe").show();
      },
      error: function () {
        $("#statusMessage").text("Failed to complete transcription.");
        $("#transcribeButton").prop("disabled", false);
        $(".lds-circle").hide(); // Hide the spinner on error
      },
>>>>>>> sankofa
    });
  }

  window.onbeforeunload = function () {
    $.ajax({
      url: "/cancel_transcription",
      type: "POST",
      async: false, // Synchronous request
      success: function (response) {
        console.log(response.message);
      },
      error: function () {
        console.log("Failed to cancel transcription.");
      },
    });
  };

  $("#downloadLink").on("click", function (e) {
    e.preventDefault();
    window.location.href = "/download?session_id=" + $("#sessionId").val();
  });
});
