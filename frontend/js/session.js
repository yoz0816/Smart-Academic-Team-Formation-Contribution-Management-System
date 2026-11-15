"use strict";

window.JOZSession = (() => {
    const ROLE_DASHBOARDS = {
        student: "../student/dashboard.html",
        lecturer: "../lecturer/dashboard.html",
        admin: "../admin/dashboard.html"
    };

    async function getCurrentUser() {
        return window.JOZApi.get("/api/auth/me");
    }

    function redirectByRole(user) {
        const destination = ROLE_DASHBOARDS[user?.role];

        if (!destination) {
            throw new Error("Your account has an unsupported role.");
        }

        window.location.replace(destination);
    }

    async function requireRole(allowedRoles) {
        let user;

        try {
            user = await getCurrentUser();
        } catch (error) {
            console.error("Session verification failed:", error);
            window.location.replace("../auth/login.html");
            return null;
        }

        if (!user) {
            window.location.replace("../auth/login.html");
            return null;
        }

        if (!allowedRoles.includes(user.role)) {
            redirectByRole(user);
            return null;
        }

        return user;
    }

    async function logout() {
        await window.JOZApi.postWithCsrf("/api/auth/logout");

        window.location.replace("../auth/login.html");
    }

    return {
        getCurrentUser,
        redirectByRole,
        requireRole,
        logout
    };
})();
