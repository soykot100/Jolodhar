/* ===================================
   JOLODHAR - Control Panel JS
   Dashboard, ML Metrics, Reports, etc.
   =================================== */

(function () {
    "use strict";

    const J = window.JOLODHAR;
    const L_ = window.JL;
    let lang = J.lang;
    let dashboardChart = null;
    let twinChart = null;
    let featureImportanceChart = null;

    // ===== DASHBOARD =====
    window.loadDashboardChart = function () {
        const canvas = document.getElementById("dashboardChart");
        if (!canvas || typeof Chart === "undefined") return;

        // Generate hourly data (last 24h) - demo data
        const labels = [];
        const data = [];
        const now = new Date();
        for (let i = 23; i >= 0; i--) {
            const d = new Date(now - i * 3600000);
            labels.push(d.getHours() + ":00");
            data.push(Math.floor(Math.random() * 60) + 20);
        }

        if (dashboardChart) dashboardChart.destroy();
        const ctx = canvas.getContext("2d");
        dashboardChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Sensor Activity",
                    data: data,
                    borderColor: "#0EA5E9",
                    backgroundColor: "rgba(14, 165, 233, 0.15)",
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: "#0EA5E9",
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: "#CBD5E1" } }
                },
                scales: {
                    x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } }
                }
            }
        });

        // Load district activity
        L_.api(J.endpoints.sensors).then(function (data) {
            const districtCounts = {};
            (data.sensors || []).forEach(function (s) {
                districtCounts[s.district] = (districtCounts[s.district] || 0) + 1;
            });
            const list = document.getElementById("districtActivity");
            if (list) {
                list.innerHTML = "";
                const sorted = Object.entries(districtCounts).sort(function (a, b) { return b[1] - a[1]; }).slice(0, 8);
                sorted.forEach(function (entry) {
                    const row = document.createElement("div");
                    row.className = "da-row";
                    row.innerHTML = '<span class="da-name">' + entry[0] + '</span><span class="da-count">' + entry[1] + ' sensors</span>';
                    list.appendChild(row);
                });
            }
        }).catch(function () {});

        // Load recent incidents
        L_.api(J.endpoints.incidents).then(function (data) {
            const list = document.getElementById("recentIncidents");
            if (!list) return;
            const incidents = (data.incidents || []).slice(0, 8);
            if (!incidents.length) {
                list.innerHTML = '<div class="loading-spinner">No recent incidents</div>';
                return;
            }
            list.innerHTML = "";
            incidents.forEach(function (i) {
                const row = document.createElement("div");
                row.className = "incident-row severity-" + i.severity + (i.status === "resolved" ? " resolved" : "");
                row.innerHTML = `
                    <div>
                        <strong>${i.incident_type}</strong>
                        <div style="font-size:11px;color:#94A3B8;margin-top:2px;">${i.district} • ${i.sensor_id || "—"}</div>
                    </div>
                    <div style="text-align:right;font-size:12px;">
                        <span style="color:#0EA5E9;text-transform:uppercase;font-weight:600;">${i.status}</span><br>
                        <span style="color:#64748B;font-size:10px;">${L_.formatTime(i.reported_at)}</span>
                    </div>
                `;
                list.appendChild(row);
            });
        }).catch(function () {});
    };

    // ===== ML METRICS: Feature Importance Chart =====
    window.loadFeatureImportanceChart = function () {
        const canvas = document.getElementById("featureImportanceChart");
        if (!canvas || typeof Chart === "undefined") return;

        const fi = canvas.getAttribute("data-fi");
        let fiData = [];
        try {
            fiData = JSON.parse(fi);
        } catch (e) {}

        // Try fetching from API
        if (!fiData.length) {
            L_.api(J.endpoints.mlFeatureImportance).then(function (data) {
                renderFIChart(canvas, data.feature_importance || []);
            }).catch(function () {});
        } else {
            renderFIChart(canvas, fiData);
        }
    };

    function renderFIChart(canvas, fiList) {
        if (!fiList.length) return;
        if (featureImportanceChart) featureImportanceChart.destroy();
        const ctx = canvas.getContext("2d");
        featureImportanceChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: fiList.map(function (f) { return f.feature.replace(/_/g, " "); }),
                datasets: [{
                    label: "Importance",
                    data: fiList.map(function (f) { return f.importance; }),
                    backgroundColor: "rgba(14, 165, 233, 0.7)",
                    borderColor: "#0EA5E9",
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                plugins: {
                    legend: { labels: { color: "#CBD5E1" } }
                },
                scales: {
                    x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } }
                }
            }
        });
    }

    // ===== ML METRICS: Live Prediction =====
    window.runPrediction = function () {
        const featureCols = [
            "rainfall", "temperature", "humidity", "wind_speed",
            "water_level", "flow_rate", "drain_depth", "drain_width",
            "population_density", "last_maintenance_days", "debris_indicator"
        ];
        const payload = {};
        featureCols.forEach(function (c) {
            const el = document.getElementById("pred_" + c);
            payload[c] = el ? parseFloat(el.value || 0) : 0;
        });

        const resultEl = document.getElementById("predictionResult");
        if (resultEl) {
            resultEl.style.display = "block";
            resultEl.innerHTML = '<div><i class="fas fa-spinner fa-spin"></i> Predicting...</div>';
        }

        fetch(J.endpoints.mlPredict, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        }).then(function (r) { return r.json(); }).then(function (data) {
            if (data.error) {
                resultEl.innerHTML = '<div style="color:#EF4444;"><i class="fas fa-exclamation-circle"></i> ' + data.error + "</div>";
                return;
            }

            const classBn = data.predicted_class_bn || data.predicted_class;
            const classEn = data.predicted_class;
            const probs = data.probabilities || {};
            const probsBn = data.probabilities_bn || {};
            const risk = data.risk_levels || {};

            const colorMap = { Normal: "#10B981", Warning: "#F59E0B", Critical: "#EF4444" };
            const color = colorMap[classEn] || "#0EA5E9";

            let probHtml = "";
            Object.keys(probs).forEach(function (k) {
                const p = probs[k];
                const pbn = probsBn[k] || k;
                probHtml += '<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px;">' +
                    '<span>' + (lang === "bn" ? pbn : k) + '</span>' +
                    '<span style="color:' + colorMap[k] + ';font-weight:700;">' + (p * 100).toFixed(1) + '%</span>' +
                    '</div>';
            });

            resultEl.innerHTML = `
                <div style="margin-bottom:12px;">
                    <strong>${lang === "bn" ? "প্রেডিকশন ফলাফল" : "Prediction Result"}:</strong>
                    <span style="color:${color};font-size:18px;font-weight:800;margin-left:8px;">${lang === "bn" ? classBn : classEn}</span>
                </div>
                <div style="margin-bottom:12px;">
                    <strong>${lang === "bn" ? "সম্ভাবনা" : "Probabilities"}:</strong>
                    ${probHtml}
                </div>
                <div style="font-size:12px;color:#94A3B8;margin-top:8px;">
                    Blockage Risk: ${(risk.blockage_risk * 100).toFixed(1)}% • Flood Risk: ${(risk.flood_risk * 100).toFixed(1)}%
                </div>
            `;
        }).catch(function (e) {
            resultEl.innerHTML = '<div style="color:#EF4444;">Error: ' + e.message + "</div>";
        });
    };

    // ===== SENSORS =====
    window.filterSensors = function () {
        const search = (document.getElementById("sensorSearch") || {}).value || "";
        const districtFilter = (document.getElementById("sensorDistrictFilter") || {}).value || "";

        const rows = document.querySelectorAll(".sensor-row");
        rows.forEach(function (row) {
            const id = (row.getAttribute("data-id") || "").toLowerCase();
            const district = row.getAttribute("data-district") || "";
            const text = row.textContent.toLowerCase();

            const matchesSearch = !search || id.indexOf(search.toLowerCase()) >= 0 || text.indexOf(search.toLowerCase()) >= 0;
            const matchesDistrict = !districtFilter || district === districtFilter;

            row.style.display = (matchesSearch && matchesDistrict) ? "" : "none";
        });
    };

    // ===== REPORTS =====
    window.generateReport = function (type) {
        if (type === "custom") {
            document.getElementById("customRangePanel").style.display = "block";
            return;
        }
        const panel = document.getElementById("reportOutputPanel");
        const output = document.getElementById("reportOutput");
        panel.style.display = "block";
        output.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Generating ' + type + ' report...</div>';

        L_.api(J.endpoints.incidents).then(function (data) {
            const incidents = data.incidents || [];
            const resolved = incidents.filter(function (i) { return i.status === "resolved"; }).length;

            document.getElementById("reportIncidents").textContent = incidents.length;
            document.getElementById("reportResolved").textContent = resolved;

            let html = '<h3 style="color:#0EA5E9;margin-bottom:12px;text-transform:capitalize;">' + type + ' Report</h3>';
            html += '<div style="margin-bottom:12px;font-size:12px;color:#94A3B8;">Generated: ' + new Date().toLocaleString() + "</div>";
            html += '<table class="data-table"><thead><tr><th>Type</th><th>District</th><th>Severity</th><th>Status</th><th>Time</th></tr></thead><tbody>';
            incidents.slice(0, 20).forEach(function (i) {
                html += "<tr><td>" + i.incident_type + "</td><td>" + i.district + "</td><td><span class='badge badge-" +
                    (i.severity === "critical" ? "red" : i.severity === "high" ? "orange" : "blue") + "'>" + i.severity + "</span></td><td>" + i.status + "</td><td>" + L_.formatTime(i.reported_at) + "</td></tr>";
            });
            html += "</tbody></table>";
            output.innerHTML = html;
        }).catch(function (e) {
            output.innerHTML = '<div style="color:#EF4444;">Error: ' + e.message + "</div>";
        });
    };

    window.generateCustomReport = function () {
        const from = document.getElementById("reportFromDate").value;
        const to = document.getElementById("reportToDate").value;
        if (!from || !to) {
            alert("Please select both dates");
            return;
        }
        generateReport("custom");
    };

    window.downloadCSV = function () {
        const output = document.getElementById("reportOutput");
        if (!output) return;
        const tables = output.querySelectorAll("table");
        if (!tables.length) return;

        const table = tables[0];
        let csv = "";
        table.querySelectorAll("tr").forEach(function (tr) {
            const row = [];
            tr.querySelectorAll("th, td").forEach(function (cell) {
                row.push('"' + cell.textContent.replace(/"/g, '""') + '"');
            });
            csv += row.join(",") + "\n";
        });

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "jolodhar_report_" + Date.now() + ".csv";
        a.click();
        URL.revokeObjectURL(url);
    };

    // ===== DIGITAL TWIN =====
    window.loadTwinSensor = function () {
        const select = document.getElementById("twinSensorSelect");
        if (!select || !select.value) return;
        const sensorId = select.value;

        L_.api(J.endpoints.sensors + "/" + sensorId).then(function (data) {
            if (!data.sensor) return;
            const s = data.sensor;
            const ratio = s.last_reading / (s.drain_depth || 150);
            const waterPct = Math.min(100, ratio * 100);

            const blockageRisk = ratio > 0.7 ? "High" : ratio > 0.4 ? "Medium" : "Low";
            const floodRisk = ratio > 0.85 ? "Critical" : ratio > 0.6 ? "High" : "Low";

            setText("dtWaterLevel", s.last_reading + " cm");
            setText("dtFlowRate", (s.last_reading / 50).toFixed(2));
            setText("dtBlockageRisk", blockageRisk);
            setText("dtFloodRisk", floodRisk);

            const view = document.getElementById("digitalTwinView");
            if (view) {
                view.innerHTML = `
                    <div class="twin-visual">
                        <h3 style="color:#0EA5E9;margin-bottom:8px;">${s.sensor_id}</h3>
                        <p style="color:#94A3B8;font-size:12px;margin-bottom:16px;">${s.location_name} • ${s.district}</p>
                        <div class="twin-drain">
                            <div class="twin-water" style="height:${waterPct}%;"></div>
                        </div>
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:12px;">
                            <div><strong style="color:#0EA5E9;">Water Level</strong><br>${s.last_reading} cm / ${s.drain_depth} cm</div>
                            <div><strong style="color:#0EA5E9;">Battery</strong><br>${s.battery}%</div>
                            <div><strong style="color:#0EA5E9;">Status</strong><br>${s.status}</div>
                        </div>
                    </div>
                `;
            }

            // Render chart
            renderTwinChart(data.readings || []);
        }).catch(function (e) {
            console.error("Twin error:", e);
        });
    };

    function renderTwinChart(readings) {
        const canvas = document.getElementById("twinChart");
        if (!canvas || typeof Chart === "undefined") return;

        // Reverse so oldest first
        const sorted = readings.slice().reverse();
        const labels = sorted.map(function (r) { return L_.formatTime(r.timestamp); });
        const waterData = sorted.map(function (r) { return r.water_level; });
        const rainData = sorted.map(function (r) { return r.rainfall; });

        if (twinChart) twinChart.destroy();
        const ctx = canvas.getContext("2d");
        twinChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Water Level (cm)",
                        data: waterData,
                        borderColor: "#0EA5E9",
                        backgroundColor: "rgba(14, 165, 233, 0.15)",
                        tension: 0.4,
                        fill: true,
                        yAxisID: "y"
                    },
                    {
                        label: "Rainfall (mm)",
                        data: rainData,
                        borderColor: "#A855F7",
                        backgroundColor: "rgba(168, 85, 247, 0.1)",
                        tension: 0.4,
                        fill: false,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { labels: { color: "#CBD5E1" } } },
                scales: {
                    x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y: { position: "left", ticks: { color: "#0EA5E9" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y1: { position: "right", ticks: { color: "#A855F7" }, grid: { drawOnChartArea: false } }
                }
            }
        });
    }

    function setText(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    // ===== CLIMATE ANALYSIS =====
    let monthlyClimateChart = null;
    let droughtTrendChart = null;

    window.loadClimateAnalysis = function () {
        const distSel = document.getElementById("climateDistrictSelect");
        const yearSel = document.getElementById("climateYearSelect");
        if (!distSel || !yearSel) return;

        const district = distSel.value;
        const year = yearSel.value;
        const url = J.endpoints.climateUnified(district) + "?year=" + year;

        // Show loading
        ["droughtIndex", "avgTemp", "avgHumidity", "avgSoil", "nasaTemp", "tomorrowRain"].forEach(function (id) {
            setText(id, "—");
        });

        L_.api(url).then(function (data) {
            // Mendeley historical data
            if (data.mendeley && data.mendeley.drought_analysis) {
                const d = data.mendeley.drought_analysis;
                setText("droughtIndex", d.drought_index);
                setText("avgTemp", d.avg_temperature);
                setText("avgHumidity", d.avg_humidity);
                setText("avgSoil", d.avg_soil_moisture);
                const catEl = document.getElementById("droughtCategory");
                if (catEl) catEl.textContent = lang === "bn" ? d.category_bn : d.category;
            }

            // NASA POWER live
            if (data.nasa_power && data.nasa_power.temperature) {
                setText("nasaTemp", data.nasa_power.temperature + "°C");
            }

            // Tomorrow forecast
            if (data.forecast && data.forecast.rain_probability !== undefined) {
                setText("tomorrowRain", data.forecast.rain_probability + "%");
            }

            // Render monthly chart
            if (data.mendeley && data.mendeley.monthly_summary) {
                renderMonthlyClimateChart(data.mendeley.monthly_summary);
            }

            // Render drought trend
            if (data.mendeley && data.mendeley.yearly_trend) {
                renderDroughtTrendChart(data.mendeley.yearly_trend);
            }

            // Render comparison table
            renderComparisonTable(data);
        }).catch(function (e) {
            console.error("Climate analysis error:", e);
        });
    };

    function renderMonthlyClimateChart(monthly) {
        const canvas = document.getElementById("monthlyClimateChart");
        if (!canvas || typeof Chart === "undefined") return;

        if (monthlyClimateChart) monthlyClimateChart.destroy();
        const ctx = canvas.getContext("2d");
        monthlyClimateChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: monthly.map(function (m) { return m.month_name; }),
                datasets: [
                    {
                        label: "Avg Temp (°C)",
                        data: monthly.map(function (m) { return m.avg_temp; }),
                        borderColor: "#EF4444",
                        backgroundColor: "rgba(239, 68, 68, 0.1)",
                        tension: 0.4,
                        yAxisID: "y"
                    },
                    {
                        label: "Humidity (%)",
                        data: monthly.map(function (m) { return m.avg_humidity; }),
                        borderColor: "#0EA5E9",
                        backgroundColor: "rgba(14, 165, 233, 0.1)",
                        tension: 0.4,
                        yAxisID: "y1"
                    },
                    {
                        label: "Soil Moisture",
                        data: monthly.map(function (m) { return m.avg_soil; }),
                        borderColor: "#14B8A6",
                        backgroundColor: "rgba(20, 184, 166, 0.1)",
                        tension: 0.4,
                        yAxisID: "y2"
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: "#CBD5E1" } } },
                scales: {
                    x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y: { position: "left", ticks: { color: "#EF4444" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y1: { position: "right", ticks: { color: "#0EA5E9" }, grid: { drawOnChartArea: false } },
                    y2: { display: false }
                }
            }
        });
    }

    function renderDroughtTrendChart(trend) {
        const canvas = document.getElementById("droughtTrendChart");
        if (!canvas || typeof Chart === "undefined") return;

        if (droughtTrendChart) droughtTrendChart.destroy();
        const ctx = canvas.getContext("2d");
        droughtTrendChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: trend.map(function (t) { return t.year; }),
                datasets: [{
                    label: "Drought Index",
                    data: trend.map(function (t) { return t.drought_index; }),
                    backgroundColor: trend.map(function (t) {
                        if (t.drought_index >= 60) return "#EF4444";
                        if (t.drought_index >= 40) return "#F97316";
                        if (t.drought_index >= 25) return "#F59E0B";
                        if (t.drought_index >= 10) return "#3B82F6";
                        return "#10B981";
                    }),
                    borderColor: "rgba(14, 165, 233, 0.5)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: "#CBD5E1" } } },
                scales: {
                    x: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" } },
                    y: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(51,65,85,0.3)" }, max: 100 }
                }
            }
        });
    }

    function renderComparisonTable(data) {
        const container = document.getElementById("comparisonTable");
        if (!container) return;

        const m = data.mendeley || {};
        const d = m.drought_analysis || {};
        const n = data.nasa_power || {};
        const f = data.forecast || {};

        container.innerHTML = `
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th class="col-hist">Mendeley Historical (${d.year || '—'})</th>
                        <th class="col-live">NASA POWER (Live)</th>
                        <th class="col-live">Forecast (Tomorrow)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Temperature</td>
                        <td class="col-hist">${d.avg_temperature !== undefined ? d.avg_temperature + ' °C' : '—'}</td>
                        <td class="col-live">${n.temperature !== undefined ? n.temperature + ' °C' : '—'}</td>
                        <td class="col-live">${f.temp_max !== undefined ? f.temp_max + ' °C (max)' : '—'}</td>
                    </tr>
                    <tr>
                        <td>Humidity</td>
                        <td class="col-hist">${d.avg_humidity !== undefined ? d.avg_humidity + ' %' : '—'}</td>
                        <td class="col-live">${n.humidity !== undefined ? n.humidity + ' %' : '—'}</td>
                        <td class="col-live">${f.hourly && f.hourly.length ? f.hourly[0].humidity + ' %' : '—'}</td>
                    </tr>
                    <tr>
                        <td>Precipitation</td>
                        <td class="col-hist">—</td>
                        <td class="col-live">${n.precipitation !== undefined ? n.precipitation + ' mm' : '—'}</td>
                        <td class="col-live">${f.precipitation_sum !== undefined ? f.precipitation_sum + ' mm' : '—'}</td>
                    </tr>
                    <tr>
                        <td>Wind Speed</td>
                        <td class="col-hist">—</td>
                        <td class="col-live">${n.wind_speed !== undefined ? n.wind_speed + ' m/s' : '—'}</td>
                        <td class="col-live">${f.wind_speed_max !== undefined ? f.wind_speed_max + ' m/s' : '—'}</td>
                    </tr>
                    <tr>
                        <td>Soil Moisture</td>
                        <td class="col-hist">${d.avg_soil_moisture !== undefined ? d.avg_soil_moisture : '—'}</td>
                        <td class="col-live">—</td>
                        <td class="col-live">—</td>
                    </tr>
                    <tr>
                        <td>Drought Index</td>
                        <td class="col-hist"><strong>${d.drought_index !== undefined ? d.drought_index : '—'}</strong></td>
                        <td class="col-live">—</td>
                        <td class="col-live">—</td>
                    </tr>
                    <tr>
                        <td>Rain Probability</td>
                        <td class="col-hist">—</td>
                        <td class="col-live">—</td>
                        <td class="col-live"><strong style="color:${f.will_rain ? '#0EA5E9' : '#10B981'};">${f.rain_probability !== undefined ? f.rain_probability + '%' : '—'}</strong></td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top:12px;font-size:11px;color:#64748B;">
                <i class="fas fa-info-circle"></i> Data sources: ${data.data_sources ? data.data_sources.join(', ') : '—'}
            </div>
        `;
    }

    window.loadAllDrought = function () {
        const grid = document.getElementById("allDroughtGrid");
        if (!grid) return;

        grid.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i></div>';

        L_.api(J.endpoints.mendeleyAllDrought).then(function (data) {
            const districts = data.districts || [];
            if (!districts.length) {
                grid.innerHTML = '<div class="loading-spinner">No data</div>';
                return;
            }
            grid.innerHTML = "";
            districts.forEach(function (d) {
                const cell = document.createElement("div");
                cell.className = "drought-cell severity-" + d.severity;
                cell.innerHTML = `
                    <div class="dc-name">${lang === "bn" ? d.bn_name : d.district}</div>
                    <div class="dc-index">${d.drought_index}</div>
                    <div class="dc-cat">${lang === "bn" ? d.category_bn : d.category}</div>
                `;
                grid.appendChild(cell);
            });
        }).catch(function (e) {
            grid.innerHTML = '<div class="loading-spinner">Error loading data</div>';
        });
    };

    // ===== DATA SOURCES PAGE =====
    window.loadDataSourcesPage = function () {
        const cardsEl = document.getElementById("dataSourceCards");
        const distEl = document.getElementById("districtsCoverage");
        if (!cardsEl) return;

        L_.api(J.endpoints.dataSources).then(function (data) {
            const sources = data.sources || [];
            cardsEl.innerHTML = "";
            const colorMap = {
                "NASA POWER API": "stat-blue",
                "Mendeley BD Dataset": "stat-purple",
                "Open-Meteo Forecast API": "stat-green"
            };
            const iconMap = {
                "NASA POWER API": "fa-satellite",
                "Mendeley BD Dataset": "fa-database",
                "Open-Meteo Forecast API": "fa-cloud-rain"
            };
            sources.forEach(function (s) {
                const card = document.createElement("div");
                card.className = "stat-card " + (colorMap[s.name] || "stat-blue");
                const params = (s.parameters || []).slice(0, 6).join(", ");
                card.innerHTML = `
                    <div class="stat-icon"><i class="fas ${iconMap[s.name] || 'fa-database'}"></i></div>
                    <div class="stat-body">
                        <div class="stat-label" style="font-size:13px;font-weight:700;color:#F1F5F9;">${s.name}</div>
                        <div class="stat-sub" style="margin-top:4px;">${s.type}</div>
                        <div class="stat-sub" style="margin-top:6px;font-size:10px;">${params}${s.parameters && s.parameters.length > 6 ? '...' : ''}</div>
                        <div class="stat-sub" style="margin-top:4px;">${s.usage}</div>
                        ${s.districts_count ? '<div class="stat-sub">Districts: ' + s.districts_count + '</div>' : ''}
                    </div>
                `;
                cardsEl.appendChild(card);
            });

            // Render districts coverage
            if (distEl) {
                L_.api(J.endpoints.mendeleyDistricts).then(function (dData) {
                    const districts = dData.districts || [];
                    distEl.innerHTML = "";
                    districts.forEach(function (d) {
                        const cell = document.createElement("div");
                        cell.className = "coverage-cell risk-" + d.drought_risk;
                        cell.innerHTML = `
                            <div class="cc-name">${lang === "bn" ? d.bn_name : d.name}</div>
                            <div class="cc-region">${d.region} • Risk: ${d.drought_risk}</div>
                        `;
                        distEl.appendChild(cell);
                    });
                }).catch(function () {});
            }
        }).catch(function (e) {
            cardsEl.innerHTML = '<div class="loading-spinner">Error</div>';
        });
    };

    // ===== INIT =====
    document.addEventListener("DOMContentLoaded", function () {
        lang = J.lang;

        // Determine active page and init accordingly
        const pageEl = document.querySelector(".page-section");
        if (!pageEl) return;

        // Check what's on the page
        if (document.getElementById("dashboardChart")) {
            loadDashboardChart();
        }
        if (document.getElementById("featureImportanceChart")) {
            L_.api(J.endpoints.mlFeatureImportance).then(function (data) {
                renderFIChart(document.getElementById("featureImportanceChart"), data.feature_importance || []);
            }).catch(function () {});
        }
        if (document.getElementById("twinSensorSelect")) {
            L_.api(J.endpoints.sensors).then(function (data) {
                const sel = document.getElementById("twinSensorSelect");
                (data.sensors || []).slice(0, 20).forEach(function (s) {
                    const opt = document.createElement("option");
                    opt.value = s.sensor_id;
                    opt.textContent = s.sensor_id + " — " + s.location_name;
                    sel.appendChild(opt);
                });
            }).catch(function () {});
        }
        // Climate Analysis page
        if (document.getElementById("climateDistrictSelect")) {
            loadClimateAnalysis();
            loadAllDrought();
        }
        // Data Sources page
        if (document.getElementById("dataSourceCards")) {
            loadDataSourcesPage();
        }
    });

})();
