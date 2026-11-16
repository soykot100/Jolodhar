/* ===================================
   JOLODHAR - Common App JS
   WebSocket, utilities, helpers
   =================================== */

(function () {
    "use strict";

    // ===== Utilities =====
    window.JL = {
        formatDate: function (iso, lang) {
            if (!iso) return "—";
            lang = lang || (window.JOLODHAR && window.JOLODHAR.lang) || "bn";
            try {
                const d = new Date(iso);
                const opts = { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" };
                return d.toLocaleString(lang === "bn" ? "bn-BD" : "en-US", opts);
            } catch (e) {
                return iso;
            }
        },

        formatTime: function (iso) {
            if (!iso) return "—";
            try {
                const d = new Date(iso);
                return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
            } catch (e) {
                return iso;
            }
        },

        formatNumber: function (n, decimals) {
            decimals = decimals || 0;
            if (n === null || n === undefined || isNaN(n)) return "—";
            return Number(n).toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
        },

        api: function (url, options) {
            options = options || {};
            return fetch(url, options).then(function (r) {
                if (!r.ok) throw new Error("HTTP " + r.status);
                return r.json();
            });
        },

        createElement: function (tag, className, html) {
            const el = document.createElement(tag);
            if (className) el.className = className;
            if (html !== undefined) el.innerHTML = html;
            return el;
        },

        // Weather code -> icon
        weatherIcon: function (code) {
            if (code === 0) return "fa-sun";
            if (code >= 1 && code <= 3) return "fa-cloud";
            if (code >= 45 && code <= 48) return "fa-smog";
            if (code >= 51 && code <= 57) return "fa-cloud-rain";
            if (code >= 61 && code <= 67) return "fa-cloud-showers-heavy";
            if (code >= 71 && code <= 77) return "fa-snowflake";
            if (code >= 80 && code <= 82) return "fa-cloud-rain";
            if (code >= 85 && code <= 86) return "fa-snowflake";
            if (code >= 95) return "fa-bolt";
            return "fa-cloud";
        },

        // Severity color helper
        severityColor: function (sev) {
            const colors = {
                critical: "red",
                warning: "yellow",
                info: "blue"
            };
            return colors[sev] || "blue";
        },

        // Notification icon helper
        notifIcon: function (type) {
            const icons = {
                blockage: "fa-ban",
                flood: "fa-house-flood",
                rain: "fa-cloud-rain",
                sensor_offline: "fa-wifi-slash",
                maintenance: "fa-tools",
                resolved: "fa-check-circle"
            };
            return icons[type] || "fa-bell";
        }
    };

    // ===== WebSocket =====
    let socket = null;
    function initSocket() {
        try {
            socket = io();
            socket.on("connect", function () {
                console.log("JOLODHAR WebSocket connected");
            });
            socket.on("live_sensor_update", function (data) {
                if (window.onLiveSensorUpdate) {
                    window.onLiveSensorUpdate(data);
                }
            });
            socket.on("weather_update", function (data) {
                if (window.onWeatherUpdate) {
                    window.onWeatherUpdate(data);
                }
            });
            socket.on("disconnect", function () {
                console.log("JOLODHAR WebSocket disconnected");
            });
        } catch (e) {
            console.warn("WebSocket init failed:", e);
        }
    }

    window.JLSocket = {
        start: function () { initSocket(); },
        emit: function (event, data) {
            if (socket) socket.emit(event, data);
        },
        on: function (event, cb) {
            if (socket) socket.on(event, cb);
        }
    };

    document.addEventListener("DOMContentLoaded", function () {
        initSocket();
    });

})();
