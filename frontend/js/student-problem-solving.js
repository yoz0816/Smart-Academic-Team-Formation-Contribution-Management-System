"use strict";

document.addEventListener("DOMContentLoaded", async () => {
    const API_ENDPOINT = "/api/student/problem-solving";

    const CATEGORIES = [
        {
            name: "Logical Thinking",
            icon: "◇"
        },
        {
            name: "Analytical Thinking",
            icon: "⌕"
        },
        {
            name: "Critical Thinking",
            icon: "◎"
        },
        {
            name: "Creativity",
            icon: "✦"
        },
        {
            name: "Decision-Making",
            icon: "⚖"
        },
        {
            name: "Technical Problem-Solving",
            icon: "⌘"
        }
    ];

    const PROFICIENCIES = [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert"
    ];

    const assessmentsContainer =
        document.getElementById("problemAssessments");

    const assessmentCount =
        document.getElementById("assessmentCount");

    const statusElement =
        document.getElementById("problemPageStatus");

    let assessments = new Map();
    let draftLevels = new Map();
    let isLoading = true;
    let busyCategory = null;

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
        if (!statusElement) return;

        statusElement.textContent = message;
        statusElement.className = `problem-page-status ${type}`.trim();
    }

    function updateUserDetails(user) {
        const name = user?.full_name || "Student";

        const nameElement = document.getElementById("userName");
        const avatarElement = document.getElementById("userAvatar");
        const yearElement = document.getElementById("currentYear");

        if (nameElement) {
            nameElement.textContent = name;
        }

        if (avatarElement) {
            avatarElement.textContent = name.charAt(0).toUpperCase();
        }

        if (yearElement) {
            yearElement.textContent = new Date().getFullYear();
        }
    }

    function updateCounter() {
        assessmentCount.textContent = `${assessments.size}/6`;
    }

    function hasChanges(category) {
        const saved = assessments.get(category);
        const draft = draftLevels.get(category) || "";

        if (!draft) {
            return false;
        }

        return !saved || saved.proficiency !== draft;
    }

    function renderAssessments() {
        updateCounter();

        assessmentsContainer.innerHTML = CATEGORIES.map(
            (item, index) => {
                const category = item.name;
                const saved = assessments.get(category);
                const selectedLevel = draftLevels.get(category) || "";
                const isAssessed = Boolean(saved);
                const isBusy = busyCategory === category;

                const options = PROFICIENCIES.map((level) => `
                    <option
                        value="${level}"
                        ${selectedLevel === level ? "selected" : ""}
                    >${level}</option>
                `).join("");

                const saveLabel = isBusy
                    ? "Saving..."
                    : saved
                        ? "Update Assessment"
                        : "Save Assessment";

                const saveDisabled =
                    isLoading ||
                    isBusy ||
                    !hasChanges(category);

                return `
                    <article class="problem-assessment-card
                        ${isAssessed ? "is-assessed" : ""}"
                        data-category="${escapeHTML(category)}">

                        <div class="problem-card-top">
                            <div class="problem-card-identity">
                                <span class="problem-card-icon"
                                      aria-hidden="true">
                                    ${item.icon}
                                </span>

                                <h3 class="problem-card-title">
                                    ${escapeHTML(category)}
                                </h3>
                            </div>

                            <span class="problem-card-number">
                                ${String(index + 1).padStart(2, "0")}
                            </span>
                        </div>

                        <p class="problem-card-status">
                            ${isAssessed ? "Assessment saved" : "Not assessed yet"}
                        </p>

                        <label
                            class="problem-field-label"
                            for="proficiency-${index}"
                        >
                            Your proficiency level
                        </label>

                        <select
                            class="problem-proficiency-select"
                            id="proficiency-${index}"
                            data-proficiency="${escapeHTML(category)}"
                            ${isLoading || isBusy ? "disabled" : ""}
                        >
                            <option value="">Choose proficiency</option>
                            ${options}
                        </select>

                        <div class="problem-card-actions">
                            <button
                                type="button"
                                class="problem-save-button"
                                data-save-category="${escapeHTML(category)}"
                                ${saveDisabled ? "disabled" : ""}
                            >
                                ${saveLabel}
                            </button>

                            ${saved ? `
                                <button
                                    type="button"
                                    class="problem-remove-button"
                                    data-remove-category="${escapeHTML(category)}"
                                    ${isBusy ? "disabled" : ""}
                                >
                                    Remove
                                </button>
                            ` : ""}
                        </div>
                    </article>
                `;
            }
        ).join("");
    }

    async function loadAssessments() {
        isLoading = true;
        renderAssessments();

        try {
            const response = await window.JOZApi.get(API_ENDPOINT);

            const records = Array.isArray(response?.abilities)
                ? response.abilities
                : [];

            assessments.clear();
            draftLevels.clear();

            records.forEach((record) => {
                if (
                    !CATEGORIES.some((item) => item.name === record.category) ||
                    !PROFICIENCIES.includes(record.proficiency)
                ) {
                    return;
                }

                assessments.set(record.category, {
                    id: Number(record.id),
                    category: record.category,
                    proficiency: record.proficiency
                });

                draftLevels.set(record.category, record.proficiency);
            });

            showStatus(
                assessments.size
                    ? "Your saved problem-solving assessments have been loaded."
                    : "You have not assessed any categories yet."
            );
        } catch (error) {
            showStatus(
                error.message || "Unable to load your assessments.",
                "error"
            );

            throw error;
        } finally {
            isLoading = false;
            renderAssessments();
        }
    }

    async function saveAssessment(category) {
        if (isLoading || busyCategory) return;

        const proficiency = draftLevels.get(category);

        if (!PROFICIENCIES.includes(proficiency)) {
            showStatus("Please choose a valid proficiency level.", "error");
            return;
        }

        if (!hasChanges(category)) return;

        const existing = assessments.get(category);

        busyCategory = category;
        renderAssessments();
        showStatus(`Saving your ${category} assessment...`);

        try {
            const payload = {
                category,
                proficiency
            };

            const response = existing
                ? await window.JOZApi.put(
                    `${API_ENDPOINT}/${existing.id}`,
                    payload
                )
                : await window.JOZApi.post(
                    API_ENDPOINT,
                    payload
                );

            assessments.set(category, {
                id: Number(response.id),
                category: response.category,
                proficiency: response.proficiency
            });

            draftLevels.set(category, response.proficiency);

            showStatus(
                `${category} assessment saved successfully.`,
                "success"
            );
        } catch (error) {
            showStatus(
                error.message || `Unable to save ${category}.`,
                "error"
            );
        } finally {
            busyCategory = null;
            renderAssessments();
        }
    }

    async function removeAssessment(category) {
        if (isLoading || busyCategory) return;

        const existing = assessments.get(category);

        if (!existing) return;

        busyCategory = category;
        renderAssessments();
        showStatus(`Removing your ${category} assessment...`);

        try {
            await window.JOZApi.delete(
                `${API_ENDPOINT}/${existing.id}`
            );

            assessments.delete(category);
            draftLevels.delete(category);

            showStatus(
                `${category} assessment removed successfully.`,
                "success"
            );
        } catch (error) {
            showStatus(
                error.message || `Unable to remove ${category}.`,
                "error"
            );
        } finally {
            busyCategory = null;
            renderAssessments();
        }
    }

    assessmentsContainer.addEventListener("change", (event) => {
        const select = event.target.closest("[data-proficiency]");

        if (!select || isLoading || busyCategory) return;

        const category = select.dataset.proficiency;
        const proficiency = select.value;

        if (proficiency === "") {
            draftLevels.delete(category);
        } else {
            draftLevels.set(category, proficiency);
        }

        renderAssessments();
    });

    assessmentsContainer.addEventListener("click", (event) => {
        const saveButton = event.target.closest("[data-save-category]");

        if (saveButton) {
            saveAssessment(saveButton.dataset.saveCategory);
            return;
        }

        const removeButton = event.target.closest("[data-remove-category]");

        if (removeButton) {
            removeAssessment(removeButton.dataset.removeCategory);
        }
    });

    try {
        const user = await window.JOZSession.requireRole(["student"]);

        if (!user) return;

        updateUserDetails(user);

        const logoutButton = document.getElementById("logoutButton");

        logoutButton?.addEventListener("click", () => {
            window.JOZSession.logout();
        });

        await loadAssessments();
    } catch (error) {
        console.error(
            "Problem-Solving page initialization failed:",
            error
        );

        isLoading = false;
        renderAssessments();

        showStatus(
            error.message || "Unable to initialize the Problem-Solving page.",
            "error"
        );
    }
});
