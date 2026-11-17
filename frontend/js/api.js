"use strict";

window.JOZApi = (() => {
    const BASE_URL = "http://localhost:8000";

    function getErrorMessage(data, fallback = "Something went wrong. Please try again.") {
        const detail = data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        if (Array.isArray(detail)) {
            return detail
                .map((item) => item.msg)
                .filter(Boolean)
                .join(" ");
        }

        return fallback;
    }

    async function request(endpoint, options = {}) {
        const headers = new Headers(options.headers || {});
        const hasBody = options.body !== undefined && options.body !== null;
        const isFormData = hasBody && options.body instanceof FormData;

        if (hasBody && !isFormData && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const response = await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            headers,
            credentials: "include"
        });

        if (response.status === 204) {
            return null;
        }

        const contentType = response.headers.get("content-type") || "";
        let data = null;

        if (contentType.includes("application/json")) {
            data = await response.json().catch(() => null);
        } else {
            const responseText = await response.text().catch(() => "");
            data = responseText ? { detail: responseText } : null;
        }

        if (!response.ok) {
            throw new Error(getErrorMessage(data));
        }

        return data;
    }

    function get(endpoint, options = {}) {
        return request(endpoint, {
            ...options,
            method: "GET"
        });
    }

    function post(endpoint, body, options = {}) {
        return request(endpoint, {
            ...options,
            method: "POST",
            body: body instanceof FormData
                ? body
                : JSON.stringify(body ?? {})
        });
    }

    function put(endpoint, body, options = {}) {
        return request(endpoint, {
            ...options,
            method: "PUT",
            body: body instanceof FormData
                ? body
                : JSON.stringify(body ?? {})
        });
    }

    function patch(endpoint, body, options = {}) {
        return request(endpoint, {
            ...options,
            method: "PATCH",
            body: body instanceof FormData
                ? body
                : JSON.stringify(body ?? {})
        });
    }

    function deleteRequest(endpoint, options = {}) {
        return request(endpoint, {
            ...options,
            method: "DELETE"
        });
    }

    async function getCsrfToken() {
        const data = await get("/api/auth/csrf");

        if (!data?.csrf_token) {
            throw new Error("Unable to obtain a security token.");
        }

        return data.csrf_token;
    }

    async function withCsrf(callback, options = {}) {
        const csrfToken = await getCsrfToken();
        const headers = new Headers(options.headers || {});

        headers.set("X-CSRF-Token", csrfToken);

        return callback({
            ...options,
            headers
        });
    }

    function postWithCsrf(endpoint, body, options = {}) {
        return withCsrf(
            (secureOptions) => post(endpoint, body, secureOptions),
            options
        );
    }

    function putWithCsrf(endpoint, body, options = {}) {
        return withCsrf(
            (secureOptions) => put(endpoint, body, secureOptions),
            options
        );
    }

    function patchWithCsrf(endpoint, body, options = {}) {
        return withCsrf(
            (secureOptions) => patch(endpoint, body, secureOptions),
            options
        );
    }

    function deleteWithCsrf(endpoint, options = {}) {
        return withCsrf(
            (secureOptions) => deleteRequest(endpoint, secureOptions),
            options
        );
    }

    return {
        baseUrl: BASE_URL,
        request,
        get,
        post,
        put,
        patch,
        delete: deleteRequest,
        getCsrfToken,
        postWithCsrf,
        putWithCsrf,
        patchWithCsrf,
        deleteWithCsrf
    };
})();
