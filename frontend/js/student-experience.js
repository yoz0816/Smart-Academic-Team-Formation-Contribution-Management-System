"use strict";

document.addEventListener("DOMContentLoaded", initializeStudentExperience);

async function initializeStudentExperience() {
    const user = await window.JOZSession.requireRole(["student"]);
    if (!user) return;

    const form = document.getElementById("experienceForm");
    const cgpaInput = document.getElementById("cgpa");
    const saveButton = document.getElementById("saveExperienceButton");
    const message = document.getElementById("experienceMessage");
    const recordContainer = document.getElementById("experienceRecord");

    let currentRecord = null;

    const fullName = user.full_name || "Student";
    document.getElementById("userName").textContent = fullName;
    document.getElementById("userAvatar").textContent = fullName.charAt(0).toUpperCase();
    document.getElementById("currentYear").textContent = new Date().getFullYear();

    document.getElementById("logoutButton").addEventListener("click", async () => {
        try {
            await window.JOZSession.logout();
        } catch (error) {
            showMessage(error.message || "Unable to sign out.", "error");
        }
    });

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#039;"
        })[character]);
    }

    function showMessage(text, type = "") {
        message.textContent = text;
        message.className = "experience-message";
        if (type) message.classList.add(`is-${type}`);
    }

    function statusMarkup(status) {
        const values = {
            Pending: ["fa-clock", "pending"],
            Approved: ["fa-circle-check", "approved"],
            Rejected: ["fa-circle-xmark", "rejected"]
        };
        const [icon, cssClass] = values[status] || values.Pending;

        return `<span class="experience-status ${cssClass}">
            <i class="fa-solid ${icon}"></i>${escapeHTML(status)}
        </span>`;
    }

    function renderRecord(record) {
        currentRecord = record;

        if (!record) {
            recordContainer.innerHTML = `
                <div class="experience-empty">
                    <i class="fa-solid fa-file-circle-plus"></i>
                    <h4>No CGPA submitted</h4>
                    <p>Enter your cumulative GPA and submit it for administrator verification.</p>
                </div>`;
            document.getElementById("experienceFormHeading").textContent = "Submit your CGPA";
            saveButton.innerHTML = '<i class="fa-solid fa-paper-plane"></i><span>Submit CGPA</span>';
            cgpaInput.value = "";
            return;
        }

        recordContainer.innerHTML = `
            <div class="experience-record">
                <div class="experience-record-top">
                    <span class="experience-record-label">Cumulative GPA / 4.00</span>
                    ${statusMarkup(record.status)}
                </div>
                <div class="experience-record-value">${Number(record.cgpa).toFixed(2)}</div>
                <div class="experience-record-detail">
                    Submitted: ${escapeHTML(new Date(record.created_at).toLocaleString())}
                    ${record.verified_at
                        ? `<br>Reviewed: ${escapeHTML(new Date(record.verified_at).toLocaleString())}`
                        : ""}
                </div>
                ${record.rejection_reason
                    ? `<div class="experience-rejection">
                        <strong>Administrator's feedback</strong><br>
                        ${escapeHTML(record.rejection_reason)}
                       </div>`
                    : ""}
            </div>`;

        cgpaInput.value = Number(record.cgpa).toFixed(2);
        document.getElementById("experienceFormHeading").textContent = "Update your CGPA";
        saveButton.innerHTML = '<i class="fa-solid fa-floppy-disk"></i><span>Save Changes</span>';
    }

    async function loadRecord() {
        recordContainer.innerHTML = `
            <div class="experience-loading">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <span>Loading your record...</span>
            </div>`;

        try {
            const record = await window.JOZApi.get("/api/student/academic-experience");
            renderRecord(record);
        } catch (error) {
            recordContainer.innerHTML = `
                <div class="experience-empty">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <h4>Unable to load your record</h4>
                    <p>${escapeHTML(error.message || "Please refresh and try again.")}</p>
                </div>`;
        }
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const value = cgpaInput.value.trim();
        const cgpa = Number(value);

        if (!value || !Number.isFinite(cgpa) || cgpa < 0 || cgpa > 4 ||
            !/^\d+(\.\d{1,2})?$/.test(value)) {
            showMessage("Enter a valid CGPA between 0.00 and 4.00, with up to two decimal places.", "error");
            cgpaInput.focus();
            return;
        }

        const isEditing = Boolean(currentRecord);
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><span>Saving...</span>';
        showMessage("Saving your CGPA submission...");

        try {
            const payload = { cgpa: Number(cgpa.toFixed(2)) };

            const record = isEditing
                ? await window.JOZApi.put("/api/student/academic-experience", payload)
                : await window.JOZApi.post("/api/student/academic-experience", payload);

            renderRecord(record);
            showMessage(
                isEditing
                    ? "Your CGPA was updated and sent for verification again."
                    : "Your CGPA was submitted successfully and is awaiting verification.",
                "success"
            );
        } catch (error) {
            showMessage(error.message || "Unable to save your CGPA.", "error");
        } finally {
            saveButton.disabled = false;
            saveButton.innerHTML = currentRecord
                ? '<i class="fa-solid fa-floppy-disk"></i><span>Save Changes</span>'
                : '<i class="fa-solid fa-paper-plane"></i><span>Submit CGPA</span>';
        }
    });

    await loadRecord();
}
