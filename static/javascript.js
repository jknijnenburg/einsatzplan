const currentDate = new Date();
const currentYear = currentDate.getFullYear();
const startOfYear = new Date(currentYear, 0, 1);
const millisecondsInWeek = 604800000;

const weeksInYear = Math.ceil((currentDate - startOfYear) / millisecondsInWeek);

const weekOutputElement = document.getElementById("week-output");
weekOutputElement.textContent = "KW " + weeksInYear;

$(function () {
  $("#assignForm").on('submit', function (event) {
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
