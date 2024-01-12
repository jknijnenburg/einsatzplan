// DESIGN
$(document).ready(function () {
  $("#personal_nr_list").chosen();
});

// CREATE MEETING
$(function () {
  // Initialize the datepicker
  $("#datepicker").datepicker({
    dateFormat: "yy-mm-dd",
    minDate: 0, // Set the minimum date to today
  });

  // Submit form and update table
  $("#reservation-form").submit(function (e) {
    e.preventDefault();

    // Get form data
    var formData = $(this).serializeArray();
    var services = [];

    const room = $('input[name="room"]').val();

    // Get selected date
    const date = $("#datepicker").datepicker("getDate");
    const formattedDate = $.datepicker.formatDate("yy-mm-dd", date);

    // Get time
    const startTime = document.getElementById("start-time").value;
    const endTime = document.getElementById("end-time").value;

    // Extract selected services
    $('input[name="services"]:checked').each(function () {
      services.push($(this).val());
    });

    // Get the selected personal_nr_list as an array
    const personal_nr_list = $('select[name="personal_nr_list"]').val();

    // Check if personal_nr_list is not empty
    if (!personal_nr_list || personal_nr_list.length === 0) {
      console.log("Error: personal_nr_list is empty.");
      return; // Prevent further execution
    }

    // Extend the form data with additional fields
    const extendedFormData = `${formData}&date=${formattedDate}&startTime=${startTime}&endTime=${endTime}&room=${room}&services=${services}`;

    // Set the form token in the session
    const formToken = $("input[name='form_token']").val();
    sessionStorage.setItem("form_token", formToken);

    console.log("Submitting meeting form...");

    $.ajax({
      url: "/reserve_meeting",
      method: "POST",
      data:
        extendedFormData +
        "&personal_nr_list=" +
        personal_nr_list.join(",") +
        "&form_token=" +
        formToken,

      success: function (response) {
        alert(response);
        window.location.reload();
      },

      error: function (xhr, status, error) {
        // Handle the error
        alert("Meeting konnte nicht erstellt werden.");
      },
    });
  });
});

// DELETE MEETING
document.addEventListener("DOMContentLoaded", function () {
  // Add a click event listener to all delete buttons
  var deleteButtons = document.querySelectorAll(".delete-btn");
  deleteButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var m_group = button.getAttribute("data-group-m");
      deleteMeeting(m_group);
    });
  });
});

function deleteMeeting(m_group) {
  // Perform an AJAX request to delete the meeting
  fetch("/delete_meeting", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ m_group: m_group }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Meeting wurde erfolgreich gelöscht!");
        // Optionally, update the UI to reflect the deletion
        // For example, remove the deleted row from the table
        var deletedRow = document
          .querySelector(`.delete-btn[data-group-m="${m_group}"]`)
          .closest("tr");
        deletedRow.remove();
        window.location.reload();
      } else {
        alert("Error beim löschen des Meetings.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
