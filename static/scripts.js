$(document).ready(function () {
  const body = $("body");
  const darkModeToggle = $("#darkModeToggle");
  const uploadForm = $("#uploadForm");
  const statusMessage = $("#statusMessage");
  const transcribeButton = $("#transcribeButton");
  const downloadLink = $("#downloadLink");
  const audioFileInput = $("#audioFile");
  const fileName = $("#fileName");
  const sessionIdInput = $("#sessionId");

  let files;
  let sessionId;

  // Check the session for dark mode preference
  $.ajax({
    url: "/get_dark_mode",
    type: "GET",
    success: function (response) {
      darkModeToggle.prop("checked", response.dark_mode === "true");
      body.toggleClass("dark-mode", response.dark_mode === "true");
    },
  });

  darkModeToggle.on("change", function () {
    const isDarkMode = $(this).is(":checked");
    $.ajax({
      url: "/set_dark_mode",
      type: "POST",
      data: { dark_mode: isDarkMode ? "true" : "false" },
      success: function (response) {
        body.toggleClass("dark-mode", response.dark_mode === "true");
      },
    });
  });

  audioFileInput.on("change", function () {
    files = this.files;
    fileName.text(files.length > 0 ? files[0].name : "");
    transcribeButton.prop("disabled", files.length === 0);
  });

  uploadForm.on("submit", function (e) {
    e.preventDefault();
    if (!files) {
      alert("Please select a file first.");
      return;
    }

    let formData = new FormData();
    $.each(files, function (i, file) {
      formData.append("files", file);
    });

    statusMessage.text("Checking status...").show();
    $.ajax({
      url: "/check_status",
      type: "GET",
      success: function (response) {
        if (response.transcription_in_progress) {
          alert("A transcription is already in progress.");
          return;
        }

        statusMessage
          .text("Your audio recording is being transcribed, please wait....")
          .show();
        transcribeButton.prop("disabled", true).text("Transcribing").show();
        $(".lds-circle").show();

        $.ajax({
          url: "/",
          type: "POST",
          data: formData,
          contentType: false,
          processData: false,
          success: function (response) {
            statusMessage.text("Transcribing...").show();
            sessionId = response.session_id;
            sessionIdInput.val(sessionId);
            statusMessage.text("Preparing download link...").show();
            downloadFiles(sessionId);
          },
          error: function () {
            statusMessage.text("Failed to upload files.");
            transcribeButton.prop("disabled", false).text("Transcribe").show();
            $(".lds-circle").hide();
          },
        });
      },
    });
  });

  function downloadFiles(sessionId) {
    $.ajax({
      url: "/download?session_id=" + sessionId,
      type: "GET",
      success: function () {
        statusMessage
          .text("Transcription complete. You can download the files now.")
          .show();
        downloadLink.show();
        $(".lds-circle").hide();
        transcribeButton.prop("disabled", false).text("Transcribe").show();
      },
      error: function () {
        statusMessage.text("Failed to complete transcription.");
        transcribeButton.prop("disabled", false);
        $(".lds-circle").hide();
      },
    });
  }

  window.onbeforeunload = function () {
    $.ajax({
      url: "/cancel_transcription",
      type: "POST",
      async: false,
      success: function (response) {
        console.log(response.message);
      },
      error: function () {
        console.log("Failed to cancel transcription.");
      },
    });
  };

  downloadLink.on("click", function (e) {
    e.preventDefault();
    window.location.href = "/download?session_id=" + sessionIdInput.val();
  });
});
