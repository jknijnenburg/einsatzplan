// Constants and Configurations
const CONFIG = {
  COLORS: {
    SPECIAL_VALUES: {
      1: "#000000", // Schule
      2: "#FFFF00", // Abwesend
      3: "#0000FF", // Urlaub
      4: "#89CFF0", // Gleitzeit
    },
  },
  DATE_LOCALE: {
    format: "YYYY-MM-DD",
    firstDay: 1,
    applyLabel: "Übernehmen",
    cancelLabel: "Abbrechen",
    daysOfWeek: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
    monthNames: [
      "Januar",
      "Februar",
      "März",
      "April",
      "Mai",
      "Juni",
      "Juli",
      "August",
      "September",
      "Oktober",
      "November",
      "Dezember",
    ],
  },
};

// Calendar Management
const CalendarManager = {
  init() {
    this.setupWeekNavigation();
    this.setupWeekJumping();
    this.setupTodayButton();
    this.updateUrlParams();
    this.initializeWeekDisplay();
  },

  initializeWeekDisplay() {
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const startOfYear = new Date(currentYear, 0, 1);
    const millisecondsInWeek = 604800000;
    const weeksInYear = Math.ceil(
      (currentDate - startOfYear) / millisecondsInWeek
    );

    const weekOutputElement = document.getElementById("week-output");
    if (weekOutputElement) {
      weekOutputElement.textContent = "KW " + weeksInYear;
    }
  },

  getCurrentWeek() {
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 1);
    const days = Math.floor((now - start) / (24 * 60 * 60 * 1000));
    return Math.ceil((days + start.getDay() + 1) / 7);
  },

  getUrlParameters() {
    const params = new URLSearchParams(window.location.search);
    return {
      kw1: parseInt(params.get("kw_1")) || this.getCurrentWeek(),
      kw2: parseInt(params.get("kw_2")) || this.getCurrentWeek() + 1,
    };
  },

  updateUrlParams() {
    const params = this.getUrlParameters();
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("kw_1", params.kw1);
    newUrl.searchParams.set("kw_2", params.kw2);
    window.history.replaceState({}, "", newUrl);
  },

  navigateWeeks(direction) {
    const params = this.getUrlParameters();
    params.kw1 += direction;
    params.kw2 += direction;

    // Handle year transitions
    if (params.kw1 > 52) {
      params.kw1 = 1;
    } else if (params.kw1 < 1) {
      params.kw1 = 52;
    }

    if (params.kw2 > 52) {
      params.kw2 = 1;
    } else if (params.kw2 < 1) {
      params.kw2 = 52;
    }

    this.refreshCalendar(params.kw1, params.kw2);
  },

  jumpToWeek(weekNumber) {
    if (weekNumber < 1 || weekNumber > 52) {
      alert("Bitte geben Sie eine gültige Kalenderwoche (1-52) ein.");
      return;
    }

    const params = this.getUrlParameters();
    params.kw1 = parseInt(weekNumber);
    params.kw2 = parseInt(weekNumber) + 1;

    if (params.kw2 > 52) {
      params.kw2 = 1;
    }

    this.refreshCalendar(params.kw1, params.kw2);
  },

  refreshCalendar(kw1, kw2) {
    const url = new URL(window.location.href);
    url.searchParams.set("kw_1", kw1);
    url.searchParams.set("kw_2", kw2);
    window.location.href = url.toString();
  },

  setupWeekNavigation() {
    const prevWeek = document.getElementById("prev-week");
    const nextWeek = document.getElementById("next-week");

    if (prevWeek) {
      prevWeek.addEventListener("click", () => this.navigateWeeks(-1));
    }
    if (nextWeek) {
      nextWeek.addEventListener("click", () => this.navigateWeeks(1));
    }
  },

  setupWeekJumping() {
    const jumpForm = document.getElementById("jump-to-week-form");
    if (jumpForm) {
      jumpForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const weekInput = document.getElementById("week-number-input");
        this.jumpToWeek(weekInput.value);
      });
    }
  },

  setupTodayButton() {
    const todayButton = document.getElementById("today-button");
    if (todayButton) {
      todayButton.addEventListener("click", () => {
        const currentWeek = this.getCurrentWeek();
        this.refreshCalendar(currentWeek, currentWeek + 1);
      });
    }
  },
};

// Assignment Management
const AssignmentManager = {
  init() {
    $("#editAssignmentModal").hide();
    this.setupAssignmentForms();
    this.setupRecurringAssignments();
    this.setupGroupAssignments();
    this.setupAssignmentActions();
    this.setupDataManagement();
    this.setupEditForm();
  },

  setupAssignmentForms() {
    $('input[name="datefilter"], input[name="datefilter-g"]').daterangepicker({
      autoUpdateInput: false,
      locale: CONFIG.DATE_LOCALE,
    });

    $('input[name="datefilter"], input[name="datefilter-g"]')
      .on("apply.daterangepicker", function (ev, picker) {
        $(this).val(
          picker.startDate.format("YYYY-MM-DD") +
            " - " +
            picker.endDate.format("YYYY-MM-DD")
        );
      })
      .on("cancel.daterangepicker", function () {
        $(this).val("");
      });

    // Single assignment form
    $("#assignForm").on("submit", function (event) {
      event.preventDefault();
      const assignments = AssignmentManager.collectAssignmentData(this);
      AssignmentManager.submitAssignments(assignments);
    });
  },

  setupRecurringAssignments() {
    $("#is_recurring, #is_recurring_group").change(function () {
      const targetId =
        this.id === "is_recurring"
          ? "recurring_options"
          : "recurring_options_group";
      $(`#${targetId}`).toggle(this.checked);
    });
  },

  setupGroupAssignments() {
    // Initialize chosen selects
    $(
      "#personal_nr_list, #dd-m, #dd-p, #dd-car, #dd-l, #dd-x, #dd-xx, #dd-xxx"
    ).chosen();
    $("#dd-p-g, #dd-car-g, #dd-l-g, #dd-x-g, #dd-xx-g, #dd-xxx-g").chosen();

    // Group assignment form
    $("#group-form").on("submit", function (event) {
      event.preventDefault();
      const groupAssignments = AssignmentManager.collectGroupData(this);
      AssignmentManager.submitGroupAssignments(groupAssignments);
    });
  },

  setupAssignmentActions() {
    // Delete assignment button
    $(".delete-btn").click(function (e) {
      e.stopPropagation();
      const assignmentId = $(this).data("assignment-id");
      if (
        assignmentId &&
        confirm("Möchten Sie diese Zuteilung wirklich löschen?")
      ) {
        AssignmentManager.deleteAssignment(assignmentId);
      }
    });

    // Edit assignment button
    $(".edit-btn").click((e) => {
      e.preventDefault();
      e.stopPropagation();
      const assignmentId = $(e.currentTarget).data("assignment-id");
      console.log("Edit button clicked for assignment:", assignmentId);
      this.openEditModal(assignmentId);
    });

    // Close modal when clicking x button
    $(".close").click(() => {
      $("#editAssignmentModal").hide();
    });

    // Close modal when clicking outside
    $(window).click((e) => {
      const modal = $("#editAssignmentModal");
      if (e.target === modal[0]) {
        modal.hide();
      }
    });
  },

  setupDataManagement() {
    // Setup all data management forms
    const formIds = [
      "submit_m_add",
      "submit_c_add",
      "submit_p_add",
      "submit_car_add",
      "submit_extra_add",
      "submit_m_delete",
      "submit_c_delete",
      "submit_car_delete",
      "submit_p_delete",
      "submit_extra_delete",
    ];

    formIds.forEach((formId) => {
      $(`#${formId}`).on("submit", function (event) {
        event.preventDefault();
        AssignmentManager.handleDataSubmission(this);
      });
    });
  },

  collectAssignmentData(form) {
    const startDate = moment(
      $(form).find('input[name="datefilter"]').data("daterangepicker").startDate
    );
    const endDate = moment(
      $(form).find('input[name="datefilter"]').data("daterangepicker").endDate
    );
    const isRecurring = $("#is_recurring").is(":checked");
    const recurrenceInterval = parseInt($("#recurrence_interval").val(), 10);
    const recurrenceEndDate = moment($("#recurrence_end_date").val());

    const assignments = [];

    function createAssignment(start, end) {
      return {
        personal_nr: $('select[name="personal_nr"]').val(),
        startDate: start.format("YYYY-MM-DD"),
        endDate: end.format("YYYY-MM-DD"),
        year: start.year(),
        week_id: getNumberOfWeek(start.toDate()),
        project_id: $('select[name="project_id"]').val() || "0",
        car_id: $('select[name="car_id"]').val() || "0",
        ort: $('select[name="ort"]').val(),
        extra1: $('select[name="extra1"]').val() || "no",
        extra2: $('select[name="extra2"]').val() || "no",
        extra3: $('select[name="extra3"]').val() || "no",
        hinweis: $('textarea[name="hinweis"]').val() || "",
        checkedRadioButton: $("input[name='abw']:checked").val() || "0",
      };
    }

    assignments.push(createAssignment(startDate, endDate));

    if (isRecurring) {
      let currentStart = startDate.clone().add(recurrenceInterval, "weeks");
      let currentEnd = endDate.clone().add(recurrenceInterval, "weeks");

      while (currentStart.isSameOrBefore(recurrenceEndDate)) {
        assignments.push(createAssignment(currentStart, currentEnd));
        currentStart.add(recurrenceInterval, "weeks");
        currentEnd.add(recurrenceInterval, "weeks");
      }
    }

    return assignments;
  },

  submitAssignments(assignments) {
    $.ajax({
      url: "/assign_mitarbeiter_bulk",
      method: "POST",
      data: JSON.stringify(assignments),
      contentType: "application/json",
      success: function (response) {
        alert(response.message);
        $(document).trigger("assignmentUpdated");
        window.location.reload();
      },
      error: function (xhr) {
        alert(
          "Fehler beim Zuweisen: " +
            (xhr.responseJSON?.error || "Unbekannter Fehler")
        );
      },
    });
  },

  collectGroupData(form) {
    const startDate = moment(
      $(form).find('input[name="datefilter-g"]').data("daterangepicker")
        .startDate
    );
    const endDate = moment(
      $(form).find('input[name="datefilter-g"]').data("daterangepicker").endDate
    );
    const isRecurring = $("#is_recurring_group").is(":checked");
    const recurrenceInterval = parseInt(
      $("#recurrence_interval_group").val(),
      10
    );
    const recurrenceEndDate = moment($("#recurrence_end_date_group").val());

    const groupAssignments = [];

    function createGroupAssignment(start, end) {
      return {
        personal_nr_list: $("#personal_nr_list").val(),
        startDate: start.format("YYYY-MM-DD"),
        endDate: end.format("YYYY-MM-DD"),
        year: start.year(),
        week_id: getNumberOfWeek(start.toDate()),
        project_id: $('select[name="project_id"]').val() || "0",
        car_id: $('select[name="car_id"]').val() || "0",
        ort: $('select[name="ort"]').val(),
        extra1: $('select[name="extra1"]').val() || "no",
        extra2: $('select[name="extra2"]').val() || "no",
        extra3: $('select[name="extra3"]').val() || "no",
        hinweis: $('textarea[name="hinweis"]').val() || "",
      };
    }

    // Add initial assignment
    groupAssignments.push(createGroupAssignment(startDate, endDate));

    // Add recurring assignments if enabled
    if (isRecurring) {
      let currentStart = startDate.clone().add(recurrenceInterval, "weeks");
      let currentEnd = endDate.clone().add(recurrenceInterval, "weeks");

      while (currentStart.isSameOrBefore(recurrenceEndDate)) {
        groupAssignments.push(createGroupAssignment(currentStart, currentEnd));
        currentStart = currentStart.clone().add(recurrenceInterval, "weeks");
        currentEnd = currentEnd.clone().add(recurrenceInterval, "weeks");
      }
    }

    return groupAssignments;
  },

  submitGroupAssignments(groupAssignments) {
    $.ajax({
      url: "/assign_group_bulk",
      method: "POST",
      data: JSON.stringify(groupAssignments),
      contentType: "application/json",
      success: function (response) {
        alert(response.message);
        window.location.reload();
      },
      error: function (xhr) {
        alert(
          "Fehler beim Gruppenzuweisen: " +
            (xhr.responseJSON?.error || "Unbekannter Fehler")
        );
      },
    });
  },

  deleteAssignment(assignmentId) {
    $.ajax({
      url: "/delete_assignment",
      method: "POST",
      data: { assignmentId: assignmentId },
      success: function (response) {
        if (response.status === "success") {
          alert("Zuteilung erfolgreich gelöscht!");
          window.location.reload();
        }
      },
      error: function () {
        alert("Fehler beim Löschen der Zuteilung");
      },
    });
  },

  openEditModal(assignmentId) {
    console.log("Opening edit modal for assignment:", assignmentId);
    $.ajax({
      url: `/get_assignment_details/${assignmentId}`,
      method: "GET",
      success: function (data) {
        console.log("Received data:", data);
        if (data.error) {
          alert(data.error);
          return;
        }

        $("#editAssignmentId").val(assignmentId);
        $("#editStartDate").val(data.start_date);
        $("#editEndDate").val(data.end_date);
        $("#editHinweis").val(data.hinweis || "");

        // Clear all checkboxes first
        $('input[name="employees[]"]').prop("checked", false);

        if (!data.is_group) {
          // For single assignments, disable all checkboxes except the assigned one
          $('input[name="employees[]"]').prop("disabled", true);
        } else {
          // For group assignments, enable all checkboxes
          $('input[name="employees[]"]').prop("disabled", false);
        }

        // Check boxes for assigned employees
        if (data.employees && data.employees.length > 0) {
          data.employees.forEach(function (employeeId) {
            $(`#employee_${employeeId}`).prop("checked", true);
          });
        }

        $("#editAssignmentModal").show();
      },
      error: function (xhr) {
        console.error("Error loading assignment details:", xhr);
        alert("Fehler beim Laden der Zuteilungsdetails");
      },
    });
  },

  setupEditForm() {
    // Add group selection functionality
    $(".work-field-title").click(function () {
      const $checkboxes = $(this)
        .siblings(".employee-checkbox")
        .find('input[type="checkbox"]');
      const allChecked =
        $checkboxes.length === $checkboxes.filter(":checked").length;
      $checkboxes.prop("checked", !allChecked);
    });

    $("#editAssignmentForm").on("submit", function (e) {
      e.preventDefault();

      // Validate that at least one employee is selected
      if ($('input[name="employees[]"]:checked').length === 0) {
        alert("Bitte wählen Sie mindestens einen Mitarbeiter aus.");
        return;
      }

      const formData = $(this).serialize();

      $.ajax({
        url: "/edit_assignment",
        method: "POST",
        data: formData,
        success: function (response) {
          if (response.status === "success") {
            alert("Zuteilung erfolgreich aktualisiert");
            window.location.reload();
          } else {
            alert(response.message || "Fehler beim Aktualisieren");
          }
        },
        error: function (xhr) {
          alert("Fehler beim Aktualisieren der Zuteilung");
        },
      });
    });
  },

  handleDataSubmission(form) {
    const formId = $(form).attr("id");
    const endpoint = "/" + formId;
    const formData = $(form).serialize();

    $.ajax({
      url: endpoint,
      method: "POST",
      data: formData,
      success: function (response) {
        alert(response);
        window.location.reload();
      },
      error: function (xhr) {
        alert("Ein Fehler ist aufgetreten. Bitte erneut versuchen.");
      },
    });
  },
};


const AssignmentsListManager = {
  init() {
    // Ensure this runs when the document is ready
    $(document).ready(() => {
      console.log("Initializing AssignmentsListManager");
      this.setupModal();
      this.setupEventHandlers();
    });
  },

  setupModal() {
    // Show modal button - use direct event binding
    $(document).on("click", "#showAllAssignmentsListBtn", (e) => {
      console.log("Show all assignments button clicked");
      e.preventDefault();
      e.stopPropagation();
      this.loadAssignments();
      $("#allAssignmentsListModal").fadeIn(300);
    });

    // Close button - use direct event binding
    $(document).on("click", ".assignments-close", (e) => {
      console.log("Close button clicked");
      e.preventDefault();
      e.stopPropagation();
      $("#allAssignmentsListModal").fadeOut(300);
    });

    // Click outside modal to close
    $(document).on("click", (e) => {
      const modal = $("#allAssignmentsListModal");
      if ($(e.target).is(modal)) {
        modal.fadeOut(300);
      }
    });
  },

  setupEventHandlers() {
    // Select all checkbox
    $(document).on("change", "#selectAllAssignmentsList", function () {
      $(".assignments-list-checkbox").prop("checked", $(this).is(":checked"));
    });

    // Search functionality
    $(document).on("input", "#assignmentsListSearch", function () {
      const searchTerm = $(this).val().toLowerCase();
      $(".assignments-list-row").each(function () {
        const text = $(this).text().toLowerCase();
        $(this).toggle(text.includes(searchTerm));
      });
    });

    // Delete selected button
    $(document).on("click", "#deleteSelectedAssignmentsList", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const selectedIds = [];
      $(".assignments-list-checkbox:checked").each(function () {
        selectedIds.push($(this).val());
      });

      if (selectedIds.length === 0) {
        alert("Bitte wählen Sie mindestens eine Zuweisung aus.");
        return;
      }

      if (
        confirm(
          `Möchten Sie wirklich ${selectedIds.length} Zuweisungen löschen?`
        )
      ) {
        this.deleteSelectedAssignments(selectedIds);
      }
    });
  },

  loadAssignments() {
    console.log("Loading assignments");
    $.ajax({
      url: "/get_all_assignments",
      method: "GET",
      success: (response) => {
        if (response.error) {
          alert(response.error);
          return;
        }

        const tbody = $("#assignmentsListTableBody");
        tbody.empty();

        response.assignments.forEach((assignment) => {
          const row = $("<tr>").addClass("assignments-list-row");
          row.append(`
                      <td>
                          <input type="checkbox" class="assignments-list-checkbox" value="${
                            assignment.assignment_id
                          }">
                      </td>
                      <td>${assignment.employee_name}</td>
                      <td>${assignment.project_name}</td>
                      <td>${assignment.start_date}</td>
                      <td>${assignment.end_date}</td>
                      <td>${
                        assignment.group_id > 0
                          ? `<span class="assignments-group-indicator">Gruppe ${assignment.group_id}</span>`
                          : "Einzeln"
                      }</td>
                  `);
          tbody.append(row);
        });
      },
      error: () => {
        alert("Fehler beim Laden der Zuweisungen");
      },
    });
  },

  deleteSelectedAssignments(assignmentIds) {
    $.ajax({
      url: "/delete_assignments_bulk",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ assignment_ids: assignmentIds }),
      success: (response) => {
        if (response.error) {
          alert(response.error);
          return;
        }
        alert(response.message);
        this.loadAssignments(); // Refresh the list
        window.location.reload(); // Refresh the main page
      },
      error: () => {
        alert("Fehler beim Löschen der Zuweisungen");
      },
    });
  },
};

// Visual Effects Manager
const VisualManager = {
  init() {
    this.setupModalHandling();
    this.setupHintSystem();
    this.initializeGroupColors();
    this.initializeSpecialValues();
    this.initializeHints();
  },

  initializeSpecialValues() {
    this.highlightSpecialValues();
  },

  initializeHints() {
    this.checkForHints();
  },

  setupModalHandling() {
    // Close modal when clicking the × button
    $(".close").click(function () {
      $("#editAssignmentModal").hide();
    });

    // Close modal when clicking outside
    $(window).click(function (event) {
      if ($(event.target).is("#editAssignmentModal")) {
        $("#editAssignmentModal").hide();
      }
    });
  },

  setupHintSystem() {
    // Show hint on click
    $(document).on("click", ".assignment-cell", function () {
      const assignmentId = $(this)
        .find("div[data-assignment-id]")
        .data("assignment-id");
      if (assignmentId) {
        VisualManager.showHint(assignmentId);
      }
    });
  },

  showHint(assignmentId) {
    $.ajax({
      url: "/get_assignment_hinweis",
      method: "POST",
      data: { assignmentId: assignmentId },
      success: function (response) {
        if (response.hinweis) {
          alert(response.hinweis);
        }
      },
    });
  },

  checkForHints() {
    $(".assignment-cell").each(function () {
      const assignmentId = $(this)
        .find("div[data-assignment-id]")
        .data("assignment-id");
      if (!assignmentId) return;

      const $cell = $(this);

      $.ajax({
        url: "/get_assignment_hinweis",
        method: "POST",
        data: { assignmentId: assignmentId },
        success: function (response) {
          $cell.find(".hint-icon").remove();

          if (response.hinweis) {
            const iconHtml = "<i class='bx bx-info-circle hint-icon'></i>";
            $cell.append(iconHtml);
            $cell.data("hint-text", response.hinweis);
          }
        },
      });
    });
  },

  groupColors: {},

  initializeGroupColors() {
    this.highlightDuplicateGroups();
  },

  generatePastelColor() {
    // Store predefined colors for consistency
    const colors = [
      "hsl(200, 70%, 80%)",
      "hsl(150, 70%, 80%)",
      "hsl(100, 70%, 80%)",
      "hsl(50, 70%, 80%)",
      "hsl(0, 70%, 80%)",
      "hsl(300, 70%, 80%)",
      "hsl(250, 70%, 80%)",
      "hsl(175, 70%, 80%)",
      "hsl(125, 70%, 80%)",
      "hsl(75, 70%, 80%)",
      "hsl(25, 70%, 80%)",
      "hsl(275, 70%, 80%)",
    ];

    // Find first unused color
    for (let color of colors) {
      if (!Object.values(this.groupColors).includes(color)) {
        return color;
      }
    }

    // If all colors are used, generate a random one
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 70%, 80%)`;
  },

  highlightDuplicateGroups() {
    const groupColors = {};
    const usedColors = new Set();

    $(".assignment-cell div[data-group-id]").each(function () {
      const groupId = $(this).data("group-id");
      if (groupId && groupId !== "0") {
        if (!groupColors[groupId]) {
          let color;
          do {
            color = VisualManager.generatePastelColor();
          } while (usedColors.has(color));

          usedColors.add(color);
          groupColors[groupId] = color;
        }
        $(this)
          .closest(".assignment-cell")
          .css("background-color", groupColors[groupId]);
      }
    });
  },

  highlightSpecialValues() {
    $(".assignment-cell div[data-abw-id]").each(function () {
      const abwValue = $(this).data("abw-id");
      const color = CONFIG.COLORS.SPECIAL_VALUES[abwValue];

      if (color) {
        const cell = $(this).closest(".assignment-cell");
        cell.css("background-color", color);
      }
    });
  },

  generatePastelColor() {
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 70%, 80%)`;
  },

  getBrightness(color) {
    const hex = color.replace("#", "");
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    return (r * 299 + g * 587 + b * 114) / 1000;
  },
};

// Utility Functions
function getNumberOfWeek(date) {
  const specific_date = new Date(date);
  const firstDayOfYear = new Date(specific_date.getFullYear(), 0, 1);
  const pastDaysOfYear = (specific_date - firstDayOfYear) / 86400000;
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
}

// Login Management
const LoginManager = {
  init() {
    this.setupLoginForm();
    this.setupLogoutHandler();
    this.setupAdminLogin();
  },

  setupLoginForm() {
    $("#login-form").on("submit", function (event) {
      event.preventDefault();
      // Add your login form handling logic here
    });
  },

  setupLogoutHandler() {
    $("#logout-button").on("click", function () {
      $.ajax({
        url: "/logout",
        method: "POST",
        success: function () {
          window.location.href = "/login";
        },
      });
    });
  },

  setupAdminLogin() {
    $("#admin-login-form").on("submit", function (event) {
      event.preventDefault();
      $.ajax({
        url: "/login_admin",
        method: "POST",
        data: $(this).serialize(),
        success: function (response) {
          if (response.status === "success") {
            window.location.reload();
          } else {
            alert("Admin-Login fehlgeschlagen.");
          }
        },
      });
    });
  },
};

// Initialize everything when document is ready
$(document).ready(function () {
  console.log("Document ready");
  CalendarManager.init();
  AssignmentManager.init();
  VisualManager.init();
  LoginManager.init();
  AssignmentManager.setupEditForm();
  AssignmentsListManager.init();

  // Add event handlers for any dynamic content updates
  // For example, after creating or editing assignments
  $(document).on("assignmentUpdated", refreshVisuals);

  // Setup general AJAX error handling
  $(document).ajaxError(function (event, xhr, settings, error) {
    if (xhr.status === 401) {
      window.location.href = "/login";
    } else if (xhr.status === 403) {
      alert("Sie haben keine Berechtigung für diese Aktion.");
    } else if (xhr.status === 404) {
      alert("Die angeforderte Ressource wurde nicht gefunden.");
    } else if (xhr.status === 500) {
      alert(
        "Ein Serverfehler ist aufgetreten. Bitte versuchen Sie es später erneut."
      );
    }
  });
});
