/* ===================================
   JOLODHAR - Public Dashboard JS
   Map, Weather, Road Status, Suggestions
   =================================== */

(function () {
    "use strict";

    let map = null;
    let markers = [];
    let currentDistrict = null;
    const J = window.JOLODHAR;
    const L_ = window.JL;
    let lang = J.lang;

    // ===== INIT MAP =====
    function initMap() {
        const mapEl = document.getElementById("liveMap");
        if (!mapEl || typeof L === "undefined") return;

        const lat = J.defaultLat;
        const lon = J.defaultLon;

        map = L.map("liveMap", {
            center: [lat, lon],
            zoom: 11,
            zoomControl: true
        });

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap | JOLODHAR",
            maxZoom: 18
        }).addTo(map);

        loadSensorMarkers();
    }

    function clearMarkers() {
        markers.forEach(function (m) { map.removeLayer(m); });
        markers = [];
    }

    function loadSensorMarkers() {
        L_.api(J.endpoints.sensors).then(function (data) {
            clearMarkers();
            const sensors = data.sensors || [];

            sensors.forEach(function (s) {
                if (!s.lat || !s.lon) return;

                // Determine status from water level
                let status = "clear";
                const ratio = s.last_reading / (s.drain_depth || 150);
                if (s.status === "offline") status = "offline";
                else if (ratio >= 0.85 || s.last_reading >= 130) status = "blocked";
                else if (ratio >= 0.60 || s.last_reading >= 90) status = "caution";

                const icon = L.divIcon({
                    className: "map-marker marker-" + status,
                    iconSize: [24, 24],
                    html: ""
                });

                const marker = L.marker([s.lat, s.lon], { icon: icon }).addTo(map);
                const statusText = {
                    clear: lang === "bn" ? "নিরাপদ" : "Normal",
                    caution: lang === "bn" ? "সতর্কতা" : "Warning",
                    blocked: lang === "bn" ? "জলাবদ্ধ" : "Blocked",
                    offline: lang === "bn" ? "অফলাইন" : "Offline"
                }[status];

                const popupHtml = `
                    <div style="min-width:180px;">
                        <strong>${s.sensor_id}</strong><br>
                        <span>${s.location_name || ""}</span><br>
                        <span style="color:#0EA5E9;">${s.district}</span><br>
                        <hr style="margin:6px 0;border:none;border-top:1px solid #334155;">
                        <strong>Water: ${s.last_reading} cm</strong><br>
                        Status: <strong style="color:${
                            status === "blocked" ? "#EF4444" :
                            status === "caution" ? "#F59E0B" :
                            status === "offline" ? "#64748B" : "#10B981"
                        };">${statusText}</strong>
                    </div>
                `;
                marker.bindPopup(popupHtml);
                markers.push(marker);
            });

            document.getElementById("mapLastUpdate").textContent = new Date().toLocaleTimeString();
        }).catch(function (e) {
            console.error("Sensor load error:", e);
        });
    }

    // ===== WEATHER: TOMORROW RAIN FORECAST =====
    function loadRainForecast(lat, lon) {
        const url = J.endpoints.weatherTomorrow + "?lat=" + lat + "&lon=" + lon + "&lang=" + lang;

        // Show loading
        const answerEl = document.getElementById("rainAnswer");
        const probEl = document.getElementById("rainProb");
        const detailEl = document.getElementById("rainDetail");
        const iconEl = document.getElementById("rainIcon");
        const cardEl = document.getElementById("rainAlertCard");

        if (answerEl) answerEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>' + (lang === "bn" ? "লোড হচ্ছে..." : "Loading...") + "</span>";
        if (probEl) probEl.textContent = "—";

        L_.api(url).then(function (data) {
            if (!data || data.error) {
                if (answerEl) answerEl.innerHTML = "<span>" + (lang === "bn" ? "আবহাওয়া তথ্য পাওয়া যায়নি" : "Weather unavailable") + "</span>";
                return;
            }

            const willRain = data.will_rain;
            const prob = data.rain_probability || 0;
            const rainText = data.rain_text || (willRain ? "Rain expected" : "No rain");

            if (answerEl) answerEl.textContent = rainText;
            if (probEl) probEl.textContent = prob + "%";
            if (detailEl) {
                const detail = lang === "bn" ?
                    `${data.weather_text} • সর্বোচ্চ ${data.temp_max}° • সর্বনিম্ন ${data.temp_min}° • বৃষ্টিপাত ${data.precipitation_sum}mm` :
                    `${data.weather_text} • Max ${data.temp_max}° • Min ${data.temp_min}° • Precip ${data.precipitation_sum}mm`;
                detailEl.textContent = detail;
            }

            if (iconEl) {
                const iconClass = L_.weatherIcon(data.weather_code);
                iconEl.innerHTML = '<i class="fas ' + iconClass + '"></i>';
            }

            if (cardEl) {
                if (willRain) {
                    cardEl.style.borderColor = "var(--primary)";
                    cardEl.style.boxShadow = "var(--shadow-lg), 0 0 30px rgba(14, 165, 233, 0.4)";
                } else {
                    cardEl.style.borderColor = "var(--success)";
                    cardEl.style.boxShadow = "var(--shadow-lg), 0 0 20px rgba(16, 185, 129, 0.3)";
                }
            }

            // Update probability circle visualization
            const circle = document.querySelector(".rain-prob-circle");
            if (circle) {
                const deg = (prob / 100) * 360;
                circle.style.background = `conic-gradient(${willRain ? "var(--primary)" : "var(--success)"} ${deg}deg, var(--bg-card) ${deg}deg)`;
            }

            // Render hourly forecast
            renderHourly(data.hourly || []);
        }).catch(function (e) {
            console.error("Forecast error:", e);
            if (answerEl) answerEl.innerHTML = "<span>" + (lang === "bn" ? "আবহাওয়া তথ্য লোড করতে সমস্যা" : "Failed to load forecast") + "</span>";
        });
    }

    function renderHourly(hourly) {
        const section = document.getElementById("hourlySection");
        const scroll = document.getElementById("hourlyScroll");
        if (!section || !scroll || !hourly.length) return;

        section.style.display = "block";
        scroll.innerHTML = "";

        hourly.forEach(function (h) {
            if (!h.hour) return;
            const isRain = (h.precipitation_probability || 0) >= 40;
            const iconClass = isRain ? "fa-cloud-rain rainy" :
                (h.cloud_cover || 0) > 70 ? "fa-cloud cloudy" :
                (h.cloud_cover || 0) > 30 ? "fa-cloud-sun cloudy" : "fa-sun clear";

            const card = document.createElement("div");
            card.className = "hourly-card";
            card.innerHTML = `
                <div class="hourly-time">${h.hour.substring(0, 5)}</div>
                <div class="hourly-icon ${iconClass.split(" ")[1]}"><i class="fas ${iconClass.split(" ")[0]}"></i></div>
                <div class="hourly-temp">${h.temperature || "—"}°</div>
                <div class="hourly-precip">${h.precipitation_probability || 0}%</div>
            `;
            scroll.appendChild(card);
        });
    }

    // ===== WEATHER: CURRENT =====
    function loadCurrentWeather(lat, lon) {
        const url = J.endpoints.weatherCurrent + "?lat=" + lat + "&lon=" + lon + "&lang=" + lang;
        L_.api(url).then(function (data) {
            if (!data || data.error) return;

            setText("weatherTemp", data.temperature !== null && data.temperature !== undefined ? Math.round(data.temperature) : "—");
            setText("weatherHumidity", (data.humidity !== null && data.humidity !== undefined ? data.humidity + "%" : "—"));
            setText("weatherPrecip", (data.precipitation !== null && data.precipitation !== undefined ? data.precipitation + " mm" : "0 mm"));
            setText("weatherWind", (data.wind_speed !== null && data.wind_speed !== undefined ? data.wind_speed + " m/s" : "—"));
            setText("weatherCloud", (data.cloud_cover !== null && data.cloud_cover !== undefined ? data.cloud_cover + "%" : "—"));
            setText("weatherText", data.weather_text || "—");

            const iconEl = document.getElementById("weatherIcon");
            if (iconEl) {
                const iconClass = L_.weatherIcon(data.weather_code);
                iconEl.innerHTML = '<i class="fas ' + iconClass + '"></i>';
            }
        }).catch(function (e) {
            console.error("Weather error:", e);
        });
    }

    // ===== NOTIFICATIONS =====
    function loadNotifications() {
        L_.api(J.endpoints.notifications + "?limit=10").then(function (data) {
            const list = document.getElementById("notifList");
            const count = document.getElementById("notifCount");
            if (!list) return;

            const notifs = data.notifications || [];
            if (count) count.textContent = notifs.length;

            if (!notifs.length) {
                list.innerHTML = '<div class="notif-empty">' + (lang === "bn" ? "কোনো সক্রিয় নোটিফিকেশন নেই" : "No active notifications") + "</div>";
                return;
            }

            list.innerHTML = "";
            notifs.forEach(function (n) {
                const item = document.createElement("div");
                item.className = "notif-item";
                item.innerHTML = `
                    <div class="notif-icon-box severity-${n.severity}">
                        <i class="fas ${L_.notifIcon(n.type)}"></i>
                    </div>
                    <div class="notif-item-content">
                        <div class="notif-item-title">${n.title}</div>
                        <div class="notif-item-msg">${n.message}</div>
                        <div class="notif-item-meta">
                            <i class="fas fa-map-marker-alt"></i> ${n.district || ""} • ${L_.formatTime(n.timestamp)}
                        </div>
                    </div>
                `;
                list.appendChild(item);
            });
        }).catch(function (e) {
            console.error("Notifications error:", e);
        });
    }

    // ===== ROAD STATUS =====
    function loadRoads(district) {
        const url = J.endpoints.roads + (district ? "?district=" + encodeURIComponent(district) : "");
        L_.api(url).then(function (data) {
            const roads = data.roads || [];
            const summary = data.summary || {};

            // Update summary cards
            setText("roadsClear", summary.clear || 0);
            setText("roadsCaution", summary.caution || 0);
            setText("roadsBlocked", summary.blocked || 0);

            const list = document.getElementById("roadList");
            if (!list) return;

            if (!roads.length) {
                list.innerHTML = '<div class="road-list-loading">' + (lang === "bn" ? "এই জেলার জন্য কোনো রাস্তার তথ্য নেই" : "No road data for this district") + "</div>";
                return;
            }

            list.innerHTML = "";
            roads.forEach(function (r) {
                const item = document.createElement("div");
                item.className = "road-item status-" + r.status;

                const statusText = lang === "bn" ? r.status_bn : r.status.charAt(0).toUpperCase() + r.status.slice(1);
                const actionText = {
                    use_route: lang === "bn" ? "✓ ব্যবহার করুন" : "✓ Use this route",
                    caution_route: lang === "bn" ? "⚠ ধীরে চালান" : "⚠ Drive slowly",
                    avoid_route: lang === "bn" ? "✗ এড়িয়ে চলুন" : "✗ Avoid this route"
                }[r.action_key] || "";

                const iconClass = {
                    clear: "fa-check-circle",
                    caution: "fa-exclamation-triangle",
                    blocked: "fa-times-circle",
                    unknown: "fa-question-circle"
                }[r.status] || "fa-road";

                item.innerHTML = `
                    <div class="road-item-icon"><i class="fas ${iconClass}"></i></div>
                    <div class="road-item-info">
                        <div class="road-item-name">${r.road_name}</div>
                        <div class="road-item-meta">${lang === "bn" ? "জেলা" : "District"}: ${r.district} • ${lang === "bn" ? "জল স্তর" : "Water"}: ${r.water_level} cm • ${L_.formatTime(r.last_updated)}</div>
                    </div>
                    <div class="road-item-status">${statusText}</div>
                    <div class="road-item-action">${actionText}</div>
                `;
                list.appendChild(item);
            });
        }).catch(function (e) {
            console.error("Roads error:", e);
        });
    }

    // ===== SUGGESTIONS =====
    function loadSuggestions(district) {
        const url = J.endpoints.suggestions + "?district=" + encodeURIComponent(district || J.defaultDistrict) + "&lang=" + lang;
        L_.api(url).then(function (data) {
            const list = document.getElementById("suggestionsList");
            if (!list) return;

            const suggestions = data.suggestions || [];
            if (!suggestions.length) {
                list.innerHTML = '<div class="sugg-loading">' + (lang === "bn" ? "কোনো পরামর্শ নেই" : "No suggestions") + "</div>";
                return;
            }

            list.innerHTML = "";
            suggestions.forEach(function (s) {
                const item = document.createElement("div");
                item.className = "sugg-item sugg-" + s.color;
                const text = lang === "bn" ? s.text_bn : s.text_en;
                item.innerHTML = `
                    <div class="sugg-icon"><i class="fas fa-${s.icon}"></i></div>
                    <div class="sugg-text">${text}</div>
                `;
                list.appendChild(item);
            });
        }).catch(function (e) {
            console.error("Suggestions error:", e);
        });
    }

    // ===== DASHBOARD STATS =====
    function loadQuickStats() {
        L_.api(J.endpoints.dashboardStats).then(function (data) {
            setText("statSensors", data.sensors_online + "/" + data.sensors_total);
            setText("statAlerts", data.active_alerts);
        }).catch(function () {});
    }

    // ===== DISTRICT CHANGE =====
    function onDistrictChange() {
        const select = document.getElementById("districtSelect");
        if (!select) return;

        const selected = select.options[select.selectedIndex];
        const lat = parseFloat(selected.getAttribute("data-lat") || J.defaultLat);
        const lon = parseFloat(selected.getAttribute("data-lon") || J.defaultLon);
        const districtName = select.value;

        currentDistrict = districtName;

        // Update map center
        if (map) {
            map.setView([lat, lon], 11);
        }

        // Reload all data for new district
        loadRainForecast(lat, lon);
        loadCurrentWeather(lat, lon);
        loadRoads(districtName);
        loadSuggestions(districtName);
        loadSensorMarkers();
    }

    // ===== LIVE UPDATE HANDLER =====
    window.onLiveSensorUpdate = function (data) {
        if (!data || !data.sensors) return;

        // Update markers positions/status in real-time
        data.sensors.forEach(function (s) {
            // Find existing marker and update popup
            // (markers re-created on next full reload)
        });

        // Update map timestamp
        const updateEl = document.getElementById("mapLastUpdate");
        if (updateEl) updateEl.textContent = new Date().toLocaleTimeString();
    };

    // ===== HELPERS =====
    function setText(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    // ===== INIT =====
    document.addEventListener("DOMContentLoaded", function () {
        lang = J.lang;
        const select = document.getElementById("districtSelect");
        if (select) {
            select.addEventListener("change", onDistrictChange);
            // Set initial district
            currentDistrict = select.value || J.defaultDistrict;
        }

        // Initialize
        initMap();
        loadQuickStats();
        loadNotifications();

        // Initial load for default district
        const lat = J.defaultLat;
        const lon = J.defaultLon;
        loadRainForecast(lat, lon);
        loadCurrentWeather(lat, lon);
        loadRoads(currentDistrict || J.defaultDistrict);
        loadSuggestions(currentDistrict || J.defaultDistrict);

        // Auto refresh every 60 seconds
        setInterval(function () {
            loadNotifications();
            loadQuickStats();
            if (currentDistrict) {
                const sel = document.getElementById("districtSelect");
                if (sel) {
                    const opt = sel.options[sel.selectedIndex];
                    if (opt) {
                        loadRoads(currentDistrict);
                        loadSuggestions(currentDistrict);
                    }
                }
            }
        }, 60000);

        // Auto refresh map markers every 30s
        setInterval(loadSensorMarkers, 30000);
    });

})();
