"use strict";

document.addEventListener("DOMContentLoaded", initializeStudentSkills);

async function initializeStudentSkills() {
    const user = await window.JOZSession.requireRole(["student"]);

    if (!user) return;

    const form = document.getElementById("skillForm");
    const skillNameInput = document.getElementById("skillName");
    const categoryInput = document.getElementById("skillCategory");
    const proficiencyInput = document.getElementById("skillProficiency");
    const saveButton = document.getElementById("saveSkillButton");
    const cancelButton = document.getElementById("cancelEditButton");
    const message = document.getElementById("skillFormMessage");
    const skillsList = document.getElementById("skillsList");

    let skills = [];
    let editingSkillId = null;

    const fullName = user.full_name || "Student";

    document.getElementById("userName").textContent = fullName;
    document.getElementById("userAvatar").textContent =
        fullName.charAt(0).toUpperCase();

    document.getElementById("currentYear").textContent =
        new Date().getFullYear();

    document.getElementById("logoutButton").addEventListener("click", async () => {
        try {
            await window.JOZSession.logout();
        } catch (error) {
            showMessage(error.message || "Unable to sign out.", "error");
        }
    });

    function showMessage(text, type = "") {
        message.textContent = text;
        message.className = "skills-form-message";

        if (type === "success") {
            message.classList.add("is-success");
        } else if (type === "error") {
            message.classList.add("is-error");
        }
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    }

    function getSkillIcon(category) {
        const icons = {
            "Programming Languages": "fa-code",
            "Frameworks & Tools": "fa-layer-group",
            "Databases": "fa-database",
            "Mobile Development": "fa-mobile-screen-button",
            "UI/UX Design": "fa-pen-ruler",
            "Testing & QA": "fa-vial",
            "Other": "fa-laptop-code"
        };

        return icons[category] || "fa-laptop-code";
    }

    function updateSkillCounters() {
        const total = skills.length;

        document.getElementById("totalSkills").textContent = total;
        document.getElementById("skillsCount").textContent =
            `${total} ${total === 1 ? "skill" : "skills"}`;
    }

    function renderSkills() {
        updateSkillCounters();

        if (skills.length === 0) {
            skillsList.innerHTML = `
                <div class="skills-empty">
                    <i class="fa-solid fa-code"></i>
                    <h4>No technical skills added yet</h4>
                    <p>
                        Start building your technical profile by adding
                        your first skill using the form.
                    </p>
                </div>
            `;
            return;
        }

        skillsList.innerHTML = skills.map((skill) => {
            const icon = getSkillIcon(skill.category);

            return `
                <article class="skill-card">
                    <div class="skill-card-main">
                        <div class="skill-card-icon">
                            <i class="fa-solid ${icon}"></i>
                        </div>

                        <div class="skill-card-info">
                            <h4>${escapeHTML(skill.skill_name)}</h4>
                            <span class="skill-card-category">
                                ${escapeHTML(skill.category)}
                            </span>

                            <div class="skill-card-meta">
                                <span class="skill-proficiency">
                                    ${escapeHTML(skill.proficiency)}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="skill-card-actions">
                        <button
                            type="button"
                            class="skill-action-button"
                            data-action="edit"
                            data-id="${Number(skill.id)}"
                            aria-label="Edit ${escapeHTML(skill.skill_name)}"
                            title="Edit skill"
                        >
                            <i class="fa-solid fa-pen"></i>
                        </button>

                        <button
                            type="button"
                            class="skill-action-button delete"
                            data-action="delete"
                            data-id="${Number(skill.id)}"
                            aria-label="Delete ${escapeHTML(skill.skill_name)}"
                            title="Delete skill"
                        >
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </article>
            `;
        }).join("");
    }

    function resetForm() {
        form.reset();
        editingSkillId = null;

        document.getElementById("formHeading").textContent =
            "Add a technical skill";

        document.getElementById("formDescription").textContent =
            "Enter a skill and select your proficiency.";

        saveButton.innerHTML =
            '<i class="fa-solid fa-plus"></i><span>Add Skill</span>';

        cancelButton.hidden = true;
        showMessage("");
    }

    function startEditing(skillId) {
        const skill = skills.find((item) => item.id === skillId);

        if (!skill) return;

        editingSkillId = skill.id;

        skillNameInput.value = skill.skill_name;
        categoryInput.value = skill.category;
        proficiencyInput.value = skill.proficiency;

        document.getElementById("formHeading").textContent =
            "Edit technical skill";

        document.getElementById("formDescription").textContent =
            "Update the skill information and save your changes.";

        saveButton.innerHTML =
            '<i class="fa-solid fa-floppy-disk"></i><span>Save Changes</span>';

        cancelButton.hidden = false;
        showMessage("");

        skillNameInput.focus();
        form.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    async function loadSkills() {
        skillsList.innerHTML = `
            <div class="skills-loading">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <span>Loading your skills...</span>
            </div>
        `;

        try {
            const response = await window.JOZApi.get("/api/student/skills");

            if (Array.isArray(response)) {
                skills = response;
            } else {
                skills = response?.skills ?? response?.items ?? [];
            }

            renderSkills();
        } catch (error) {
            skillsList.innerHTML = `
                <div class="skills-empty">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <h4>Unable to load your skills</h4>
                    <p>${escapeHTML(error.message || "Please refresh the page and try again.")}</p>
                </div>
            `;
        }
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const skillName = skillNameInput.value.trim();
        const category = categoryInput.value;
        const proficiency = proficiencyInput.value;

        if (!skillName) {
            showMessage("Please enter a skill name.", "error");
            skillNameInput.focus();
            return;
        }

        if (!category || !proficiency) {
            showMessage("Please select a category and proficiency level.", "error");
            return;
        }

        const payload = {
            skill_name: skillName,
            category,
            proficiency
        };

        const isEditing = editingSkillId !== null;

        saveButton.disabled = true;
        cancelButton.disabled = true;

        saveButton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i><span>Saving...</span>';

        showMessage(isEditing ? "Updating your skill..." : "Adding your skill...");

        try {
            if (isEditing) {
                await window.JOZApi.put(
                    `/api/student/skills/${editingSkillId}`,
                    payload
                );
            } else {
                await window.JOZApi.post(
                    "/api/student/skills",
                    payload
                );
            }

            resetForm();
            await loadSkills();

            showMessage(
                isEditing
                    ? "Your skill has been updated successfully."
                    : "Your skill has been added successfully.",
                "success"
            );
        } catch (error) {
            showMessage(
                error.message || "Unable to save your skill.",
                "error"
            );
        } finally {
            saveButton.disabled = false;
            cancelButton.disabled = false;

            if (editingSkillId !== null) {
                saveButton.innerHTML =
                    '<i class="fa-solid fa-floppy-disk"></i><span>Save Changes</span>';
            } else {
                saveButton.innerHTML =
                    '<i class="fa-solid fa-plus"></i><span>Add Skill</span>';
            }
        }
    });

    cancelButton.addEventListener("click", resetForm);

    skillsList.addEventListener("click", async (event) => {
        const button = event.target.closest("button[data-action]");

        if (!button) return;

        const skillId = Number(button.dataset.id);
        const action = button.dataset.action;

        if (!Number.isInteger(skillId) || skillId <= 0) return;

        if (action === "edit") {
            startEditing(skillId);
            return;
        }

        if (action === "delete") {
            const skill = skills.find((item) => item.id === skillId);

            if (!skill) return;

            const confirmed = window.confirm(
                `Are you sure you want to delete "${skill.skill_name}"?`
            );

            if (!confirmed) return;

            button.disabled = true;

            try {
                await window.JOZApi.delete(
                    `/api/student/skills/${skillId}`
                );

                if (editingSkillId === skillId) {
                    resetForm();
                }

                await loadSkills();
                showMessage("The skill has been deleted successfully.", "success");
            } catch (error) {
                button.disabled = false;
                showMessage(
                    error.message || "Unable to delete this skill.",
                    "error"
                );
            }
        }
    });

    await loadSkills();
}
