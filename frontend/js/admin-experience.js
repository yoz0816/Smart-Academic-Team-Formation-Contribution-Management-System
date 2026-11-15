"use strict";

document.addEventListener("DOMContentLoaded", initializeAdminExperience);
async function initializeAdminExperience() {
    const user = await window.JOZSession.requireRole(["admin"]);
    if (!user) return;

    const list = document.getElementById("adminExperienceList");
    const filter = document.getElementById("statusFilter");
    const message = document.getElementById("adminExperienceMessage");

    document.getElementById("userName").textContent = user.full_name || "Administrator";
    document.getElementById("userAvatar").textContent =
        (user.full_name || "A").charAt(0).toUpperCase();
    document.getElementById("currentYear").textContent = new Date().getFullYear();

    document.getElementById("logoutButton").addEventListener("click", async () => {
        try {
            await window.JOZSession.logout();
        } catch (error) {
            showMessage(error.message || "Unable to sign out.", "error");
        }
    });

    let records = [];

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#039;"
        })[character]);
    }

    function showMessage(text, type = "") {
        message.textContent = text;
        message.className = "admin-experience-message";
        if (type) message.classList.add(`is-${type}`);
    }

    function updateCounters() {
        document.getElementById("totalRecords").textContent = records.length;
        document.getElementById("pendingRecords").textContent =
            records.filter(item => item.status === "Pending").length;
        document.getElementById("approvedRecords").textContent =
            records.filter(item => item.status === "Approved").length;
        document.getElementById("rejectedRecords").textContent =
            records.filter(item => item.status === "Rejected").length;
    }

    function statusMarkup(status) {
        const cssClass = status.toLowerCase();
        const icons = {
            Pending: "fa-clock",
            Approved: "fa-circle-check",
            Rejected: "fa-circle-xmark"
        };

        return `<span class="admin-experience-status ${cssClass}">
            <i class="fa-solid ${icons[status] || icons.Pending}"></i>
            ${escapeHTML(status)}
        </span>`;
    }

    function renderRecords() {
        updateCounters();

        const selectedStatus = filter.value;
        const visibleRecords = selectedStatus
            ? records.filter(record => record.status === selectedStatus)
            : records;

        if (!visibleRecords.length) {
            list.innerHTML = `
                <div class="admin-experience-empty">
                    <i class="fa-solid fa-folder-open"></i>
                    No ${selectedStatus ? selectedStatus.toLowerCase() : ""} CGPA submissions found.
                </div>`;
            return;
        }

        list.innerHTML = visibleRecords.map(record => `
            <article class="admin-experience-card">
                <div class="admin-experience-student">
                    <div class="admin-experience-avatar">
                        ${escapeHTML((record.student_name || "S").charAt(0).toUpperCase())}
                    </div>
                    <div>
                        <h4>${escapeHTML(record.student_name)}</h4>
                        <p>${escapeHTML(record.student_email)}</p>
                        <div class="admin-experience-meta">
                            <span>Student ID: ${Number(record.student_id)}</span>
                            <span>Submitted: ${escapeHTML(new Date(record.created_at).toLocaleDateString())}</span>
                        </div>
                        <div class="admin-experience-cgpa">
                            CGPA: ${Number(record.cgpa).toFixed(2)} / 4.00
                        </div>
                    </div>
                </div>

                <div class="admin-experience-actions">
                    ${statusMarkup(record.status)}
                    ${record.status === "Pending" ? `
                        <button type="button" class="admin-review-button approve"
                                data-action="approve" data-id="${Number(record.id)}">
                            <i class="fa-solid fa-check"></i> Approve
                        </button>
                        <button type="button" class="admin-review-button reject"
                                data-action="reject" data-id="${Number(record.id)}">
                            <i class="fa-solid fa-xmark"></i> Reject
                        </button>
                    ` : ""}
                </div>

                ${record.rejection_reason ? `
                    <div class="admin-experience-reason">
                        <strong>Rejection reason:</strong>
                        ${escapeHTML(record.rejection_reason)}
                    </div>` : ""}
            </article>
        `).join("");
    }

    async function loadRecords() {
        list.innerHTML = `
            <div class="admin-experience-loading">
                <i class="fa-solid fa-spinner fa-spin"></i> Loading submissions...
            </div>`;

        try {
            const response = await window.JOZApi.get("/api/admin/academic-experience");
            records = response?.records || [];
            renderRecords();
            showMessage("");
        } catch (error) {
            list.innerHTML = `
                <div class="admin-experience-empty">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    Unable to load CGPA submissions.<br>
                    ${escapeHTML(error.message || "Please refresh and try again.")}
                </div>`;
        }
    }

    async function reviewRecord(recordId, decision) {
        let rejectionReason = null;

        if (decision === "Rejected") {
            rejectionReason = window.prompt(
                "Enter the reason for rejecting this CGPA submission:"
            );

            if (rejectionReason === null) return;

            rejectionReason = rejectionReason.trim();

            if (!rejectionReason) {
                showMessage("A rejection reason is required.", "error");
                return;
            }

            if (rejectionReason.length > 1000) {
                showMessage("The rejection reason must not exceed 1000 characters.", "error");
                return;
            }
        } else {
            const confirmed = window.confirm(
                "Have you checked this CGPA against the official university record? Approve this submission?"
            );

            if (!confirmed) return;
        }

        const button = list.querySelector(
            `button[data-id="${recordId}"][data-action="${decision.toLowerCase()}"]`
        );

        if (button) button.disabled = true;

        try {
            await window.JOZApi.patch(
                `/api/admin/academic-experience/${recordId}/review`,
                {
                    decision,
                    rejection_reason: rejectionReason
                }
            );

            showMessage(
                decision === "Approved"
                    ? "CGPA successfully approved."
                    : "CGPA rejected. The student can review the reason and resubmit.",
                "success"
            );

            await loadRecords();
        } catch (error) {
            showMessage(error.message || "Unable to review this submission.", "error");
            if (button) button.disabled = false;
        }
    }

    list.addEventListener("click", async event => {
        const button = event.target.closest("button[data-action][data-id]");
        if (!button) return;

        const recordId = Number(button.dataset.id);
        if (!Number.isInteger(recordId) || recordId <= 0) return;

        if (button.dataset.action === "approve") {
            await reviewRecord(recordId, "Approved");
        } else if (button.dataset.action === "reject") {
            await reviewRecord(recordId, "Rejected");
        }
    });

    filter.addEventListener("change", renderRecords);

    await loadRecords();
}
