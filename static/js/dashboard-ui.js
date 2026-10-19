/* Zyroniq dashboard visual enhancements.
   Uses the existing admin API and preserves admin.js functionality. */

   (() => {
    "use strict";

    const $ = (selector) => document.querySelector(selector);

    function updateDate() {
        const dateElement = $("#currentDate");
        if (!dateElement) return;

        dateElement.textContent = new Date().toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[character]);
    }

    function formatShortDate(value) {
        if (!value) return "Date unavailable";

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "Date unavailable";

        return date.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short"
        });
    }

    function customerInitial(customer) {
        const name = String(customer.name || "").trim();

        if (name) return name.charAt(0).toUpperCase();

        const sender = String(customer.sender || "");
        return sender ? sender.slice(-2) : "?";
    }

    function renderRecentCustomers(customers) {
        const container = $("#recentCustomers");
        if (!container) return;

        const latest = [...customers]
            .sort((a, b) => {
                const first = new Date(b.last_interaction || b.created_at || 0);
                const second = new Date(a.last_interaction || a.created_at || 0);
                return first - second;
            })
            .slice(0, 3);

        if (!latest.length) {
            container.innerHTML =
                '<div class="empty-state">No customers to display yet.</div>';
            return;
        }

        const avatarStyles = ["", "purple", "blue"];

        container.innerHTML = latest.map((customer, index) => {
            const name = customer.name || customer.sender || "Customer";
            const date = formatShortDate(
                customer.last_interaction || customer.created_at
            );

            return `
                <div class="recent-item">
                    <div class="recent-avatar ${avatarStyles[index % avatarStyles.length]}">
                        ${escapeHTML(customerInitial(customer))}
                    </div>
                    <div class="recent-info">
                        <strong>${escapeHTML(name)}</strong>
                        <small>${escapeHTML(customer.sender || "WhatsApp customer")}</small>
                    </div>
                    <span class="recent-date">${escapeHTML(date)}</span>
                </div>
            `;
        }).join("");
    }

    function drawChart() {
        const canvas = $("#customerAnalyticsChart");
        if (!canvas) return;

        const rect = canvas.getBoundingClientRect();
        if (rect.width < 10 || rect.height < 10) return;

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(rect.width * dpr);
        canvas.height = Math.round(rect.height * dpr);

        const ctx = canvas.getContext("2d");
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const width = rect.width;
        const height = rect.height;
        ctx.clearRect(0, 0, width, height);

        const left = 28;
        const right = 8;
        const top = 10;
        const bottom = 23;
        const chartWidth = Math.max(1, width - left - right);
        const chartHeight = Math.max(1, height - top - bottom);

        const monthCount = Math.max(
            3,
            Math.min(12, Number($("#analyticsPeriod")?.value || 6))
        );

        const now = new Date();
        const months = [];

        for (let i = monthCount - 1; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);

            months.push({
                key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`,
                label: date.toLocaleDateString("en-GB", { month: "short" }),
                customers: 0,
                leads: 0
            });
        }

        const monthMap = new Map(months.map(month => [month.key, month]));

        function countRecords(records, type) {
            if (!Array.isArray(records)) return;

            records.forEach(record => {
                if (!record?.created_at) return;

                const date = new Date(record.created_at);
                if (Number.isNaN(date.getTime())) return;

                const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
                const month = monthMap.get(key);

                if (month) {
                    month[type]++;
                }
            });
        }

        // These arrays are populated from the existing API responses.
        countRecords(window.dashboardCustomers || [], "customers");
        countRecords(window.dashboardLeads || [], "leads");

        const highestValue = Math.max(
            1,
            ...months.map(month => Math.max(month.customers, month.leads))
        );

        // Round the chart scale up to a readable value.
        const maxValue = Math.max(5, Math.ceil(highestValue / 5) * 5);

        ctx.font = "10px Inter, sans-serif";
        ctx.textBaseline = "middle";
        ctx.textAlign = "right";

        for (let i = 0; i <= 3; i++) {
            const y = top + chartHeight * i / 3;

            ctx.strokeStyle = "rgba(177, 207, 249, 0.12)";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(left, y);
            ctx.lineTo(width - right, y);
            ctx.stroke();

            ctx.fillStyle = "#8298b8";
            ctx.fillText(
                String(Math.round(maxValue * (3 - i) / 3)),
                left - 9,
                y
            );
        }

        const groupWidth = chartWidth / monthCount;
        const barWidth = Math.min(18, groupWidth * 0.24);

        months.forEach((month, index) => {
            const centerX = left + groupWidth * (index + 0.5);

            const customerHeight = month.customers / maxValue * chartHeight;
            const leadHeight = month.leads / maxValue * chartHeight;

            const blueGradient = ctx.createLinearGradient(
                0, top + chartHeight - customerHeight, 0, top + chartHeight
            );
            blueGradient.addColorStop(0, "#59d0ff");
            blueGradient.addColorStop(1, "#2875ed");

            const purpleGradient = ctx.createLinearGradient(
                0, top + chartHeight - leadHeight, 0, top + chartHeight
            );
            purpleGradient.addColorStop(0, "#a98aff");
            purpleGradient.addColorStop(1, "#6846ef");

            function roundedBar(x, y, w, h, color) {
                if (h <= 0) return;

                ctx.fillStyle = color;
                ctx.beginPath();

                if (typeof ctx.roundRect === "function") {
                    ctx.roundRect(x, y, w, h, [Math.min(5, w / 2), Math.min(5, w / 2), 1, 1]);
                } else {
                    ctx.rect(x, y, w, h);
                }

                ctx.fill();
            }

            roundedBar(
                centerX - barWidth - 2,
                top + chartHeight - customerHeight,
                barWidth,
                customerHeight,
                blueGradient
            );

            roundedBar(
                centerX + 2,
                top + chartHeight - leadHeight,
                barWidth,
                leadHeight,
                purpleGradient
            );

            ctx.fillStyle = "#93a8c5";
            ctx.textAlign = "center";
            ctx.font = "9px Inter, sans-serif";
            ctx.fillText(month.label, centerX, height - 9);
        });
    }

    async function loadVisualData() {
        if (!localStorage.getItem("jwt")) return;

        const token = localStorage.getItem("jwt");

        try {
            const [customersResponse, leadsResponse] = await Promise.all([
                fetch("/admin/customers", {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }),
                fetch("/admin/leads", {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                })
            ]);

            if (customersResponse.status === 401 || leadsResponse.status === 401) {
                console.warn("Dashboard session may have expired.");
                return;
            }

            if (!customersResponse.ok || !leadsResponse.ok) {
                console.error("Could not load dashboard analytics data.");
                return;
            }

            const [customersData, leadsData] = await Promise.all([
                customersResponse.json(),
                leadsResponse.json()
            ]);

            window.dashboardCustomers = customersData.customers || [];
            window.dashboardLeads = leadsData.leads || [];

            renderRecentCustomers(window.dashboardCustomers);
            drawChart();

        } catch (error) {
            console.error("Could not load dashboard data:", error);
        }
    }

    function wireSearch() {
        const globalSearch = $("#globalSearch");
        const customerSearch = $("#customerSearch");

        if (!globalSearch || !customerSearch) return;

        globalSearch.addEventListener("input", () => {
            customerSearch.value = globalSearch.value;
            if (typeof window.filterCustomers === "function") {
                window.filterCustomers();
            }
        });

        globalSearch.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                globalSearch.value = "";
                customerSearch.value = "";
                if (typeof window.filterCustomers === "function") {
                    window.filterCustomers();
                }
            }
        });
    }

    function wireNavigation() {
        const links = document.querySelectorAll(".sidebar-nav a[href^='#']");

        links.forEach((link) => {
            link.addEventListener("click", () => {
                links.forEach((item) => item.classList.remove("active"));
                link.classList.add("active");
            });
        });
    }

    function wireAddCustomer() {
        const button = $("#addCustomerButton");
        if (!button) return;

        button.addEventListener("click", () => {
            const section = $("#customers-section");
            const search = $("#customerSearch");

            section?.scrollIntoView({ behavior: "smooth", block: "start" });

            if (search) {
                setTimeout(() => search.focus(), 350);
            }
        });
    }

    function initialize() {
        updateDate();
        drawChart();
        wireSearch();
        wireNavigation();
        wireAddCustomer();

        $("#analyticsPeriod")?.addEventListener("change", drawChart);

        let resizeTimer;
        window.addEventListener("resize", () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(drawChart, 100);
        });

        window.addEventListener("load", () => {
            drawChart();
            loadVisualData();
        });

        window.addEventListener("storage", (event) => {
            if (event.key === "jwt" && event.newValue) {
                loadVisualData();
            }
        });

        document.addEventListener("visibilitychange", () => {
            if (!document.hidden) {
                loadVisualData();
                drawChart();
            }
        });

        const originalLoadDashboard = window.loadDashboard;

        if (typeof originalLoadDashboard === "function") {
            window.loadDashboard = async function (...args) {
                const result = await originalLoadDashboard.apply(this, args);

                if (localStorage.getItem("jwt")) {
                    await loadVisualData();
                } else {
                    window.dashboardCustomers = [];
                    window.dashboardLeads = [];
                    renderRecentCustomers([]);
                }

                drawChart();
                return result;
            };
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize, { once: true });
    } else {
        initialize();
    }
})();
