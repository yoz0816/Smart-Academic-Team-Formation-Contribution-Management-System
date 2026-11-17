document.addEventListener("DOMContentLoaded", async () => {
    const MAX_PREFERENCES = 3;

    const searchInput = document.getElementById("studentSearch");
    const clearSearchButton = document.getElementById("clearSearchButton");
    const resultsContainer = document.getElementById("studentResults");
    const selectedContainer = document.getElementById("selectedStudents");
    const selectedCount = document.getElementById("selectedCount");
    const saveButton = document.getElementById("savePreferencesButton");
    const statusElement = document.getElementById("preferencesStatus");

    let selectedStudents = [];
    let savedIds = [];
    let isLoading = true;
    let isSaving = false;
    let searchTimer = null;
    let searchRequestNumber = 0;

    function escapeHTML(value) {
        return String(value).replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    }

    function showStatus(message, type = "") {
        statusElement.textContent = message;
        statusElement.className = `preferences-status ${type}`.trim();
    }

    function updateUserDetails(user) {
        const name = user?.full_name || "Student";

        const nameElement = document.getElementById("userName");
        const avatarElement = document.getElementById("userAvatar");
        const yearElement = document.getElementById("currentYear");

        if (nameElement) nameElement.textContent = name;
        if (avatarElement) {
            avatarElement.textContent = name.charAt(0).toUpperCase();
        }
        if (yearElement) {
            yearElement.textContent = new Date().getFullYear();
        }
    }

    function getSelectedIds() {
        return selectedStudents.map((student) => Number(student.id));
    }

    function hasUnsavedChanges() {
        const current = getSelectedIds();
        const saved = [...savedIds];

        return current.length !== saved.length ||
            current.some((id) => !saved.includes(id));
    }

    function updateSelectionUI() {
        selectedCount.textContent =
            `${selectedStudents.length}/${MAX_PREFERENCES}`;

        saveButton.disabled =
            isLoading || isSaving || !hasUnsavedChanges();

        saveButton.querySelector("span:first-child").textContent =
            isSaving ? "Saving..." : "Save Preferences";
    }

    function renderSelectedStudents() {
        if (selectedStudents.length === 0) {
            selectedContainer.innerHTML = `
                <div class="preferences-empty-state">
                    You have not selected any preferred teammates yet.
                    Search for classmates above to add them.
                </div>
            `;

            updateSelectionUI();
            return;
        }

        selectedContainer.innerHTML = selectedStudents.map((student, index) => {
            const name = escapeHTML(student.full_name || "Student");
            const initial = escapeHTML(
                (student.full_name || "S").charAt(0).toUpperCase()
            );

            return `
                <div class="selected-preference-row">
                    <div class="selected-preference-info">
                        <span class="selected-preference-number">${index + 1}</span>
                        <span class="preference-student-avatar"
                              aria-hidden="true">${initial}</span>
                        <span class="preference-student-name">${name}</span>
                    </div>

                    <button
                        type="button"
                        class="preference-remove-button"
                        data-remove-student="${Number(student.id)}"
                        ${isSaving ? "disabled" : ""}
                    >
                        Remove
                    </button>
                </div>
            `;
        }).join("");

        updateSelectionUI();
    }

    function renderStudentResults(students) {
        if (!students.length) {
            resultsContainer.innerHTML = `
                <div class="preferences-empty-state">
                    No active students found. Try another name.
                </div>
            `;
            return;
        }

        const selectedIds = new Set(getSelectedIds());
        const atLimit = selectedStudents.length >= MAX_PREFERENCES;

        resultsContainer.innerHTML = students.map((student) => {
            const id = Number(student.id);
            const name = escapeHTML(student.full_name || "Student");
            const initial = escapeHTML(
                (student.full_name || "S").charAt(0).toUpperCase()
            );
            const isSelected = selectedIds.has(id);

            let buttonText = "＋ Add";
            let buttonDisabled = false;

            if (isSelected) {
                buttonText = "Selected";
                buttonDisabled = true;
            } else if (atLimit) {
                buttonText = "Limit reached";
                buttonDisabled = true;
            }

            return `
                <div class="preference-student-row">
                    <div class="preference-student-info">
                        <span class="preference-student-avatar"
                              aria-hidden="true">${initial}</span>
                        <span class="preference-student-name">${name}</span>
                    </div>

                    <button
                        type="button"
                        class="preference-add-button"
                        data-add-student="${id}"
                        ${buttonDisabled || isSaving ? "disabled" : ""}
                    >
                        ${buttonText}
                    </button>
                </div>
            `;
        }).join("");
    }

    async function searchStudents(search = "") {
        const requestNumber = ++searchRequestNumber;

        resultsContainer.innerHTML = `
            <div class="preferences-empty-state">
                Searching students...
            </div>
        `;

        try {
            const query = encodeURIComponent(search.trim());
            const response = await window.JOZApi.get(
                `/api/student/preferences/students?search=${query}`
            );

            if (requestNumber !== searchRequestNumber) return;

            const students = Array.isArray(response?.students)
                ? response.students
                : [];

            renderStudentResults(students);
        } catch (error) {
            if (requestNumber !== searchRequestNumber) return;

            resultsContainer.innerHTML = `
                <div class="preferences-empty-state">
                    Unable to search students. Please try again.
                </div>
            `;

            showStatus(
                error.message || "Could not search students.",
                "error"
            );
        }
    }

    async function loadPreferences() {
        try {
            const response = await window.JOZApi.get(
                "/api/student/preferences"
            );

            const preferences = Array.isArray(response?.preferred_teammates)
                ? response.preferred_teammates
                : [];

            selectedStudents = preferences.map((student) => ({
                id: Number(student.id),
                full_name: student.full_name
            }));

            savedIds = getSelectedIds();

            renderSelectedStudents();

            showStatus(
                selectedStudents.length
                    ? "Your saved teammate preferences have been loaded."
                    : "You have not selected any preferred teammates yet."
            );
        } catch (error) {
            selectedContainer.innerHTML = `
                <div class="preferences-empty-state">
                    Unable to load your preferences. Please refresh the page.
                </div>
            `;

            showStatus(
                error.message || "Could not load your preferences.",
                "error"
            );

            throw error;
        } finally {
            isLoading = false;
            updateSelectionUI();
        }
    }

    function addStudent(studentId) {
        if (isSaving || isLoading) return;

        const id = Number(studentId);

        if (!Number.isInteger(id) || id <= 0) return;

        if (selectedStudents.some((student) => Number(student.id) === id)) {
            return;
        }

        if (selectedStudents.length >= MAX_PREFERENCES) {
            showStatus(
                "You can select a maximum of three preferred teammates.",
                "error"
            );
            return;
        }

        const resultButton = resultsContainer.querySelector(
            `[data-add-student="${id}"]`
        );

        const nameElement = resultButton?.closest(".preference-student-row")
            ?.querySelector(".preference-student-name");

        if (!nameElement) return;

        selectedStudents.push({
            id,
            full_name: nameElement.textContent
        });

        showStatus("Student added. Save your changes to confirm.");
        renderSelectedStudents();

        const currentQuery = searchInput.value.trim();
        searchStudents(currentQuery);
    }

    function removeStudent(studentId) {
        if (isSaving || isLoading) return;

        const id = Number(studentId);

        selectedStudents = selectedStudents.filter(
            (student) => Number(student.id) !== id
        );

        showStatus("Student removed. Save your changes to confirm.");
        renderSelectedStudents();

        searchStudents(searchInput.value.trim());
    }

    async function savePreferences() {
        if (isSaving || isLoading || !hasUnsavedChanges()) return;

        isSaving = true;
        updateSelectionUI();
        showStatus("Saving your teammate preferences...");

        try {
            const response = await window.JOZApi.putWithCsrf(
                "/api/student/preferences",
                {
                    preferred_user_ids: getSelectedIds()
                }
            );

            const saved = Array.isArray(response?.preferred_teammates)
                ? response.preferred_teammates
                : selectedStudents;

            selectedStudents = saved.map((student) => ({
                id: Number(student.id),
                full_name: student.full_name
            }));

            savedIds = getSelectedIds();

            showStatus(
                "Your preferred teammates have been saved successfully.",
                "success"
            );
        } catch (error) {
            showStatus(
                error.message || "Unable to save your preferences.",
                "error"
            );
        } finally {
            isSaving = false;
            renderSelectedStudents();
            searchStudents(searchInput.value.trim());
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);

        searchTimer = setTimeout(() => {
            searchStudents(searchInput.value);
        }, 300);
    });

    clearSearchButton.addEventListener("click", () => {
        searchInput.value = "";
        searchInput.focus();
        searchStudents("");
    });

    resultsContainer.addEventListener("click", (event) => {
        const button = event.target.closest("[data-add-student]");
        if (!button) return;

        addStudent(button.dataset.addStudent);
    });

    selectedContainer.addEventListener("click", (event) => {
        const button = event.target.closest("[data-remove-student]");
        if (!button) return;

        removeStudent(button.dataset.removeStudent);
    });

    saveButton.addEventListener("click", savePreferences);

    try {
        const user = await window.JOZSession.requireRole(["student"]);
        if (!user) return;

        updateUserDetails(user);

        const logoutButton = document.getElementById("logoutButton");
        logoutButton?.addEventListener("click", () => {
            window.JOZSession.logout();
        });

        await loadPreferences();
        await searchStudents("");
    } catch (error) {
        console.error("Student preferences initialization failed:", error);

        if (isLoading) {
            isLoading = false;
            updateSelectionUI();
        }

        showStatus(
            error.message || "Unable to initialize the preferences page.",
            "error"
        );
    }
});
