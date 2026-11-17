document.addEventListener("DOMContentLoaded", async () => {
    const interests = [
        { name: "Web Development", icon: "⌘" },
        { name: "Mobile Application Development", icon: "▣" },
        { name: "Desktop Application Development", icon: "▤" },
        { name: "Cybersecurity", icon: "⬡" },
        { name: "Data Science & Analytics", icon: "▥" },
        { name: "Database Systems", icon: "▦" },
        { name: "Cloud Computing & DevOps", icon: "☁" },
        { name: "Computer Networking", icon: "◎" },
        { name: "Internet of Things (IoT)", icon: "◉" },
        { name: "UI/UX Design", icon: "✎" },
        { name: "Software Testing & Quality Assurance", icon: "✓" },
        { name: "Game Development", icon: "◇" },
        { name: "Operating Systems", icon: "▧" },
        { name: "Software Engineering & Architecture", icon: "⌘" }
    ];

    const grid = document.getElementById("interestsGrid");
    const selectedCount = document.getElementById("selectedCount");
    const saveButton = document.getElementById("saveInterestsButton");
    const clearButton = document.getElementById("clearInterestsButton");
    const statusElement = document.getElementById("interestsStatus");

    let selectedInterests = new Set();
    let savedInterests = new Set();
    let isSaving = false;
    let isLoading = true;

    function showStatus(message, type = "") {
        statusElement.textContent = message;
        statusElement.className = `interests-status ${type}`.trim();
    }

    function updateUserDetails(user) {
        const name = user?.full_name || "Student";
        const nameElement = document.getElementById("userName");
        const avatarElement = document.getElementById("userAvatar");
        const yearElement = document.getElementById("currentYear");

        if (nameElement) nameElement.textContent = name;
        if (avatarElement) avatarElement.textContent = name.charAt(0).toUpperCase();
        if (yearElement) yearElement.textContent = new Date().getFullYear();
    }

    function updateSelectionUI() {
        selectedCount.textContent = selectedInterests.size;

        grid.querySelectorAll(".interest-card").forEach((card) => {
            const checkbox = card.querySelector("input");
            const selected = selectedInterests.has(checkbox.value);

            checkbox.checked = selected;
            card.classList.toggle("selected", selected);

            const checkmark = card.querySelector(".interest-card-check");
            checkmark.textContent = selected ? "✓" : "";
        });

        const hasChanges =
            selectedInterests.size !== savedInterests.size ||
            [...selectedInterests].some((interest) => !savedInterests.has(interest));

        saveButton.disabled = isLoading || isSaving || !hasChanges;
        clearButton.disabled = isLoading || isSaving;
    }

    function renderInterests() {
        grid.innerHTML = interests.map((interest, index) => `
            <label class="interest-card" for="interest-${index}">
                <input
                    type="checkbox"
                    id="interest-${index}"
                    value="${interest.name}"
                    aria-label="${interest.name}"
                >
                <span class="interest-card-icon" aria-hidden="true">${interest.icon}</span>
                <span class="interest-card-name">${interest.name}</span>
                <span class="interest-card-check" aria-hidden="true"></span>
            </label>
        `).join("");

        grid.querySelectorAll("input[type='checkbox']").forEach((checkbox) => {
            checkbox.addEventListener("change", () => {
                if (checkbox.checked) {
                    selectedInterests.add(checkbox.value);
                } else {
                    selectedInterests.delete(checkbox.value);
                }

                showStatus("");
                updateSelectionUI();
            });
        });

        updateSelectionUI();
    }

    async function loadInterests() {
        try {
            const response = await window.JOZApi.get("/api/student/interests");
            const existing = Array.isArray(response?.interests)
                ? response.interests
                : [];

            selectedInterests = new Set(existing);
            savedInterests = new Set(existing);

            renderInterests();
            showStatus(
                existing.length
                    ? "Your saved interests have been loaded."
                    : "Choose the interest areas that match you."
            );
        } catch (error) {
            grid.innerHTML = `
                <div class="interests-empty">
                    Unable to load your interests. Please refresh the page and try again.
                </div>
            `;
            showStatus(error.message || "Could not load your interests.", "error");
            saveButton.disabled = true;
            clearButton.disabled = true;
        } finally {
            isLoading = false;
            updateSelectionUI();
        }
    }

    async function saveInterests() {
        if (isSaving || isLoading) return;

        isSaving = true;
        saveButton.disabled = true;
        saveButton.querySelector("span:first-child").textContent = "Saving...";
        showStatus("Saving your interests...");

        try {
            const response = await window.JOZApi.putWithCsrf("/api/student/interests", {
                interests: [...selectedInterests]
            });

            const saved = Array.isArray(response?.interests)
                ? response.interests
                : [...selectedInterests];

            selectedInterests = new Set(saved);
            savedInterests = new Set(saved);

            showStatus("Your interests have been saved successfully.", "success");
        } catch (error) {
            showStatus(error.message || "Unable to save your interests.", "error");
        } finally {
            isSaving = false;
            saveButton.querySelector("span:first-child").textContent = "Save Interests";
            updateSelectionUI();
        }
    }

    clearButton.addEventListener("click", () => {
        selectedInterests.clear();
        showStatus("All selections cleared. Save your changes to confirm.");
        updateSelectionUI();
    });

    saveButton.addEventListener("click", saveInterests);

    try {
        const user = await window.JOZSession.requireRole(["student"]);
        if (!user) return;

        updateUserDetails(user);

        const logoutButton = document.getElementById("logoutButton");
        logoutButton?.addEventListener("click", () => {
            window.JOZSession.logout();
        });

        renderInterests();
        await loadInterests();
    } catch (error) {
        console.error("Student interests initialization failed:", error);
        showStatus("Unable to initialize the interests page.", "error");
    }
});
