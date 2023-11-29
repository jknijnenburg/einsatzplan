const currentDate = new Date();
const currentYear = currentDate.getFullYear();
const startOfYear = new Date(currentYear, 0, 1);
const millisecondsInWeek = 604800000;

const weeksInYear = Math.ceil((currentDate - startOfYear) / millisecondsInWeek);

const weekOutputElement = document.getElementById("week-output");
weekOutputElement.textContent = "KW " + weeksInYear;

$(function () {
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
        picker.startDate.format("DD.MM.YYYY") +
          " - " +
          picker.endDate.format("DD.MM.YYYY")
      );

      const year = picker.startDate.getFullYear();
      // Send the selected dates to the Python backend
      $.ajax({
        url: "/assign_mitarbeiter",
        method: "POST",
        data: {
          startDate: startDate,
          endDate: endDate,
          year: year,
        },
        success: function (response) {
          // Handle the response from the Python backend
        },
        error: function (xhr, status, error) {
          // Handle the error
        },
      });
    }
  );

  $('input[name="datefilter"]').on(
    "cancel.daterangepicker",
    function (ev, picker) {
      $(this).val("");
    }
  );
});
