"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("dashboardSidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (!sidebar || !toggle) return;

    const overlay = document.createElement("div");
    overlay.className = "sidebar-overlay";
    overlay.setAttribute("aria-hidden", "true");
    document.body.appendChild(overlay);

    function openSidebar() {
        sidebar.classList.add("is-open");
        overlay.classList.add("is-visible");
        toggle.setAttribute("aria-expanded", "true");
        document.body.classList.add("sidebar-open");
    }

    function closeSidebar() {
        sidebar.classList.remove("is-open");
        overlay.classList.remove("is-visible");
        toggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("sidebar-open");
    }

    toggle.addEventListener("click", () => {
        sidebar.classList.contains("is-open")
            ? closeSidebar()
            : openSidebar();
    });

    overlay.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeSidebar();
    });

    sidebar.querySelectorAll(".sidebar-link[href]").forEach((link) => {
        link.addEventListener("click", closeSidebar);
    });

    const currentPage = window.location.pathname.split("/").pop();

    sidebar.querySelectorAll(".sidebar-link[href]").forEach((link) => {
        const linkPage = link.getAttribute("href");

        if (linkPage === currentPage) {
            sidebar.querySelectorAll(".sidebar-link").forEach((item) => {
                item.classList.remove("active");
            });

            link.classList.add("active");
        }
    });
});
