// Utility functions for cookies
function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function deleteCookie(name) {
  document.cookie = name + "=; Max-Age=-99999999; path=/";
}

$(document).ready(function () {
  var darkMode = getCookie("dark_mode");
  if (darkMode === "true") {
    $("#darkModeToggle").prop("checked", true);
    $("body").addClass("dark-mode");
  } else {
    $("#darkModeToggle").prop("checked", false);
    $("body").removeClass("dark-mode");
  }

  $("#darkModeToggle").on("change", function () {
    var darkModeValue = $(this).is(":checked") ? "true" : "false";
    setCookie("dark_mode", darkModeValue, 7);
    if (darkModeValue === "true") {
      $("body").addClass("dark-mode");
    } else {
      $("body").removeClass("dark-mode");
    }
  });

  let files;
  let sessionId = getCookie("session_id");

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

    // Clear previous session data
    deleteCookie("session_id");

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

        // Add session ID to formData
        formData.append("session_id", sessionId);

        $.ajax({
          url: "/",
          type: "POST",
          data: formData,
          contentType: false,
          processData: false,
          success: function (response) {
            $("#statusMessage").text("Transcribing...").show();
            sessionId = response.session_id;
            setCookie("session_id", sessionId, 1); // Set session ID in cookie for 1 day
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
