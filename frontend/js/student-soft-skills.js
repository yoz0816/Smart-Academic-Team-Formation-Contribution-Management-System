document.addEventListener("DOMContentLoaded", async () => {
    const SOFT_SKILLS = [
        {
            name: "Communication",
            icon: "◉",
            description: "Expressing ideas clearly, listening actively, and sharing information effectively."
        },
        {
            name: "Leadership",
            icon: "♛",
            description: "Guiding teammates, taking initiative, and helping a team achieve its goals."
        },
        {
            name: "Teamwork",
            icon: "♧",
            description: "Collaborating with others, sharing responsibilities, and supporting team members."
        },
        {
            name: "Time Management",
            icon: "◷",
            description: "Organizing tasks, meeting deadlines, and using time productively."
        },
        {
            name: "Adaptability",
            icon: "⟳",
            description: "Adjusting to changes, learning from challenges, and responding to new situations."
        },
        {
            name: "Responsibility",
            icon: "✓",
            description: "Being accountable, completing assigned work, and following through on commitments."
        }
    ];

    const PROFICIENCIES = [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert"
    ];

    const grid = document.getElementById("softSkillsGrid");
    const selectedCount = document.getElementById("selectedCount");
    const saveButton = document.getElementById("saveSoftSkillsButton");
    const statusElement = document.getElementById("softSkillsStatus");

    let savedSkills = new Map();
    let selectedSkills = new Map();
    let isLoading = true;
    let isSaving = false;

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
        statusElement.className = `soft-skills-status ${type}`.trim();
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

    function hasUnsavedChanges() {
        if (selectedSkills.size !== savedSkills.size) return true;

        for (const [name, proficiency] of selectedSkills) {
            if (savedSkills.get(name)?.proficiency !== proficiency) {
                return true;
            }
        }

        return false;
    }

    function updateSelectionUI() {
        selectedCount.textContent = `${selectedSkills.size}/6`;

        saveButton.disabled =
            isLoading || isSaving || !hasUnsavedChanges();

        saveButton.querySelector("span:first-child").textContent =
            isSaving ? "Saving..." : "Save Soft Skills";
    }

    function renderSkills() {
        grid.innerHTML = SOFT_SKILLS.map((skill, index) => {
            const selected = selectedSkills.has(skill.name);
            const proficiency = selected
                ? selectedSkills.get(skill.name)
                : "Intermediate";

            const safeName = escapeHTML(skill.name);
            const safeDescription = escapeHTML(skill.description);

            return `
                <article class="soft-skill-card ${selected ? "selected" : ""}">
                    <div class="soft-skill-card-top">
                        <span class="soft-skill-icon" aria-hidden="true">
                            ${skill.icon}
                        </span>

                        <label class="soft-skill-toggle">
                            <input
                                type="checkbox"
                                data-skill-toggle="${safeName}"
                                ${selected ? "checked" : ""}
                                ${isSaving ? "disabled" : ""}
                                aria-label="Select ${safeName}"
                            >
                            <span class="soft-skill-toggle-track"></span>
                        </label>
                    </div>

                    <h3>${safeName}</h3>
                    <p>${safeDescription}</p>

                    <div class="soft-skill-proficiency">
                        <label for="softSkillLevel${index}">
                            Proficiency level
                        </label>

                        <select
                            id="softSkillLevel${index}"
                            data-skill-level="${safeName}"
                            ${!selected || isSaving ? "disabled" : ""}
                        >
                            ${PROFICIENCIES.map((level) => `
                                <option value="${level}"
                                    ${proficiency === level ? "selected" : ""}>
                                    ${level}
                                </option>
                            `).join("")}
                        </select>
                    </div>

                    <span class="soft-skill-selection-label">
                        ${selected ? "Selected" : "Not selected"}
                    </span>
                </article>
            `;
        }).join("");

        updateSelectionUI();
    }

    async function loadSoftSkills() {
        try {
            const response = await window.JOZApi.get(
                "/api/student/soft-skills"
            );

            const records = Array.isArray(response?.soft_skills)
                ? response.soft_skills
                : [];

            savedSkills.clear();
            selectedSkills.clear();

            records.forEach((record) => {
                if (
                    SOFT_SKILLS.some((skill) => skill.name === record.skill_name) &&
                    PROFICIENCIES.includes(record.proficiency)
                ) {
                    const entry = {
                        id: Number(record.id),
                        proficiency: record.proficiency
                    };

                    savedSkills.set(record.skill_name, entry);
                    selectedSkills.set(record.skill_name, record.proficiency);
                }
            });

            renderSkills();

            showStatus(
                selectedSkills.size
                    ? "Your saved soft skills have been loaded."
                    : "Select the soft skills that describe you."
            );
        } catch (error) {
            grid.innerHTML = `
                <div class="soft-skills-empty">
                    Unable to load your soft skills. Please refresh the page.
                </div>
            `;

            showStatus(
                error.message || "Could not load your soft skills.",
                "error"
            );

            throw error;
        } finally {
            isLoading = false;
            updateSelectionUI();
        }
    }

    function handleSkillToggle(skillName, checked) {
        if (isLoading || isSaving) return;

        if (!SOFT_SKILLS.some((skill) => skill.name === skillName)) {
            return;
        }

        if (checked) {
            selectedSkills.set(skillName, "Intermediate");
            showStatus("Skill selected. Choose its proficiency level.");
        } else {
            selectedSkills.delete(skillName);
            showStatus("Skill removed from your selection.");
        }

        renderSkills();
    }

    function handleProficiencyChange(skillName, proficiency) {
        if (isLoading || isSaving) return;

        if (
            !selectedSkills.has(skillName) ||
            !PROFICIENCIES.includes(proficiency)
        ) {
            return;
        }

        selectedSkills.set(skillName, proficiency);
        showStatus("Proficiency updated. Save your changes.");
        updateSelectionUI();
    }

    async function saveSoftSkills() {
        if (isLoading || isSaving || !hasUnsavedChanges()) return;

        isSaving = true;
        updateSelectionUI();
        renderSkills();
        showStatus("Saving your soft skills...");

        try {
            for (const [name, record] of savedSkills) {
                if (!selectedSkills.has(name)) {
                    await window.JOZApi.delete(
                        `/api/student/soft-skills/${record.id}`
                    );
                }
            }
            for (const [name, proficiency] of selectedSkills) {
                const existing = savedSkills.get(name);

                if (!existing) {
                    await window.JOZApi.post(
                        "/api/student/soft-skills",
                        {
                            skill_name: name,
                            proficiency
                        }
                    );
                } else if (existing.proficiency !== proficiency) {
                    await window.JOZApi.put(
                        `/api/student/soft-skills/${existing.id}`,
                        {
                            skill_name: name,
                            proficiency
                        }
                    );
                }
            }

            const response = await window.JOZApi.get(
                "/api/student/soft-skills"
            );

            const records = Array.isArray(response?.soft_skills)
                ? response.soft_skills
                : [];

            savedSkills.clear();
            selectedSkills.clear();

            records.forEach((record) => {
                savedSkills.set(record.skill_name, {
                    id: Number(record.id),
                    proficiency: record.proficiency
                });

                selectedSkills.set(
                    record.skill_name,
                    record.proficiency
                );
            });

            showStatus(
                "Your soft skills have been saved successfully.",
                "success"
            );
        } catch (error) {
            showStatus(
                error.message ||
                "Some changes could not be saved. Reload your skills before trying again.",
                "error"
            );

            try {
                const response = await window.JOZApi.get(
                    "/api/student/soft-skills"
                );

                const records = Array.isArray(response?.soft_skills)
                    ? response.soft_skills
                    : [];

                savedSkills.clear();
                selectedSkills.clear();

                records.forEach((record) => {
                    savedSkills.set(record.skill_name, {
                        id: Number(record.id),
                        proficiency: record.proficiency
                    });

                    selectedSkills.set(
                        record.skill_name,
                        record.proficiency
                    );
                });
            } catch (refreshError) {
                console.error("Could not refresh soft skills:", refreshError);
            }
        } finally {
            isSaving = false;
            renderSkills();
        }
    }

    grid.addEventListener("change", (event) => {
        const toggle = event.target.closest("[data-skill-toggle]");

        if (toggle) {
            handleSkillToggle(
                toggle.dataset.skillToggle,
                toggle.checked
            );
            return;
        }

        const levelSelect = event.target.closest("[data-skill-level]");

        if (levelSelect) {
            handleProficiencyChange(
                levelSelect.dataset.skillLevel,
                levelSelect.value
            );
        }
    });

    saveButton.addEventListener("click", saveSoftSkills);

    try {
        const user = await window.JOZSession.requireRole(["student"]);
        if (!user) return;

        updateUserDetails(user);

        document.getElementById("logoutButton")?.addEventListener(
            "click",
            () => window.JOZSession.logout()
        );

        await loadSoftSkills();
    } catch (error) {
        console.error("Soft Skills initialization failed:", error);

        isLoading = false;
        updateSelectionUI();

        showStatus(
            error.message || "Unable to initialize the Soft Skills page.",
            "error"
        );
    }
});
