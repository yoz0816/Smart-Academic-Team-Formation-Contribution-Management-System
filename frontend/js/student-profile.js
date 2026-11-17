"use strict";

document.addEventListener("DOMContentLoaded", () => {
    initializeAcademicProfile();
});

async function initializeAcademicProfile() {
    const user = await window.JOZSession.requireRole(["student"]);

    if (!user) return;

    const form = document.getElementById("academicProfileForm");
    const saveButton = document.getElementById("saveProfileButton");
    const message = document.getElementById("profileMessage");

    const fullName = user.full_name || "Student";
    const initial = fullName.charAt(0).toUpperCase();

    document.getElementById("userName").textContent = fullName;
    document.getElementById("userAvatar").textContent = initial;
    document.getElementById("currentYear").textContent =
        new Date().getFullYear();

    document.getElementById("logoutButton").addEventListener(
        "click",
        async () => {
            try {
                await window.JOZSession.logout();
            } catch (error) {
                showMessage(error.message || "Unable to sign out.", "error");
            }
        }
    );

    function showMessage(text, type = "") {
        message.textContent = text;
        message.className = "academic-form-message";

        if (type === "success") {
            message.classList.add("is-success");
        } else if (type === "error") {
            message.classList.add("is-error");
        }
    }

    function updateCompletion(percentage) {
        const safePercentage = Math.max(0, Math.min(100, percentage || 0));

        document.getElementById("completionLabel").textContent =
            `${safePercentage}%`;

        document.getElementById("completionBar").style.width =
            `${safePercentage}%`;
    }

    function populateForm(profile) {
        document.getElementById("studentId").value =
            profile.student_id || "";

        document.getElementById("university").value =
            profile.university || "";

        document.getElementById("faculty").value =
            profile.faculty || "";

        document.getElementById("department").value =
            profile.department || "";

        document.getElementById("degreeProgram").value =
            profile.degree_program || "";

        document.getElementById("yearOfStudy").value =
            profile.year_of_study == null
                ? ""
                : String(profile.year_of_study);

        updateCompletion(profile.completion_percentage);
    }

    function getFormData() {
        const yearValue = document.getElementById("yearOfStudy").value;

        return {
            student_id: document.getElementById("studentId").value.trim() || null,
            university: document.getElementById("university").value.trim() || null,
            faculty: document.getElementById("faculty").value.trim() || null,
            department: document.getElementById("department").value.trim() || null,
            degree_program: document.getElementById("degreeProgram").value.trim() || null,
            year_of_study: yearValue ? Number(yearValue) : null
        };
    }

    async function loadProfile() {
        saveButton.disabled = true;
        showMessage("Loading your academic information...");

        try {
            const profile = await window.JOZApi.get(
                "/api/student/academic-profile"
            );

            populateForm(profile);
            showMessage("");
        } catch (error) {
            showMessage(
                error.message || "Unable to load your academic information.",
                "error"
            );
        } finally {
            saveButton.disabled = false;
        }
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const data = getFormData();

        if (data.year_of_study !== null &&
            (!Number.isInteger(data.year_of_study) ||
             data.year_of_study < 1 ||
             data.year_of_study > 5)) {
            showMessage("Please select a valid year of study.", "error");
            return;
        }

        saveButton.disabled = true;
        saveButton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i><span>Saving...</span>';

        showMessage("Saving your academic information...");

        try {
            const updatedProfile = await window.JOZApi.putWithCsrf(
                "/api/student/academic-profile",
                data
            );

            populateForm(updatedProfile);
            showMessage(
                "Your academic information has been saved successfully.",
                "success"
            );
        } catch (error) {
            showMessage(
                error.message || "Unable to save your academic information.",
                "error"
            );
        } finally {
            saveButton.disabled = false;
            saveButton.innerHTML =
                '<i class="fa-solid fa-floppy-disk"></i><span>Save Academic Information</span>';
        }
    });

    await loadProfile();
}
