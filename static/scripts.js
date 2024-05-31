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
    }

    let formData = new FormData();
    $.each(files, function (i, file) {
      formData.append("files", file);
    });

    $.ajax({
      url: "/check_status",
      type: "GET",
      success: function (response) {
        if (response.transcription_in_progress) {
          alert("A transcription is already in progress.");
          return;
        }

        $("#statusMessage").text("Transcribing Audio....").show();
        $("#transcribeButton").prop("disabled", true);
        $(".lds-circle").show(); // Show the spinner

        $.ajax({
          url: "/",
          type: "POST",
          data: formData,
          contentType: false,
          processData: false,
          success: function (response) {
            $("#statusMessage").text(
              "Files uploaded successfully. Preparing download link..."
            );
            sessionId = response.session_id;
            $("#sessionId").val(sessionId);
            downloadFiles(sessionId);
          },
          error: function (response) {
            $("#statusMessage").text("Failed to upload files.");
            $("#transcribeButton").prop("disabled", false);
            $(".lds-circle").hide(); // Hide the spinner on error
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
        $("#statusMessage").text(
          "Transcription complete. You can download the files now."
        );
        $("#downloadLink").show();
        $(".lds-circle").hide(); // Hide the spinner on success
        $("#transcribeButton").prop("disabled", false);
      },
      error: function () {
        $("#statusMessage").text("Failed to complete transcription.");
        $("#transcribeButton").prop("disabled", false);
        $(".lds-circle").hide(); // Hide the spinner on error
      },
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
