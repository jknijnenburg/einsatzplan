const currentDate = new Date();
const currentYear = currentDate.getFullYear();
const startOfYear = new Date(currentYear, 0, 1);
const millisecondsInWeek = 604800000;

const weeksInYear = Math.ceil((currentDate - startOfYear) / millisecondsInWeek);

const weekOutputElement = document.getElementById("week-output");
weekOutputElement.textContent = "KW " + weeksInYear;

function getNumberOfWeek(date) {
  const specific_date = new Date(date);
  const firstDayOfYear = new Date(specific_date.getFullYear(), 0, 1);
  const pastDaysOfYear = (specific_date - firstDayOfYear) / 86400000;
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
}

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
    const week_id = getNumberOfWeek(startDate);

    // Add other form fields here
    const personal_nr = $('select[name="personal_nr"]').val();
    const project_id = $('select[name="project_id"]').val();
    const car_id = $('select[name="car_id"]').val();
    const ort = $('select[name="ort"]').val();
    const extra1 = $('select[name="extra1"]').val();
    const extra2 = $('select[name="extra2"]').val();
    const extra3 = $('select[name="extra3"]').val();
    const hinweis = $('textarea[name="hinweis"]').val();

    const checkedRadioButton = $("input[name='abw']:checked").val();

    // Extend the form data with additional fields
    const extendedFormData = `${formData}&startDate=${startDate}&endDate=${endDate}&year=${year}&week_id=${week_id}&personal_nr=${personal_nr}&project_id=${project_id}&car_id=${car_id}&ort=${ort}&extra1=${extra1}&extra2=${extra2}&extra3=${extra3}&hinweis=${hinweis}&checkedRadioButton=${checkedRadioButton}`;

    // Send the extended form data to the Python backend using AJAX
    $.ajax({
      url: "/assign_mitarbeiter",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        // Handle the response from the Python backend
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        // Handle the error
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
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

// DESIGN
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

// ASSIGN GROUP
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
    const week_id = getNumberOfWeek(startDate);

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
    const extendedGroupData = `${formData}&startDate=${startDate}&endDate=${endDate}&year=${year}&week_id=${week_id}&project_id=${project_id}&car_id=${car_id}&ort=${ort}&extra1=${extra1}&extra2=${extra2}&extra3=${extra3}&hinweis=${hinweis}`;

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

        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        // Handle the error
        alert("Gruppe konnte nicht zugewiesen werden.." + error);
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

// Add Data & Delete Data
$(function () {
  $("#submit_m_add").on("submit", function (event) {
    // Prevent the default form submission
    event.preventDefault();

    // Get the form data
    const formData = $(this).serialize();

    const personal_nr = $('input[name="personal_nr"]').val();
    const vorname = $('input[name="vorname"]').val();
    const nachname = $('input[name="nachname"]').val();
    const bereich = $('select[name="bereich"]').val();

    const extendedFormData = `${formData}&personal_nr=${personal_nr}&vorname=${vorname}&nachname=${nachname}&bereich=${bereich}`;

    $.ajax({
      url: "/submit_m_add",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        // Handle the response from the Python backend
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        // Handle the error
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_c_add").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const customer_id = $('input[name="customer_id"]').val();
    const customer_name = $('input[name="customer_name"]').val();

    const extendedFormData = `${formData}&customer_id=${customer_id}&customer_name=${customer_name}`;

    $.ajax({
      url: "/submit_c_add",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_p_add").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const project_id = $('input[name="project_id"]').val();
    const project_name = $('input[name="project_name"]').val();
    const customer_id = $('select[name="customer_id"]').val();

    const extendedFormData = `${formData}&project_id=${project_id}&project_name=${project_name}&customer_id=${customer_id}`;

    $.ajax({
      url: "/submit_p_add",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_car_add").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const car_id = $('input[name="car_id"]').val();

    const extendedFormData = `${formData}&car_id=${car_id}`;

    $.ajax({
      url: "/submit_car_add",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_extra_add").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const extra_id = $('input[name="extra_id"]').val();
    const extra_name = $('input[name="extra_name"]').val();

    const extendedFormData = `${formData}&extra_id=${extra_id}&extra_name=${extra_name}`;

    $.ajax({
      url: "/submit_e_add",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  // DELETE DATA
  $("#submit_m_delete").on("submit", function (event) {
    // Prevent the default form submission
    event.preventDefault();

    // Get the form data
    const formData = $(this).serialize();

    const personal_nr = $('select[name="personal_nr"]').val();

    const extendedFormData = `${formData}&personal_nr=${personal_nr}`;

    $.ajax({
      url: "/submit_m_delete",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        // Handle the response from the Python backend
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        // Handle the error
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_c_delete").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const customer_id = $('input[name="kunden-delete"]').val();

    const extendedFormData = `${formData}&kunden-delete=${customer_id}`;

    $.ajax({
      url: "/submit_c_delete",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_car_delete").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const car_id = $('input[name="car-delete"]').val();

    const extendedFormData = `${formData}&car-delete=${car_id}`;

    $.ajax({
      url: "/submit_car_delete",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_p_delete").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const project_id = $('input[name="project-delete"]').val();

    const extendedFormData = `${formData}&project-delete=${project_id}`;

    $.ajax({
      url: "/submit_p_delete",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });

  $("#submit_extra_delete").on("submit", function (event) {
    event.preventDefault();

    const formData = $(this).serialize();

    const extra_id = $('input[name="extra-delete"]').val();

    const extendedFormData = `${formData}&extra-delete=${extra_id}`;

    $.ajax({
      url: "/submit_extra_delete",
      method: "POST",
      data: extendedFormData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr, status, error) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen." + error);
      },
    });
  });
});

// ICON FÜR HINWEIS
function checkForHints() {
  $(".assignment-cell").each(function () {
    var assignmentId = $(this)
      .find("div[data-assignment-id]")
      .data("assignment-id");

    if (assignmentId) {
      var $cell = $(this);

      $.ajax({
        url: "/get_assignment_hinweis",
        method: "POST",
        data: { assignmentId: assignmentId },
        success: function (response) {
          var hinweis = response.hinweis;

          // Remove existing icon
          $cell.find(".hint-icon").remove();

          if (hinweis) {
            // Add information icon
            var iconHtml = "<i class='bx bx-info-circle'></i>";
            $cell.append(iconHtml);

            // Set the flag to indicate that the icon has been added
            $cell.data("icon-added", true);
          } else {
            // Set the flag to indicate that the icon has been removed
            $cell.data("icon-added", false);
          }
        },
        error: function (xhr, status, error) {
          console.log("Kein Hinweis hinterlegt für dieses Assignment");
        },
      });
    }
  });
}

checkForHints();

// HINWEIS DARSTELLEN
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
          if (hinweis) {
            alert(hinweis);

            var iconHtml = "<i class='bx bx-info-circle'></i>";
            $(this).append(iconHtml);
          }
        },
        error: function (xhr, status, error) {
          console.log("Kein Hinweis hinterlegt für dieses Assignment");
        },
      });
    }
  });
});

// HIGHLIGHT GROUP
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
    var letters = "89ABCDEF";
    var color = "#";

    // Generate a 6-digit random hexadecimal color code
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * letters.length)];
    }

    return color;
  }
});

// HIGHLIGHT SPECIAL
$(document).ready(function () {
  highlightSpecialValues();

  function highlightSpecialValues() {
    var specialValues = {};
    var valueColors = {
      1: "#000", // Black color for "schule"
      2: "#FFFF00", // Yellow color for "abwesend"
      3: "#0000FF", // Blue color for "urlaub"
      4: "#89CFF0", // Some specific color for "gleitzeit"
    };

    // Iterate through each assignment cell
    $(".assignment-cell").each(function () {
      var assignmentId = $(this)
        .find("div[data-assignment-id]")
        .data("assignment-id");
      var abwesendValue = $(this).find("div[data-abw-id]").data("abw-id");

      if (assignmentId) {
        // Check values for each column
        var color; // Default color

        if (abwesendValue > 0) {
          if (abwesendValue == 1) {
            color = valueColors["1"]; // Black color for "schule"
          } else if (abwesendValue == 2) {
            color = valueColors["2"]; // Yellow color for "abwesend"
          } else if (abwesendValue == 3) {
            color = valueColors["3"]; // Blue color for "urlaub"
          } else if (abwesendValue == 4) {
            color = valueColors["4"]; // Specific color for "gleitzeit"
          }
        }

        // Highlight the current assignment cell with the corresponding CSS class
        $(this).css("background-color", color);
        $(this).css("color", color);
      }
    });
  }
});

// DELETE-BUTTON FOR ASSIGNMENT
$(function () {
  $(".assignment-cell .delete-btn").click(function (e) {
    e.stopPropagation(); // Prevent the click event from propagating to the assignment-cell

    var assignmentId = $(this).data("assignment-id");

    if (
      assignmentId &&
      confirm("Möchtest du wirklich diese Zuteilung löschen?")
    ) {
      $.ajax({
        url: "/delete_assignment",
        method: "POST",
        data: { assignmentId: assignmentId },
        success: function (response) {
          // Optionally, update the UI to reflect the deletion
          alert("Zuteilung erfolgreich gelöscht!");
          window.location.reload();
        },
        error: function (xhr, status, error) {
          console.log("Error beim Löschen der Zuteilung");
        },
      });
    }
  });

  $(".assignment-cell").click(function () {
    var deleteButton = $(this).find(".delete-btn");

    if (deleteButton.length) {
      var assignmentId = deleteButton.data("assignment-id");
      var startDate = deleteButton.data("start-date");

      deleteButton.click(function () {
        // Handle the delete action
        if (
          assignmentId &&
          startDate &&
          confirm("Möchtest du wirklich diese Zuteilung löschen?")
        ) {
          $.ajax({
            url: "/delete_assignment",
            method: "POST",
            data: { assignmentId: assignmentId },
            success: function (response) {
              // Optionally, update the UI to reflect the deletion
              alert("Zuteilung erfolgreich gelöscht!");
              window.location.reload();
            },
            error: function (xhr, status, error) {
              console.log("Error beim Löschen der Zuteilung");
            },
          });
        }
      });
    }
  });
});

// EDIT-Button for assignment
$(document).ready(function() {
  // Open edit modal when edit button is clicked
  $(".edit-btn").click(function() {
    var assignmentId = $(this).data("assignment-id");
    openEditModal(assignmentId);
  });

  function openEditModal(assignmentId) {
    // Fetch assignment details from the server
    $.ajax({
      url: `/get_assignment_details/${assignmentId}`,
      method: "GET",
      success: function(data) {
        $("#editAssignmentId").val(assignmentId);
        $("#editStartDate").val(data.start_date);
        $("#editEndDate").val(data.end_date);
        $("#editHinweis").val(data.hinweis);
        
        // Clear previous selections
        $("#editEmployees option").prop("selected", false);
        
        // Select the correct employees
        data.employees.forEach(function(employeeId) {
          $(`#editEmployees option[value="${employeeId}"]`).prop("selected", true);
        });

        $("#editAssignmentModal").show();
      },
      error: function(xhr, status, error) {
        console.error("Error fetching assignment details:", error);
        alert("An error occurred while fetching assignment details.");
      }
    });
  }

  // Close modal when clicking the close button
  $(".close").click(function() {
    $("#editAssignmentModal").hide();
  });

  // Handle form submission
  $("#editAssignmentForm").submit(function(e) {
    e.preventDefault();
    var formData = $(this).serialize();

    $.ajax({
      url: "/edit_assignment",
      method: "POST",
      data: formData,
      success: function(response) {
        if (response.status === "success") {
          alert(response.message);
          $("#editAssignmentModal").hide();
          refreshAssignments();
        } else {
          alert("Error: " + response.message);
        }
      },
      error: function(xhr, status, error) {
        console.error("Error updating assignment:", error);
        alert("An error occurred while updating the assignment.");
      }
    });
  });

  function refreshAssignments() {
    // Hier eventuell noch eine Logic einbauen, bei der nur die Assignments refreshed werden und nicht die ganze Seite
    
    // Page reload
    location.reload();
  }
});