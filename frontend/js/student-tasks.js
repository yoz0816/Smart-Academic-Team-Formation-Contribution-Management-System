"use strict";

document.addEventListener("DOMContentLoaded", initializeStudentTasks);

async function initializeStudentTasks() {
    const user = await window.JOZSession.requireRole(["student"]);

    if (!user) return;

    const elements = {
        userName: document.getElementById("userName"),
        userAvatar: document.getElementById("userAvatar"),
        currentYear: document.getElementById("currentYear"),
        logoutButton: document.getElementById("logoutButton"),

        refreshButton: document.getElementById("refreshTasksButton"),
        message: document.getElementById("tasksMessage"),
        loading: document.getElementById("tasksLoading"),
        waiting: document.getElementById("tasksWaitingState"),
        noResults: document.getElementById("noFilteredTasks"),
        taskList: document.getElementById("taskList"),

        search: document.getElementById("taskSearch"),
        statusFilter: document.getElementById("statusFilter"),
        priorityFilter: document.getElementById("priorityFilter"),
        clearFilters: document.getElementById("clearFiltersButton"),

        total: document.getElementById("totalTasks"),
        pending: document.getElementById("pendingTasks"),
        inProgress: document.getElementById("inProgressTasks"),
        completed: document.getElementById("completedTasks"),

        contributionOverview: document.getElementById("contributionOverview"),
        evaluatedTasks: document.getElementById("evaluatedTasks"),
        averageScore: document.getElementById("averageScore"),
        evaluationList: document.getElementById("evaluationList"),

        modal: document.getElementById("taskModal"),
        modalTitle: document.getElementById("taskModalTitle"),
        modalDetails: document.getElementById("taskModalDetails"),
        modalClose: document.getElementById("closeTaskModal"),
        modalCancel: document.getElementById("cancelSubmissionButton"),
        submissionForm: document.getElementById("submissionForm"),
        submissionText: document.getElementById("submissionText"),
        submissionMessage: document.getElementById("submissionMessage"),
        submitButton: document.getElementById("submitWorkButton")
    };

    let tasks = [];
    let activeTask = null;
    let isLoading = false;

    const fullName = user.full_name || "Student";

    elements.userName.textContent = fullName;
    elements.userAvatar.textContent = fullName.trim().charAt(0).toUpperCase() || "S";
    elements.currentYear.textContent = new Date().getFullYear();

    elements.logoutButton.addEventListener("click", async () => {
        try {
            await window.JOZSession.logout();
        } catch (error) {
            showMessage(error.message || "Unable to sign out.");
        }
    });

    elements.refreshButton.addEventListener("click", loadTasks);
    elements.search.addEventListener("input", renderTasks);
    elements.statusFilter.addEventListener("change", renderTasks);
    elements.priorityFilter.addEventListener("change", renderTasks);

    elements.clearFilters.addEventListener("click", () => {
        elements.search.value = "";
        elements.statusFilter.value = "all";
        elements.priorityFilter.value = "all";
        renderTasks();
    });

    elements.taskList.addEventListener("click", handleTaskAction);

    elements.modalClose.addEventListener("click", closeSubmissionModal);
    elements.modalCancel.addEventListener("click", closeSubmissionModal);

    elements.modal.addEventListener("click", (event) => {
        if (event.target === elements.modal) {
            closeSubmissionModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !elements.modal.hidden) {
            closeSubmissionModal();
        }
    });

    elements.submissionForm.addEventListener("submit", submitWork);

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    }

    function formatDate(value) {
        if (!value) return "Not specified";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "Date unavailable";
        }

        return new Intl.DateTimeFormat(undefined, {
            day: "numeric",
            month: "short",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit"
        }).format(date);
    }

    function isPastDeadline(value) {
        if (!value) return false;

        const date = new Date(value);

        return !Number.isNaN(date.getTime()) && date.getTime() < Date.now();
    }

    function showMessage(message, type = "error") {
        elements.message.textContent = message;
        elements.message.className =
            type === "success" ? "tasks-message success" : "tasks-message";
        elements.message.hidden = false;
    }

    function clearMessage() {
        elements.message.textContent = "";
        elements.message.hidden = true;
        elements.message.className = "tasks-message";
    }

    function showSubmissionMessage(message, type = "error") {
        elements.submissionMessage.textContent = message;
        elements.submissionMessage.className =
            type === "success"
                ? "submission-message success"
                : "submission-message";
        elements.submissionMessage.hidden = false;
    }

    function clearSubmissionMessage() {
        elements.submissionMessage.textContent = "";
        elements.submissionMessage.hidden = true;
        elements.submissionMessage.className = "submission-message";
    }

    function getStatusLabel(status) {
        const labels = {
            pending: "Pending",
            in_progress: "In Progress",
            submitted: "Submitted",
            completed: "Completed"
        };

        return labels[status] || status || "Unknown";
    }

    function getPriorityLabel(priority) {
        return String(priority || "medium").charAt(0).toUpperCase() +
            String(priority || "medium").slice(1);
    }

    function getSubmission(task) {
        return task.submission || null;
    }

    function getEvaluation(task) {
        return task.evaluation || null;
    }

    function updateSummary() {
        elements.total.textContent = tasks.length;

        elements.pending.textContent = tasks.filter(
            task => task.my_status === "pending"
        ).length;

        elements.inProgress.textContent = tasks.filter(
            task => task.my_status === "in_progress"
        ).length;

        elements.completed.textContent = tasks.filter(
            task => task.my_status === "completed"
        ).length;

        const evaluated = tasks.filter(task => getEvaluation(task));
        const scores = evaluated.map(task => Number(getEvaluation(task).score));

        const average = scores.length
            ? scores.reduce((sum, score) => sum + score, 0) / scores.length
            : null;

        elements.evaluatedTasks.textContent = evaluated.length;
        elements.averageScore.textContent =
            average === null ? "--" : `${average.toFixed(1)} / 100`;

        elements.contributionOverview.hidden = evaluated.length === 0;

        renderEvaluationList(evaluated);
    }

    function renderEvaluationList(evaluated) {
        elements.evaluationList.innerHTML = evaluated.map(task => {
            const evaluation = getEvaluation(task);

            return `
                <article class="evaluation-list-item">
                    <div>
                        <h4>${escapeHTML(task.title)}</h4>
                        <p>
                            Evaluated ${escapeHTML(formatDate(evaluation.evaluated_at))}
                            ${evaluation.feedback
                                ? `<br>${escapeHTML(evaluation.feedback)}`
                                : ""}
                        </p>
                    </div>

                    <strong class="evaluation-list-score">
                        ${Number(evaluation.score).toFixed(1)}
                    </strong>
                </article>
            `;
        }).join("");
    }

    function getFilteredTasks() {
        const searchTerm = elements.search.value.trim().toLowerCase();
        const selectedStatus = elements.statusFilter.value;
        const selectedPriority = elements.priorityFilter.value;

        return tasks.filter(task => {
            const matchesSearch =
                !searchTerm ||
                String(task.title || "").toLowerCase().includes(searchTerm) ||
                String(task.description || "").toLowerCase().includes(searchTerm);

            const matchesStatus =
                selectedStatus === "all" ||
                task.my_status === selectedStatus;

            const matchesPriority =
                selectedPriority === "all" ||
                task.priority === selectedPriority;

            return matchesSearch && matchesStatus && matchesPriority;
        });
    }

    function renderTasks() {
        const filteredTasks = getFilteredTasks();

        elements.waiting.hidden = true;
        elements.loading.hidden = true;

        if (tasks.length === 0) {
            elements.taskList.hidden = true;
            elements.noResults.hidden = true;
            elements.waiting.hidden = false;
            return;
        }

        if (filteredTasks.length === 0) {
            elements.taskList.hidden = true;
            elements.noResults.hidden = false;
            return;
        }

        elements.noResults.hidden = true;
        elements.taskList.hidden = false;

        elements.taskList.innerHTML = filteredTasks.map(renderTaskCard).join("");
    }

    function renderTaskCard(task) {
        const submission = getSubmission(task);
        const evaluation = getEvaluation(task);
        const overdue = isPastDeadline(task.deadline);

        const status = task.my_status || "pending";
        const priority = task.priority || "medium";

        const canStart =
            status === "pending" &&
            !["completed", "cancelled"].includes(task.task_status);

        const canSubmit =
            !["completed", "cancelled"].includes(task.task_status) &&
            !evaluation &&
            !overdue;

        let actionHTML = "";

        if (canStart) {
            actionHTML += `
                <button
                    type="button"
                    class="btn btn-outline btn-sm"
                    data-action="start"
                    data-assignee-id="${Number(task.assignee_id)}">
                    <i class="fa-solid fa-play"></i>
                    Start task
                </button>
            `;
        }

        if (canSubmit) {
            actionHTML += `
                <button
                    type="button"
                    class="btn btn-primary btn-sm"
                    data-action="submit"
                    data-assignee-id="${Number(task.assignee_id)}">
                    <i class="fa-solid fa-paper-plane"></i>
                    ${submission ? "Update submission" : "Submit work"}
                </button>
            `;
        }

        let actionNote = "";

        if (evaluation) {
            actionNote = "Your contribution has been evaluated.";
        } else if (overdue) {
            actionNote = "Deadline passed — ask your lecturer to extend it.";
        } else if (task.task_status === "cancelled") {
            actionNote = "This task has been cancelled.";
        } else if (task.task_status === "completed") {
            actionNote = "This task has been closed.";
        } else if (submission) {
            actionNote = "Your submission is awaiting lecturer evaluation.";
        } else if (status === "pending") {
            actionNote = "Start working when you are ready.";
        } else {
            actionNote = "Remember to submit your work before the deadline.";
        }

        const submissionHTML = submission ? `
            <section class="task-submission-preview">
                <h5><i class="fa-solid fa-file-lines"></i> Your latest submission</h5>
                <p>${escapeHTML(submission.submission_text)}</p>
                <span class="task-submission-date">
                    Submitted ${escapeHTML(formatDate(submission.submitted_at))}
                </span>
            </section>
        ` : "";

        const evaluationHTML = evaluation ? `
            <section class="task-evaluation">
                <div class="evaluation-score-row">
                    <h5><i class="fa-solid fa-award"></i> Lecturer evaluation</h5>
                    <strong class="evaluation-score">
                        ${Number(evaluation.score).toFixed(1)} / 100
                    </strong>
                </div>

                ${evaluation.feedback
                    ? `<p class="evaluation-feedback">${escapeHTML(evaluation.feedback)}</p>`
                    : '<p class="evaluation-feedback">No written feedback provided.</p>'}

                <span class="evaluation-date">
                    Evaluated ${escapeHTML(formatDate(evaluation.evaluated_at))}
                </span>
            </section>
        ` : "";

        return `
            <article class="task-card">

                <header class="task-card-header">
                    <div class="task-card-title">
                        <div class="task-badges">
                            <span class="task-badge priority-${escapeHTML(priority)}">
                                ${escapeHTML(getPriorityLabel(priority))} priority
                            </span>

                            <span class="task-badge status-${escapeHTML(status)}">
                                ${escapeHTML(getStatusLabel(status))}
                            </span>
                        </div>

                        <h4>${escapeHTML(task.title)}</h4>
                        <p>${escapeHTML(task.description)}</p>
                    </div>
                </header>

                <div class="task-card-meta">
                    <span class="task-meta-item ${overdue ? "overdue" : ""}">
                        <i class="fa-regular fa-calendar"></i>
                        Deadline: ${escapeHTML(formatDate(task.deadline))}
                    </span>

                    <span class="task-meta-item">
                        <i class="fa-regular fa-clock"></i>
                        Assigned: ${escapeHTML(formatDate(task.assigned_at))}
                    </span>

                    ${overdue && !evaluation
                        ? `
                            <span class="task-meta-item deadline-passed">
                                <i class="fa-solid fa-triangle-exclamation"></i>
                                Overdue
                            </span>
                        `
                        : ""}
                </div>

                <div class="task-card-body">
                    ${submissionHTML}
                    ${evaluationHTML}

                    <div class="task-card-actions">
                        <span class="task-action-note">
                            ${escapeHTML(actionNote)}
                        </span>

                        <div class="action-group">
                            ${actionHTML}
                        </div>
                    </div>
                </div>

            </article>
        `;
    }

    async function loadTasks() {
        if (isLoading) return;

        isLoading = true;
        clearMessage();

        elements.refreshButton.disabled = true;
        elements.loading.hidden = false;
        elements.waiting.hidden = true;
        elements.noResults.hidden = true;
        elements.taskList.hidden = true;

        try {
            const response = await window.JOZApi.get("/api/student/tasks");

            tasks = Array.isArray(response?.tasks)
                ? response.tasks
                : [];

            updateSummary();
            renderTasks();

        } catch (error) {
            tasks = [];
            updateSummary();

            elements.loading.hidden = true;
            elements.waiting.hidden = true;
            elements.taskList.hidden = true;

            showMessage(
                error.message ||
                "Unable to load your tasks. Please try again."
            );

        } finally {
            isLoading = false;
            elements.refreshButton.disabled = false;
        }
    }

    async function handleTaskAction(event) {
        const button = event.target.closest("[data-action]");

        if (!button) return;

        const action = button.dataset.action;
        const assigneeId = Number(button.dataset.assigneeId);

        if (!Number.isInteger(assigneeId) || assigneeId <= 0) {
            showMessage("Invalid task assignment.");
            return;
        }

        const task = tasks.find(
            item => Number(item.assignee_id) === assigneeId
        );

        if (!task) {
            showMessage("Task assignment could not be found.");
            return;
        }

        if (action === "start") {
            await startTask(task, button);
        }

        if (action === "submit") {
            openSubmissionModal(task);
        }
    }

    async function startTask(task, button) {
        if (task.my_status !== "pending") return;

        button.disabled = true;

        try {
            await window.JOZApi.patchWithCsrf(
            `/api/student/tasks/assignments/${task.assignee_id}/status`,
            { status: "in_progress" }
        );

            showMessage("Task started successfully.", "success");
            await loadTasks();

        } catch (error) {
            button.disabled = false;
            showMessage(
                error.message || "Unable to update task status."
            );
        }
    }

    function openSubmissionModal(task) {
        activeTask = task;

        const submission = getSubmission(task);

        elements.modalTitle.textContent = submission
            ? "Update your submission"
            : "Submit your work";

        elements.modalDetails.innerHTML = `
            <strong>${escapeHTML(task.title)}</strong><br>
            Deadline: ${escapeHTML(formatDate(task.deadline))}<br>
            Current status: ${escapeHTML(getStatusLabel(task.my_status))}
        `;

        elements.submissionText.value = submission
            ? submission.submission_text
            : "";

        elements.submitButton.innerHTML = submission
            ? '<i class="fa-solid fa-floppy-disk"></i> Update submission'
            : '<i class="fa-solid fa-paper-plane"></i> Submit work';

        clearSubmissionMessage();

        elements.modal.hidden = false;
        document.body.style.overflow = "hidden";

        elements.submissionText.focus();
    }

    function closeSubmissionModal() {
        elements.modal.hidden = true;
        document.body.style.overflow = "";
        activeTask = null;
        elements.submissionForm.reset();
        clearSubmissionMessage();
        elements.submitButton.disabled = false;
    }

    async function submitWork(event) {
        event.preventDefault();

        if (!activeTask) return;

        const submissionText = elements.submissionText.value.trim();

        if (!submissionText) {
            showSubmissionMessage("Please enter your work before submitting.");
            return;
        }

        if (submissionText.length > 10000) {
            showSubmissionMessage("Your submission is too long.");
            return;
        }

        const assigneeId = activeTask.assignee_id;

        elements.submitButton.disabled = true;
        elements.submitButton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';

        clearSubmissionMessage();

        try {
            await window.JOZApi.postWithCsrf(
                `/api/student/tasks/assignments/${assigneeId}/submission`,
                { submission_text: submissionText }
            );

            closeSubmissionModal();
            showMessage("Your work was submitted successfully.", "success");

            await loadTasks();

        } catch (error) {
            showSubmissionMessage(
                error.message || "Unable to submit your work."
            );

            elements.submitButton.disabled = false;
            elements.submitButton.innerHTML =
                '<i class="fa-solid fa-paper-plane"></i> Try again';
        }
    }

    await loadTasks();
}
