async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("jwt");

    const response = await fetch(endpoint, {
        ...options,
        headers: {
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error("Authentication failed");
    }

    return await response.json();
}

function formatDateTime(dateString) {

if (!dateString) {
    return "-";
}

const date = new Date(dateString);

if (isNaN(date.getTime())) {
    return "-";
}

return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
});
}

function formatMeetingDateTime(value) {

if (!value) {
    return "-";
}

const date = new Date(value);

if (isNaN(date.getTime())) {
    return value;
}

return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true
});
}
function showUpdateMessage(message) {

const element =
    document.getElementById("updateMessage");

if (!element) {
    console.log("updateMessage element not found");
    return;
}

element.textContent = message;

element.style.display = "block";

console.log("SUCCESS MESSAGE:", message);

setTimeout(() => {
    element.style.display = "none";
}, 4000);
}
function setActiveNavigation() {

const sections = [
    {
        id: "dashboard",
        link: document.querySelector('.sidebar a[href="#dashboard"]')
    },
    {
        id: "customers-section",
        link: document.querySelector('.sidebar a[href="#customers-section"]')
    },
    {
        id: "leads-section",
        link: document.querySelector('.sidebar a[href="#leads-section"]')
    },
    {
        id: "issues-section",
        link: document.querySelector('.sidebar a[href="#issues-section"]')
    },
    {
        id: "meetings-section",
        link: document.querySelector('.sidebar a[href="#meetings-section"]')
    }
];

const scrollPosition = window.scrollY + 150;

let activeSection = "dashboard";

sections.forEach(section => {

    const element = document.getElementById(section.id);

    if (!element) {
        return;
    }

    if (scrollPosition >= element.offsetTop) {
        activeSection = section.id;
    }

});

sections.forEach(section => {

    if (section.link) {
        section.link.classList.remove("active");
    }

});

const active = sections.find(
    section => section.id === activeSection
);

if (active && active.link) {
    active.link.classList.add("active");
}
}


window.addEventListener(
"scroll",
setActiveNavigation
);

window.addEventListener(
"load",
setActiveNavigation
);
let dashboardAutoRefresh = null;
async function loadDashboard() {

if (!localStorage.getItem("jwt")) {
        alert("Please login first.");
        return;
    }

const loadingMessage =
    document.getElementById("loadingMessage");

if (loadingMessage) {
    loadingMessage.style.display = "inline";
}

try {

    const stats = await apiRequest(
        "/admin/stats"
    );

    document.getElementById("customers").textContent =
        stats.customers;

    document.getElementById("leads").textContent =
        stats.leads;

    document.getElementById("issues").textContent =
        stats.open_issues;

    document.getElementById("meetings").textContent =
        stats.booked_meetings;

    document.getElementById("pending").textContent =
        stats.pending_meetings;

        const customers = await apiRequest(
    "/admin/customers"
);

const customerTable =
    document.getElementById("customerTable");

customerTable.innerHTML = "";

customers.customers.forEach(customer => {

    customerTable.innerHTML += `
        <tr>

            <td>${customer.id}</td>

            <td>${customer.sender}</td>

            <td>
                <input
                    id="customer-name-${customer.id}"
                    value="${customer.name || ""}"
                >
            </td>

            <td>
                <input
                    id="customer-email-${customer.id}"
                    value="${customer.email || ""}"
                >
            </td>

            <td>${formatDateTime(customer.created_at)}</td>
<td>${formatDateTime(customer.last_interaction)}</td>

            <td>
                <button
                    onclick="updateCustomer(${customer.id})"
                >
                    Save
                </button>
            </td>

        </tr>
    `;

});


    const leads = await apiRequest(
        "/admin/leads"
    );

    const leadTable =
        document.getElementById("leadTable");

    leadTable.innerHTML = "";

    leads.leads.slice(-10).reverse().forEach(lead => {

        leadTable.innerHTML += `
            <tr>
                <td>${lead.id}</td>
                <td>${lead.sender}</td>
                <td>${lead.requirement}</td>

                <td>
                    <select
                        onchange="updateLead(${lead.id}, null, this.value)"
                    >
                        <option value="normal"
                            ${lead.priority === "normal" ? "selected" : ""}>
                            Normal
                        </option>

                        <option value="high"
                            ${lead.priority === "high" ? "selected" : ""}>
                            High
                        </option>

                        <option value="urgent"
                            ${lead.priority === "urgent" ? "selected" : ""}>
                            Urgent
                        </option>
                    </select>
                </td>

                <td>
                    <select
                        onchange="updateLead(${lead.id}, this.value, null)"
                    >
                        <option value="new"
                            ${lead.status === "new" ? "selected" : ""}>
                            New
                        </option>

                        <option value="contacted"
                            ${lead.status === "contacted" ? "selected" : ""}>
                            Contacted
                        </option>

                        <option value="qualified"
                            ${lead.status === "qualified" ? "selected" : ""}>
                            Qualified
                        </option>

                        <option value="demo_requested"
                            ${lead.status === "demo_requested" ? "selected" : ""}>
                            Demo Requested
                        </option>

                        <option value="converted"
                            ${lead.status === "converted" ? "selected" : ""}>
                            Converted
                        </option>

                        <option value="lost"
                            ${lead.status === "lost" ? "selected" : ""}>
                            Lost
                        </option>
                    </select>
                </td>
            </tr>
        `;


});


    const issueStatus =
    document.getElementById("issueStatusFilter").value;

const issueEndpoint = issueStatus
    ? `/admin/issues?status=${encodeURIComponent(issueStatus)}`
    : "/admin/issues";

const issues = await apiRequest(
    issueEndpoint
);

    const issueTable =
        document.getElementById("issueTable");

    issueTable.innerHTML = "";

    issues.issues.forEach(issue => {

        issueTable.innerHTML += `
    <tr>
        <td>${issue.id}</td>
        <td>${issue.sender}</td>
        <td>${issue.description}</td>

        <td>
            <select
                onchange="updateIssue(${issue.id}, null, this.value)"
            >
                <option value="normal"
                    ${issue.priority === "normal" ? "selected" : ""}>
                    Normal
                </option>

                <option value="high"
                    ${issue.priority === "high" ? "selected" : ""}>
                    High
                </option>

                <option value="urgent"
                    ${issue.priority === "urgent" ? "selected" : ""}>
                    Urgent
                </option>
            </select>
        </td>

        <td>
            <select
                onchange="updateIssue(${issue.id}, this.value, null)"
            >
                <option value="open"
                    ${issue.status === "open" ? "selected" : ""}>
                    Open
                </option>

                <option value="in_progress"
                    ${issue.status === "in_progress" ? "selected" : ""}>
                    In Progress
                </option>

                <option value="resolved"
                    ${issue.status === "resolved" ? "selected" : ""}>
                    Resolved
                </option>
            </select>
        </td>
    </tr>
`;


    });
    const meetingStatus =
    document.getElementById("meetingStatusFilter").value;

const meetingEndpoint = meetingStatus
    ? `/admin/meetings?status=${encodeURIComponent(meetingStatus)}`
    : "/admin/meetings";

const meetings = await apiRequest(
    meetingEndpoint
);

const meetingTable =
    document.getElementById("meetingTable");

meetingTable.innerHTML = "";

meetings.meetings
    .slice()
    .reverse()
    .forEach(meeting => {

        meetingTable.innerHTML += `
            <tr>

                <td>${meeting.id}</td>

                <td>${meeting.sender}</td>

                <td>
    ${formatMeetingDateTime(meeting.requested_start)}
</td>

<td>
    ${formatMeetingDateTime(meeting.requested_end)}
</td>

                <td>
    <select
        class="meeting-status ${meeting.status === "booked"
            ? "booked"
            : meeting.status === "cancelled"
                ? "cancelled"
                : "awaiting"}"
        onchange="updateMeeting(${meeting.id}, this.value)"
    >

        <option value="awaiting_confirmation"
            ${meeting.status === "awaiting_confirmation" ? "selected" : ""}>
            Awaiting Confirmation
        </option>

        <option value="booked"
            ${meeting.status === "booked" ? "selected" : ""}>
            Booked
        </option>

        <option value="cancelled"
            ${meeting.status === "cancelled" ? "selected" : ""}>
            Cancelled
        </option>

    </select>
</td>

                <td>
                    ${meeting.calendar_event_id || "-"}
                </td>

            </tr>
        `;

    });
    if (!dashboardAutoRefresh) {
        dashboardAutoRefresh = setInterval(() => {
            if (localStorage.getItem("jwt")) {
                loadDashboard();
            }
        }, 30000);
    }

} catch (error) {

alert(
    "Unable to load dashboard. Check your API key."
);

} finally {

if (loadingMessage) {
    loadingMessage.style.display = "none";
}

}

}

async function updateMeeting(meetingId, status) {



try {

    const params = new URLSearchParams();

    params.append("status", status);

    const response = await fetch(
        `/admin/meetings/${meetingId}?${params.toString()}`,
        {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("jwt")}`
            }
        }
    );

    if (!response.ok) {
        throw new Error(
            `Server returned ${response.status}`
        );
    }

    await loadDashboard();

showUpdateMessage(
    "Meeting status updated successfully!"
);

} catch (error) {

    alert(
        "Unable to update meeting: " +
        error.message
    );

}
}
async function updateLead(leadId, status = null, priority = null) {



try {

    const params = new URLSearchParams();

    if (status) {
        params.append("status", status);
    }

    if (priority) {
        params.append("priority", priority);
    }

    const response = await fetch(
        `/admin/leads/${leadId}?${params.toString()}`,
        {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("jwt")}`
            }
        }
    );

    if (!response.ok) {
        throw new Error("Failed to update lead");
    }

    await loadDashboard();

showUpdateMessage("Lead updated successfully!");

} catch (error) {

    alert(
        "Unable to update lead. Check your admin API key."
    );

}
}

async function updateIssue(issueId, status = null, priority = null) {


try {

    const params = new URLSearchParams();

    if (status) {
        params.append("status", status);
    }

    if (priority) {
        params.append("priority", priority);
    }

    const response = await fetch(
        `/admin/issues/${issueId}?${params.toString()}`,
        {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("jwt")}`
            }
        }
    );

    if (!response.ok) {
        throw new Error("Failed to update issue");
    }

    await loadDashboard();

showUpdateMessage("Issue updated successfully!");

} catch (error) {

    alert(
        "Unable to update issue. Check your admin API key."
    );

}
}
function filterCustomers() {

const search =
    document.getElementById("customerSearch")
    .value
    .toLowerCase()
    .trim();

const rows =
    document.querySelectorAll("#customerTable tr");

rows.forEach(row => {

    const text =
        row.textContent.toLowerCase();

    row.style.display =
        text.includes(search)
            ? ""
            : "none";

});
}
async function updateCustomer(customerId) {



const name =
    document.getElementById(
        `customer-name-${customerId}`
    ).value;

const email =
    document.getElementById(
        `customer-email-${customerId}`
    ).value;

try {

    const params = new URLSearchParams();

    params.append("name", name);
    params.append("email", email);

    const response = await fetch(
        `/admin/customers/${customerId}?${params.toString()}`,
        {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("jwt")}`
            }
        }
    );

    if (!response.ok) {
        throw new Error(
            `Server returned ${response.status}`
        );
    }

    await loadDashboard();

    showUpdateMessage(
        "Customer updated successfully!"
    );

} catch (error) {

    alert(
        "Unable to update customer: " +
        error.message
    );

}
}

function logoutAdmin() {

localStorage.removeItem("jwt");

document.getElementById("customers").textContent = "-";
document.getElementById("leads").textContent = "-";
document.getElementById("issues").textContent = "-";
document.getElementById("meetings").textContent = "-";
document.getElementById("pending").textContent = "-";

document.getElementById("customerTable").innerHTML = "";
document.getElementById("leadTable").innerHTML = "";
document.getElementById("issueTable").innerHTML = "";
document.getElementById("meetingTable").innerHTML = "";

document.getElementById("lastUpdated").textContent =
    "Not loaded yet";

showUpdateMessage("Logged out successfully.");

}
