$(document).ready(function () {
  $("#darkModeToggle").on("change", function () {
    $("body").toggleClass("dark-mode");
  });

  let files;

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

    $("#statusMessage").text("Transcribing Audio....").show();
    $("#transcribeButton").prop("disabled", true);

    $.ajax({
      url: "/",
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        $("#statusMessage").text("Files uploaded successfully.");
        transcribe();
      },
      error: function (response) {
        $("#statusMessage").text("Failed to upload files.");
        $("#transcribeButton").prop("disabled", false);
      },
    });
  });

  function transcribe() {
    $.ajax({
      url: "/clear_uploads",
      type: "GET",
      success: function (response) {
        $("#statusMessage").text("Preparing download Link...");

        // Simulate long process
        setTimeout(function () {
          $.ajax({
            url: "/download",
            type: "GET",
            success: function () {
              $("#statusMessage").text(
                "Transcription complete. You can download the files now."
              );
              $("#downloadLink").show();
            },
            error: function () {
              $("#statusMessage").text("Failed to complete transcription.");
              $("#transcribeButton").prop("disabled", false);
            },
          });
        }, 5000);
      },
      error: function (response) {
        $("#statusMessage").text("Failed to clear uploads.");
        $("#transcribeButton").prop("disabled", false);
      },
    });
  }

  $("#downloadLink").on("click", function (e) {
    e.preventDefault();
    window.location.href = "/download";
  });
});
