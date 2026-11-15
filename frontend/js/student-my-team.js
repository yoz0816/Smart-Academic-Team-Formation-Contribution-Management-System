"use strict";

document.addEventListener("DOMContentLoaded", initializeStudentMyTeam);

async function initializeStudentMyTeam() {
    const user = await window.JOZSession.requireRole(["student"]);

    if (!user) return;

    const teamLoading = document.getElementById("teamLoading");
    const waitingState = document.getElementById("teamWaitingState");
    const teamList = document.getElementById("teamList");
    const teamMessage = document.getElementById("teamMessage");
    const refreshButton = document.getElementById("refreshTeamButton");

    const fullName = user.full_name || "Student";

    document.getElementById("userName").textContent = fullName;
    document.getElementById("userAvatar").textContent =
        fullName.charAt(0).toUpperCase();

    document.getElementById("currentYear").textContent =
        new Date().getFullYear();

    document.getElementById("logoutButton").addEventListener(
        "click",
        async () => {
            try {
                await window.JOZSession.logout();
            } catch (error) {
                showError(error.message || "Unable to sign out.");
            }
        }
    );

    refreshButton.addEventListener("click", loadTeams);

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
        if (!value) return "Not announced";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "Date unavailable";
        }

        return new Intl.DateTimeFormat(undefined, {
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit"
        }).format(date);
    }

    function showError(message) {
        teamMessage.textContent = message;
        teamMessage.hidden = false;
    }

    function clearError() {
        teamMessage.textContent = "";
        teamMessage.hidden = true;
    }

    function showLoading() {
        teamLoading.hidden = false;
        waitingState.hidden = true;
        teamList.hidden = true;
        refreshButton.disabled = true;
    }

    function hideLoading() {
        teamLoading.hidden = true;
        refreshButton.disabled = false;
    }

    function renderWaitingState() {
        waitingState.hidden = false;
        teamList.hidden = true;
    }

    function renderTeams(teams) {
        waitingState.hidden = true;
        teamList.hidden = false;

        teamList.innerHTML = teams.map((team) => {
            const assignment = team.assignment || {};
            const course = assignment.course || {};
            const lecturer = assignment.lecturer || {};
            const members = Array.isArray(team.members) ? team.members : [];

            const memberCards = members.map((member) => {
                const name = member.full_name || "Student";
                const initial = name.trim().charAt(0).toUpperCase() || "S";
                const isCurrentStudent = Number(member.user_id) === Number(user.id);

                return `
                    <article class="team-member-card">
                        <div class="member-avatar">
                            ${escapeHTML(initial)}
                        </div>

                        <div class="member-information">
                            <h5>${escapeHTML(name)}</h5>

                            <a href="mailto:${escapeHTML(member.email)}">
                                ${escapeHTML(member.email)}
                            </a>

                            ${isCurrentStudent
                                ? '<span class="member-you-label">You</span>'
                                : ""}
                        </div>
                    </article>
                `;
            }).join("");

            const timelineItems = [
                {
                    label: "Assignment opens",
                    date: assignment.opens_at,
                    icon: "fa-folder-open"
                },
                {
                    label: "Assignment deadline",
                    date: assignment.deadline,
                    icon: "fa-calendar-check"
                },
                {
                    label: "Proposal opens",
                    date: assignment.proposal_opens_at,
                    icon: "fa-file-circle-plus"
                },
                {
                    label: "Proposal deadline",
                    date: assignment.proposal_deadline,
                    icon: "fa-file-circle-check"
                },
                {
                    label: "Modification deadline",
                    date: assignment.modification_deadline,
                    icon: "fa-pen-to-square"
                },
                {
                    label: "Final project submission",
                    date: assignment.final_submission_deadline,
                    icon: "fa-flag-checkered"
                }
            ];

            const timelineHTML = timelineItems.map((item) => {
                if (!item.date) return "";

                const date = new Date(item.date);
                const isPast = !Number.isNaN(date.getTime()) &&
                    date.getTime() < Date.now();

                return `
                    <article class="timeline-item ${isPast ? "is-past" : ""}">
                        <div class="timeline-icon">
                            <i class="fa-solid ${item.icon}"></i>
                        </div>

                        <div>
                            <h5>${escapeHTML(item.label)}</h5>
                            <p>${escapeHTML(formatDate(item.date))}</p>
                        </div>
                    </article>
                `;
            }).join("");

            return `
                <article class="team-card">

                    <header class="team-card-header">
                        <div class="team-card-title">
                            <div class="team-icon">
                                <i class="fa-solid fa-people-group"></i>
                            </div>

                            <div>
                                <h3>${escapeHTML(team.team_name)}</h3>
                                <p>
                                    ${escapeHTML(course.course_code || "Academic course")}
                                    &mdash;
                                    ${escapeHTML(course.course_name || "Course details")}
                                </p>
                            </div>
                        </div>

                        <span class="team-published-badge">
                            <i class="fa-solid fa-circle-check"></i>
                            Published
                        </span>
                    </header>

                    <div class="team-card-body">

                        <section>
                            <div class="team-section-heading">
                                <div>
                                    <h4>Team members</h4>
                                    <p>Your assigned academic project teammates.</p>
                                </div>

                                <span class="team-member-count">
                                    ${members.length}
                                    ${members.length === 1 ? "Member" : "Members"}
                                </span>
                            </div>

                            <div class="team-members-grid">
                                ${memberCards}
                            </div>
                        </section>

                        <section class="team-information-grid">
                            <div class="team-information-item">
                                <span>Academic assignment</span>
                                <strong>${escapeHTML(assignment.title || "Not available")}</strong>
                            </div>

                            <div class="team-information-item">
                                <span>Responsible lecturer</span>
                                <strong>${escapeHTML(lecturer.full_name || "Not available")}</strong>
                            </div>

                            <div class="team-information-item">
                                <span>Course</span>
                                <strong>
                                    ${escapeHTML(course.course_code || "")}
                                    ${course.course_name ? " — " + escapeHTML(course.course_name) : ""}
                                </strong>
                            </div>

                            <div class="team-information-item">
                                <span>Team assignment date</span>
                                <strong>${escapeHTML(formatDate(team.assigned_at))}</strong>
                            </div>
                        </section>

                        ${assignment.description || assignment.instructions
                            ? `
                                <section class="team-assignment-description">
                                    <h5>Project information</h5>
                                    ${assignment.description
                                        ? `<p>${escapeHTML(assignment.description)}</p>`
                                        : ""}
                                    ${assignment.instructions
                                        ? `<p>${escapeHTML(assignment.instructions)}</p>`
                                        : ""}
                                </section>
                            `
                            : ""}

                        ${timelineHTML
                            ? `
                                <section class="team-timeline">
                                    <div class="team-section-heading">
                                        <div>
                                            <h4>Project timeline</h4>
                                            <p>Important dates for your academic assignment.</p>
                                        </div>
                                    </div>

                                    <div class="team-timeline-grid">
                                        ${timelineHTML}
                                    </div>
                                </section>
                            `
                            : ""}

                    </div>
                </article>
            `;
        }).join("");
    }

    async function loadTeams() {
        clearError();
        showLoading();

        try {
            const response = await window.JOZApi.get("/api/student/my-team");

            const teams = Array.isArray(response?.teams)
                ? response.teams
                : [];

            hideLoading();

            if (teams.length === 0) {
                renderWaitingState();
                return;
            }

            renderTeams(teams);

        } catch (error) {
            hideLoading();

            teamList.hidden = true;
            waitingState.hidden = true;

            showError(
                error.message ||
                "Unable to load your team information. Please try again."
            );
        }
    }

    await loadTeams();
}