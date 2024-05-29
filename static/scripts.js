$(document).ready(function () {
  $("#uploadForm").on("submit", function (e) {
    e.preventDefault();

    var formData = new FormData();
    var files = $("#audioFiles")[0].files;

    if (files.length === 0) {
      alert("Please select at least one file.");
      return;
    }

    for (var i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    $("#uploadStatus").text("Uploading...").show();

    $.ajax({
      url: "/",
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        $("#uploadStatus").text(response.message);
        if (response.message === "Files uploaded and processed successfully") {
          $("#transcribeBtn").show();
        }
      },
      error: function (response) {
        $("#uploadStatus").text("Error uploading files").show();
      },
    });
  });

  $("#transcribeBtn").on("click", function () {
    $("#transcriptionStatus").text("Transcribing...").show();

    $.ajax({
      url: "/download",
      type: "GET",
      success: function (response) {
        $("#transcriptionStatus").text("Transcription complete.").show();
        $("#downloadBtn").show();
      },
      error: function (response) {
        $("#transcriptionStatus").text("Error during transcription.").show();
      },
    });
  });

  $("#downloadBtn").on("click", function () {
    window.location.href = "/download";
  });

  $("#darkModeToggle").on("change", function () {
    $("body").toggleClass("dark-mode");
  });
});
