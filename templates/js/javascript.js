const currentDate = new Date();
const currentYear = currentDate.getFullYear();
const startOfYear = new Date(currentYear, 0, 1);
const millisecondsInWeek = 604800000;

const weeksInYear = Math.ceil((currentDate - startOfYear) / millisecondsInWeek);

const weekOutputElement = document.getElementById("week-output");
    weekOutputElement.textContent = "KW " + weeksInYear;