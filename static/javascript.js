const currentDate = new Date();
const currentYear = currentDate.getFullYear();
const startOfYear = new Date(currentYear, 0, 1);
const millisecondsInWeek = 604800000;

const weeksInYear = Math.ceil((currentDate - startOfYear) / millisecondsInWeek);

const weekOutputElement = document.getElementById("week-output");
weekOutputElement.textContent = "KW " + weeksInYear;

$(function () {
  $("#assignForm").on("submit", function (event) {
    // Prevent the default form submission
    event.preventDefault();

    // Get the form data
    const formData = $(this).serialize();

    // Manually add startDate and endDate to the form data
    const startDate = $('input[name="datefilter"]')
      .data("daterangepicker")
      .startDate.format("YYYY-MM-DD");
    const endDate = $('input[name="datefilter"]')
      .data("daterangepicker")
      .endDate.format("YYYY-MM-DD");
    const year = $('input[name="datefilter"]')
      .data("daterangepicker")
      .startDate.year();

    // Add other form fields here
    const personal_nr = $('select[name="personal_nr"]').val();
    const project_id = $('select[name="project_id"]').val();
    const car_id = $('select[name="car_id"]').val();
    const ort = $('select[name="ort"]').val();
    const extra1 = $('select[name="extra1"]').val();
    const extra2 = $('select[name="extra2"]').val();
    const extra3 = $('select[name="extra3"]').val();
    const hinweis = $('textarea[name="hinweis"]').val();

    // Extend the form data with additional fields
    const extendedFormData = `${formData}&startDate=${startDate}&endDate=${endDate}&year=${year}&personal_nr=${personal_nr}&project_id=${project_id}&car_id=${car_id}&ort=${ort}&extra1=${extra1}&extra2=${extra2}&extra3=${extra3}&hinweis=${hinweis}`;

    // Send the extended form data to the Python backend using AJAX
    $.ajax({
      url: "/assign_mitarbeiter",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        // Handle the response from the Python backend
        alert("Mitarbeiter erfolgreich zugewiesen!")
        window.location.reload();
      },
      error: function (xhr, status, error) {
        // Handle the error
      },
    });
  });

  $('input[name="datefilter"]').daterangepicker({
    autoUpdateInput: false,
    locale: {
      cancelLabel: "Clear",
    },
  });

  $('input[name="datefilter"]').on(
    "apply.daterangepicker",
    function (ev, picker) {
      $(this).val(
        picker.startDate.format("YYYY-MM-DD") +
          " - " +
          picker.endDate.format("YYYY-MM-DD")
      );
    }
  );

  $('input[name="datefilter"]').on(
    "cancel.daterangepicker",
    function (ev, picker) {
      $(this).val("");
    }
  );
});

$(document).ready(function () {
  $("#personal_nr_list").chosen();
  $("#dd-m").chosen();
  $("#dd-p").chosen();
  $("#dd-car").chosen();
  $("#dd-l").chosen();
  $("#dd-x").chosen();
  $("#dd-xx").chosen();
  $("#dd-xxx").chosen();

  $("#dd-p-g").chosen();
  $("#dd-car-g").chosen();
  $("#dd-l-g").chosen();
  $("#dd-x-g").chosen();
  $("#dd-xx-g").chosen();
  $("#dd-xxx-g").chosen();
});

$(function () {
  $("#group-form").on("submit", function (event) {
    // Prevent the default form submission
    event.preventDefault();

    // Get the form data
    const formData = $(this).serialize();

    // Manually add startDate and endDate to the form data
    const startDate = $('input[name="datefilter-g"]')
      .data("daterangepicker")
      .startDate.format("YYYY-MM-DD");
    const endDate = $('input[name="datefilter-g"]')
      .data("daterangepicker")
      .endDate.format("YYYY-MM-DD");
    const year = $('input[name="datefilter-g"]')
      .data("daterangepicker")
      .startDate.year();

    // Add other form fields here
    const project_id = $('select[name="project_id"]').val();
    const car_id = $('select[name="car_id"]').val();
    const ort = $('select[name="ort"]').val();
    const extra1 = $('select[name="extra1"]').val();
    const extra2 = $('select[name="extra2"]').val();
    const extra3 = $('select[name="extra3"]').val();
    const hinweis = $('textarea[name="hinweis"]').val();

    // Get the selected personal_nr_list as an array
    const personal_nr_list = $('select[name="personal_nr_list"]').val();

    // Check if personal_nr_list is not empty
    if (!personal_nr_list || personal_nr_list.length === 0) {
      console.log("Error: personal_nr_list is empty.");
      return; // Prevent further execution
    }

    // Extend the form data with additional fields
    const extendedGroupData = `${formData}&startDate=${startDate}&endDate=${endDate}&year=${year}&project_id=${project_id}&car_id=${car_id}&ort=${ort}&extra1=${extra1}&extra2=${extra2}&extra3=${extra3}&hinweis=${hinweis}`;

    // Set the form token in the session
    const formToken = $("input[name='form_token']").val();
    sessionStorage.setItem("form_token", formToken);

    console.log("Submitting form...");
    // Send the extended form data to the Python backend using AJAX
    $.ajax({
      url: "/assign_group",
      method: "POST",
      data:
        extendedGroupData +
        "&personal_nr_list=" +
        personal_nr_list.join(",") +
        "&form_token=" +
        formToken,
      success: function (response) {
        console.log("Server response:", response);

        alert("Gruppe erfolgreich zugewiesen!");
        window.location.reload();
      },
      error: function (xhr, status, error) {
        // Handle the error
        alert("Gruppe konnte nicht zugewiesen werden..");
      },
    });
  });

  $('input[name="datefilter-g"]').daterangepicker({
    autoUpdateInput: false,
    locale: {
      cancelLabel: "Clear",
    },
  });

  $('input[name="datefilter-g"]').on(
    "apply.daterangepicker",
    function (ev, picker) {
      $(this).val(
        picker.startDate.format("YYYY-MM-DD") +
          " - " +
          picker.endDate.format("YYYY-MM-DD")
      );
    }
  );

  $('input[name="datefilter-g"]').on(
    "cancel.daterangepicker",
    function (ev, picker) {
      $(this).val("");
    }
  );
});

$(function () {
  $(".assignment-cell").click(function () {
    // Check if the clicked cell has data-assignment-id attribute
    var assignmentId = $(this)
      .find("div[data-assignment-id]")
      .data("assignment-id");

    if (assignmentId) {
      $.ajax({
        url: "/get_assignment_hinweis",
        method: "POST",
        data: { assignmentId: assignmentId },
        success: function (response) {
          var hinweis = response.hinweis;
          // Display the hinweis information in a modal or tooltip
          alert(hinweis);
          // You can use a modal library like Bootstrap Modal for a better user experience
        },
        error: function (xhr, status, error) {
          console.log("Kein Hinweis hinterlegt für dieses Assignment");
        },
      });
    }
  });
});

$(document).ready(function () {
  highlightDuplicateGroups();

  function highlightDuplicateGroups() {
    var groupIds = {};
    var groupColors = {};

    // Iterate through each assignment cell
    $(".assignment-cell").each(function () {
      var assignmentId = $(this)
        .find("div[data-assignment-id]")
        .data("assignment-id");
      var groupId = $(this).find("div[data-group-id]").data("group-id");

      if (assignmentId && groupId && groupId !== "0") {
        // Check if the group_id already exists in the groupIds object
        if (!groupColors[groupId]) {
          // Generate a random color for the group
          var color = getRandomColor();

          // Store the color for the group
          groupColors[groupId] = color;
        }

        // Highlight the current assignment cell with the corresponding CSS class
        $(this).css("background-color", groupColors[groupId]);
      }
    });
  }

  // Function to generate a random color
  function getRandomColor() {
    var letters = "0123456789ABCDEF";
    var color = "#";

    // Generate a 6-digit random hexadecimal color code
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }

    return color;
  }
});
