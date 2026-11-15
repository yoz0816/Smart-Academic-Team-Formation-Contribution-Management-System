"use strict";
document.addEventListener("DOMContentLoaded", async () => {
    const currentYear = document.getElementById("currentYear");

    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }

    try {
        const user = await window.JOZSession.getCurrentUser();

        if (user) {
            window.JOZSession.redirectByRole(user);
            return;
        }
    } catch (error) {
        console.error("Session check failed:", error);
    }

    document.querySelectorAll(".password-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const wrapper = button.closest(".input-wrapper");
            const passwordInput = wrapper?.querySelector("input");
            const icon = button.querySelector("i");

            if (!passwordInput || !icon) return;

            const showPassword = passwordInput.type === "password";

            passwordInput.type = showPassword ? "text" : "password";

            button.setAttribute("aria-pressed", String(showPassword));
            button.setAttribute(
                "aria-label",
                showPassword ? "Hide password" : "Show password"
            );

            icon.classList.toggle("fa-eye", !showPassword);
            icon.classList.toggle("fa-eye-slash", showPassword);
        });
    });

    function showMessage(element, message, type = "error") {
        if (!element) return;

        element.textContent = message;
        element.hidden = false;

        element.style.borderColor =
            type === "success"
                ? "rgba(53, 214, 189, 0.35)"
                : "rgba(255, 100, 120, 0.25)";

        element.style.color =
            type === "success" ? "#35d6bd" : "#ff9ba9";

        element.style.background =
            type === "success"
                ? "rgba(53, 214, 189, 0.08)"
                : "rgba(255, 100, 120, 0.08)";
    }

    function setSubmitState(button, loading, loadingText, originalText) {
        if (!button) return;

        button.disabled = loading;
        button.textContent = loading ? loadingText : originalText;
    }

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const fullName = document.getElementById("fullName").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const confirmPassword =
                document.getElementById("confirmPassword").value;

            const message = document.getElementById("registerMessage");
            const submitButton = registerForm.querySelector(
                'button[type="submit"]'
            );
            const originalButtonText = submitButton?.textContent || "Create account";

            if (password !== confirmPassword) {
                showMessage(message, "Your passwords do not match.");
                return;
            }

            if (password.length < 8) {
                showMessage(
                    message,
                    "Your password must contain at least 8 characters."
                );
                return;
            }

            if (fullName.length < 2) {
                showMessage(message, "Please enter your full name.");
                return;
            }

            setSubmitState(
                submitButton,
                true,
                "Creating account...",
                originalButtonText
            );

            try {
                const data = await window.JOZApi.post(
                    "/api/auth/register",
                    {
                        full_name: fullName,
                        email,
                        password
                    }
                );

                showMessage(
                    message,
                    `${data.message} You can now sign in to your account.`,
                    "success"
                );

                registerForm.reset();
            } catch (error) {
                showMessage(message, error.message);
            } finally {
                setSubmitState(
                    submitButton,
                    false,
                    "",
                    originalButtonText
                );
            }
        });
    }

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            const message = document.getElementById("loginMessage");
            const submitButton = loginForm.querySelector(
                'button[type="submit"]'
            );
            const originalButtonText = submitButton?.textContent || "Sign in";

            setSubmitState(
                submitButton,
                true,
                "Signing in...",
                originalButtonText
            );

            try {
                const data = await window.JOZApi.post(
                    "/api/auth/login",
                    { email, password }
                );

                showMessage(
                    message,
                    `Welcome back, ${data.user.full_name}. Redirecting...`,
                    "success"
                );

                window.JOZSession.redirectByRole(data.user);
            } catch (error) {
                showMessage(message, error.message);

                setSubmitState(
                    submitButton,
                    false,
                    "",
                    originalButtonText
                );
            }
        });
    }
});
