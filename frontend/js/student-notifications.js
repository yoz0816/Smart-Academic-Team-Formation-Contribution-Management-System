"use strict";

document.addEventListener("DOMContentLoaded", initializeStudentNotifications);

async function initializeStudentNotifications() {
    const user = await window.JOZSession.requireRole(["student"]);
    if (!user) return;

    const API = window.JOZApi;
    const listElement = document.getElementById("notificationsList");
    const loadingElement = document.getElementById("notificationsLoading");
    const emptyElement = document.getElementById("notificationsEmpty");
    const messageElement = document.getElementById("notificationMessage");
    const refreshButton = document.getElementById("refreshNotificationsButton");
    const markAllButton = document.getElementById("markAllReadButton");

    const unreadCountElement = document.getElementById("unreadCount");
    const unreadTabCountElement = document.getElementById("unreadTabCount");
    const allCountElement = document.getElementById("allCount");
    const sidebarCountElement = document.getElementById("sidebarUnreadCount");
    const topbarIndicator = document.getElementById("topbarNotificationIndicator");

    let notifications = [];
    let activeFilter = "all";
    let unreadCount = 0;
    let isLoading = false;

    const notificationEndpoint = "/api/student/notifications";

    document.getElementById("userName").textContent =
        user.full_name || "Student";

    document.getElementById("userAvatar").textContent =
        (user.full_name || "S").trim().charAt(0).toUpperCase();

    document.getElementById("currentYear").textContent =
        new Date().getFullYear();

    document.getElementById("logoutButton").addEventListener("click", async () => {
        try {
            await window.JOZSession.logout();
        } catch (error) {
            showMessage(error.message || "Unable to sign out.", true);
        }
    });

    refreshButton.addEventListener("click", loadNotifications);
    markAllButton.addEventListener("click", markAllAsRead);

    document.querySelectorAll(".notification-tab").forEach((tab) => {
        tab.addEventListener("click", () => {
            setActiveFilter(tab.dataset.filter);
        });
    });

    listElement.addEventListener("click", handleNotificationAction);

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    }

    function showMessage(message, isError = false) {
        messageElement.textContent = message;
        messageElement.classList.toggle("error", isError);
        messageElement.hidden = false;
    }

    function clearMessage() {
        messageElement.textContent = "";
        messageElement.classList.remove("error");
        messageElement.hidden = true;
    }

    function formatDate(value) {
        if (!value) return "Date unavailable";

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "Date unavailable";

        return new Intl.DateTimeFormat(undefined, {
            day: "numeric",
            month: "short",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit"
        }).format(date);
    }

    function formatRelativeTime(value) {
        if (!value) return "Recently";

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return formatDate(value);

        const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

        if (seconds < 60) return "Just now";
        if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} hr ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;

        return formatDate(value);
    }

    function getNotificationIcon(category) {
        const icons = {
            team: "fa-people-group",
            task: "fa-list-check",
            submission: "fa-file-arrow-up",
            evaluation: "fa-chart-line",
            assignment: "fa-folder-open",
            announcement: "fa-bullhorn",
            system: "fa-circle-info"
        };

        return icons[category] || "fa-bell";
    }

    function getSafeActionUrl(actionUrl) {
        if (!actionUrl) return null;

        try {
            const target = new URL(actionUrl, window.location.origin);

            if (target.origin !== window.location.origin) {
                return null;
            }

            return target.href;
        } catch {
            return null;
        }
    }

    function updateCounts(total = notifications.length) {
        unreadCountElement.textContent = unreadCount;
        unreadTabCountElement.textContent = unreadCount;
        allCountElement.textContent = total;

        sidebarCountElement.textContent = unreadCount;
        sidebarCountElement.hidden = unreadCount === 0;

        topbarIndicator.hidden = unreadCount === 0;
        markAllButton.disabled = unreadCount === 0;
    }

    function setActiveFilter(filter) {
        activeFilter = filter === "unread" ? "unread" : "all";

        document.querySelectorAll(".notification-tab").forEach((tab) => {
            const isActive = tab.dataset.filter === activeFilter;

            tab.classList.toggle("active", isActive);
            tab.setAttribute("aria-selected", String(isActive));
        });

        renderNotifications();
    }

    function renderNotifications() {
        const visibleNotifications = activeFilter === "unread"
            ? notifications.filter((item) => !item.is_read)
            : notifications;

        listElement.innerHTML = "";

        if (visibleNotifications.length === 0) {
            listElement.hidden = true;
            emptyElement.hidden = false;

            const emptyTitle = document.getElementById("notificationsEmptyTitle");
            const emptyDescription = document.getElementById("notificationsEmptyDescription");

            if (activeFilter === "unread") {
                emptyTitle.textContent = "You're all caught up";
                emptyDescription.textContent =
                    "You don't have any unread notifications right now.";
            } else {
                emptyTitle.textContent = "No notifications yet";
                emptyDescription.textContent =
                    "Updates about your academic activities will appear here.";
            }

            return;
        }

        emptyElement.hidden = true;
        listElement.hidden = false;

        listElement.innerHTML = visibleNotifications.map((item) => {
            const category = String(item.category || "system").toLowerCase();
            const title = escapeHTML(item.title || "Notification");
            const message = escapeHTML(item.message || "");
            const isUnread = !item.is_read;
            const actionUrl = getSafeActionUrl(item.action_url);
            const timestamp = escapeHTML(formatRelativeTime(item.created_at));
            const categoryLabel = escapeHTML(category.replaceAll("_", " "));

            return `
                <article
                    class="notification-item ${isUnread ? "unread" : ""}"
                    data-notification-id="${Number(item.id)}"
                >
                    <div class="notification-type-icon ${escapeHTML(category)}">
                        <i class="fa-solid ${getNotificationIcon(category)}"></i>
                    </div>

                    <div class="notification-item-content">
                        <div class="notification-item-heading">
                            ${isUnread ? '<span class="notification-unread-dot" aria-label="Unread"></span>' : ""}
                            <h3>${title}</h3>
                        </div>

                        <p>${message}</p>

                        <div class="notification-item-meta">
                            <span class="notification-category">${categoryLabel}</span>
                            <span class="notification-time" title="${escapeHTML(formatDate(item.created_at))}">
                                <i class="fa-regular fa-clock"></i>
                                ${timestamp}
                            </span>
                        </div>
                    </div>

                    <div class="notification-item-actions">
                        ${actionUrl
                            ? `
                                <button
                                    type="button"
                                    class="notification-action open-notification"
                                    data-id="${Number(item.id)}"
                                >
                                    <span>View</span>
                                    <i class="fa-solid fa-arrow-right"></i>
                                </button>
                            `
                            : ""}
                        ${isUnread
                            ? `
                                <button
                                    type="button"
                                    class="notification-action mark-read"
                                    data-id="${Number(item.id)}"
                                    aria-label="Mark notification as read"
                                >
                                    <i class="fa-solid fa-check"></i>
                                    <span>Mark read</span>
                                </button>
                            `
                            : ""}
                    </div>
                </article>
            `;
        }).join("");
    }

    async function patchWithCsrf(endpoint) {
        const csrfToken = await API.getCsrfToken();

        return API.patch(endpoint, null, {
            headers: {
                "X-CSRF-Token": csrfToken
            }
        });
    }

    async function loadNotifications() {
        if (isLoading) return;

        isLoading = true;
        clearMessage();

        loadingElement.hidden = false;
        listElement.hidden = true;
        emptyElement.hidden = true;
        refreshButton.disabled = true;

        try {
            const [listData, countData] = await Promise.all([
                API.get(`${notificationEndpoint}?limit=100&offset=0`),
                API.get(`${notificationEndpoint}/unread-count`)
            ]);

            notifications = Array.isArray(listData?.notifications)
                ? listData.notifications
                : [];

            unreadCount = Number(
                countData?.unread_count ?? listData?.unread_count ?? 0
            );

            updateCounts(Number(listData?.total ?? notifications.length));
            renderNotifications();
        } catch (error) {
            showMessage(
                error.message || "Unable to load notifications. Please try again.",
                true
            );

            notifications = [];
            unreadCount = 0;
            updateCounts(0);
            renderNotifications();
        } finally {
            loadingElement.hidden = true;
            refreshButton.disabled = false;
            isLoading = false;
        }
    }

    async function markNotificationAsRead(notificationId) {
        const notification = notifications.find(
            (item) => Number(item.id) === Number(notificationId)
        );

        if (!notification || notification.is_read) return;

        try {
            await patchWithCsrf(
                `${notificationEndpoint}/${Number(notificationId)}/read`
            );

            notification.is_read = true;
            notification.read_at = new Date().toISOString();

            unreadCount = Math.max(0, unreadCount - 1);
            updateCounts();
            renderNotifications();
        } catch (error) {
            showMessage(
                error.message || "Unable to mark this notification as read.",
                true
            );
        }
    }

    async function markAllAsRead() {
        if (unreadCount === 0) return;

        markAllButton.disabled = true;
        clearMessage();

        try {
            await patchWithCsrf(`${notificationEndpoint}/read-all`);

            notifications.forEach((item) => {
                item.is_read = true;
                item.read_at = item.read_at || new Date().toISOString();
            });

            unreadCount = 0;
            updateCounts();
            renderNotifications();

            showMessage("All notifications have been marked as read.");
        } catch (error) {
            showMessage(
                error.message || "Unable to mark all notifications as read.",
                true
            );
        } finally {
            markAllButton.disabled = unreadCount === 0;
        }
    }

    async function handleNotificationAction(event) {
        const actionButton = event.target.closest("button[data-id]");
        if (!actionButton) return;

        const notificationId = Number(actionButton.dataset.id);
        if (!Number.isInteger(notificationId) || notificationId <= 0) return;

        if (actionButton.classList.contains("mark-read")) {
            actionButton.disabled = true;
            await markNotificationAsRead(notificationId);
            return;
        }

        if (actionButton.classList.contains("open-notification")) {
            const notification = notifications.find(
                (item) => Number(item.id) === notificationId
            );

            if (!notification) return;

            const targetUrl = getSafeActionUrl(notification.action_url);
            if (!targetUrl) return;

            actionButton.disabled = true;

            if (!notification.is_read) {
                await markNotificationAsRead(notificationId);
            }

            window.location.assign(targetUrl);
        }
    }

    await loadNotifications();
}
