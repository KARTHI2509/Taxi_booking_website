// Central JavaScript for Taxi Booking Platform
const BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
    ? "http://127.0.0.1:8000" 
    : (window.location.hostname.includes("vercel.app")
        ? (localStorage.getItem("BACKEND_URL") || "https://taxi-booking-website-f5jn.onrender.com")
        : ""); // Relative path when served directly from Django (Render/Heroku collectstatic)

// Toast Notifications System
function showToast(message, type = "success") {
    const existing = document.getElementById("appToast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "appToast";
    toast.className = "alert-toast glass-panel";
    
    let iconClass = "fa-circle-check";
    let color = "var(--success)";
    if (type === "warning") {
        iconClass = "fa-triangle-exclamation";
        color = "var(--warning)";
    } else if (type === "danger") {
        iconClass = "fa-circle-xmark";
        color = "var(--danger)";
    }

    toast.style.borderLeft = `5px solid ${color}`;
    toast.innerHTML = `
        <i class="fa-solid ${iconClass}" style="color: ${color}; font-size: 1.3rem;"></i>
        <span style="font-weight: 500;">${message}</span>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 50);

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Show/Hide loaders
function toggleLoader(show) {
    const loader = document.getElementById("loadingIndicator");
    if (loader) {
        loader.style.display = show ? "flex" : "none";
    }
}

// Reusable API Request Wrapper
async function apiCall(endpoint, method = "GET", body = null) {
    toggleLoader(true);
    const url = `${BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: {
            "Content-Type": "application/json",
        }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        toggleLoader(false);
        if (!response.ok) {
            throw new Error(data.error || "Something went wrong");
        }
        return data;
    } catch (error) {
        toggleLoader(false);
        showToast(error.message, "danger");
        throw error;
    }
}

// Session Management
function getCurrentUser() {
    const userJson = localStorage.getItem("currentUser");
    return userJson ? JSON.parse(userJson) : null;
}

function setCurrentUser(user) {
    localStorage.setItem("currentUser", JSON.stringify(user));
}

function clearUser() {
    localStorage.removeItem("currentUser");
    localStorage.removeItem("activeBookingId"); // Clear active bookings
    window.location.href = "login.html";
}

// Route Guard to redirect users based on auth status
function checkAuth() {
    const path = window.location.pathname;
    const page = path.substring(path.lastIndexOf('/') + 1) || "index.html";
    const user = getCurrentUser();

    const protectedPages = [
        "booking.html",
        "payments.html",
        "ride_history.html",
        "customer_dashboard.html",
        "driver_dashboard.html",
        "admin_dashboard.html"
    ];

    if (protectedPages.includes(page)) {
        if (!user) {
            window.location.href = "login.html";
            return;
        }

        // Role-based page access checks
        if (page === "customer_dashboard.html" && user.role !== "customer") {
            window.location.href = `${user.role}_dashboard.html`;
        }
        if (page === "driver_dashboard.html" && user.role !== "driver") {
            window.location.href = `${user.role}_dashboard.html`;
        }
        if (page === "admin_dashboard.html" && user.role !== "admin") {
            window.location.href = `${user.role}_dashboard.html`;
        }
    }

    if ((page === "login.html" || page === "register.html") && user) {
        window.location.href = `${user.role}_dashboard.html`;
    }
}

// Dynamic Header Injector
function renderNavbar() {
    const header = document.querySelector("header");
    if (!header) return;

    const path = window.location.pathname;
    const currentPage = path.substring(path.lastIndexOf('/') + 1) || "index.html";
    const user = getCurrentUser();

    let navItems = `
        <li><a href="index.html" class="nav-link ${currentPage === "index.html" ? "active" : ""}">Home</a></li>
        <li><a href="drivers.html" class="nav-link ${currentPage === "drivers.html" ? "active" : ""}">Drivers</a></li>
    `;

    if (!user) {
        navItems += `
            <li><a href="login.html" class="nav-link ${currentPage === "login.html" ? "active" : ""}">Login</a></li>
            <li><a href="register.html" class="nav-link ${currentPage === "register.html" ? "active" : ""}">Register</a></li>
        `;
    } else {
        if (user.role === "customer") {
            navItems += `
                <li><a href="customer_dashboard.html" class="nav-link ${currentPage === "customer_dashboard.html" ? "active" : ""}">Dashboard</a></li>
                <li><a href="booking.html" class="nav-link ${currentPage === "booking.html" ? "active" : ""}">Book Ride</a></li>
                <li><a href="ride_history.html" class="nav-link ${currentPage === "ride_history.html" ? "active" : ""}">My History</a></li>
            `;
        } else if (user.role === "driver") {
            navItems += `
                <li><a href="driver_dashboard.html" class="nav-link ${currentPage === "driver_dashboard.html" ? "active" : ""}">Driver Panel</a></li>
                <li><a href="ride_history.html" class="nav-link ${currentPage === "ride_history.html" ? "active" : ""}">Trips History</a></li>
            `;
        } else if (user.role === "admin") {
            navItems += `
                <li><a href="admin_dashboard.html" class="nav-link ${currentPage === "admin_dashboard.html" ? "active" : ""}">Admin Console</a></li>
            `;
        }
    }

    const badgeHTML = user 
        ? `<div class="user-badge"><i class="fa-solid fa-user"></i> <span>${user.name} (${user.role})</span></div>
           <button onclick="clearUser()" class="btn-logout">Logout</button>`
        : `<a href="booking.html" class="btn-primary"><i class="fa-solid fa-taxi"></i> Book Now</a>`;

    header.className = "glass-panel";
    header.style.margin = "1rem 5% 0 5%";
    header.style.borderRadius = "16px";
    header.innerHTML = `
        <a href="index.html" class="logo">
            <i class="fa-solid fa-taxi"></i>
            <span>CabGo</span>
        </a>
        <nav>
            <ul class="nav-menu">
                ${navItems}
            </ul>
        </nav>
        <div style="display: flex; align-items: center; gap: 1rem;">
            ${badgeHTML}
        </div>
    `;
}

// ----------------------------------------------------
// PAGE-SPECIFIC HANDLERS
// ----------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    checkAuth();
    renderNavbar();

    const path = window.location.pathname;
    const page = path.substring(path.lastIndexOf('/') + 1) || "index.html";

    if (page === "login.html") {
        initLoginPage();
    } else if (page === "register.html") {
        initRegisterPage();
    } else if (page === "booking.html") {
        initBookingPage();
    } else if (page === "drivers.html") {
        initDriversPage();
    } else if (page === "payments.html") {
        initPaymentsPage();
    } else if (page === "ride_history.html") {
        initRideHistoryPage();
    } else if (page === "customer_dashboard.html") {
        initCustomerDashboard();
    } else if (page === "driver_dashboard.html") {
        initDriverDashboard();
    } else if (page === "admin_dashboard.html") {
        initAdminDashboard();
    }
});

// LOGIN PAGE INITIALIZER
function initLoginPage() {
    const roleBtns = document.querySelectorAll(".role-btn");
    const loginForm = document.getElementById("loginForm");
    const usernameLabel = document.getElementById("usernameLabel");
    const passwordLabel = document.getElementById("passwordLabel");
    const loginEmailInput = document.getElementById("loginEmail");
    const loginPassInput = document.getElementById("loginPassword");
    let selectedRole = "customer";

    roleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            roleBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedRole = btn.getAttribute("data-role");

            if (selectedRole === "admin") {
                usernameLabel.innerText = "Username";
                passwordLabel.innerText = "Password";
                loginEmailInput.placeholder = "Enter Admin Username";
                loginEmailInput.type = "text";
            } else if (selectedRole === "driver") {
                usernameLabel.innerText = "Driver Email";
                passwordLabel.innerText = "License Number or Phone";
                loginEmailInput.placeholder = "Enter driver email";
                loginEmailInput.type = "email";
                loginPassInput.placeholder = "Enter your phone or license number";
            } else {
                usernameLabel.innerText = "Customer Email";
                passwordLabel.innerText = "Password";
                loginEmailInput.placeholder = "Enter customer email";
                loginEmailInput.type = "email";
                loginPassInput.placeholder = "Enter your password";
            }
        });
    });

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = loginEmailInput.value.trim();
        const password = loginPassInput.value.trim();

        if (!email || !password) {
            showToast("Please fill in all fields", "warning");
            return;
        }

        try {
            const data = await apiCall("/api/login/", "POST", { role: selectedRole, email, password });
            showToast(data.message, "success");
            setCurrentUser(data.user);
            
            // Redirect based on role
            setTimeout(() => {
                window.location.href = `${data.user.role}_dashboard.html`;
            }, 1000);
        } catch (err) {
            // Error handled by wrapper toast
        }
    });
}

// REGISTRATION PAGE INITIALIZER
function initRegisterPage() {
    const registerForm = document.getElementById("registerForm");
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const full_name = document.getElementById("regName").value.trim();
        const email = document.getElementById("regEmail").value.trim();
        const phone = document.getElementById("regPhone").value.trim();
        const address = document.getElementById("regAddress").value.trim();
        const password = document.getElementById("regPassword").value.trim();

        if (!full_name || !email || !password) {
            showToast("Please fill in required fields", "warning");
            return;
        }

        try {
            const data = await apiCall("/customers/add/", "POST", {
                full_name, email, phone, address, password
            });
            showToast("Registration successful! Redirecting to login...", "success");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);
        } catch (err) {}
    });
}

// BOOKING PAGE INITIALIZER
function initBookingPage() {
    const bookForm = document.getElementById("bookingForm");
    const pickupInput = document.getElementById("pickup");
    const dropInput = document.getElementById("drop");
    const vehicleTypeSelect = document.getElementById("vehicleType");
    const fareEstimateBox = document.getElementById("fareEstimateBox");
    const estDistanceEl = document.getElementById("estDistance");
    const estFareEl = document.getElementById("estFare");
    
    // Auto populate date
    const dateInput = document.getElementById("bookingDate");
    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.value = today;
    }

    // Vehicle Fare Multipliers (Per km)
    const baseRates = {
        "Bike": 10,
        "Auto": 15,
        "Hatchback": 20,
        "Sedan": 25,
        "SUV": 35,
        "Luxury": 50
    };

    function calculateEstimate() {
        const pickup = pickupInput.value.trim();
        const drop = dropInput.value.trim();
        const vType = vehicleTypeSelect.value;

        if (pickup && drop && vType) {
            // Generate a deterministic distance based on character lengths
            const distance = Math.max(5, (pickup.length + drop.length) % 25 + 3);
            const rate = baseRates[vType] || 20;
            const fare = distance * rate;

            estDistanceEl.innerText = `${distance} km`;
            estFareEl.innerText = `₹${fare}`;
            fareEstimateBox.style.display = "block";
            return fare;
        } else {
            fareEstimateBox.style.display = "none";
            return 0;
        }
    }

    pickupInput.addEventListener("input", calculateEstimate);
    dropInput.addEventListener("input", calculateEstimate);
    vehicleTypeSelect.addEventListener("change", calculateEstimate);

    bookForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = getCurrentUser();
        const pickup = pickupInput.value.trim();
        const drop = dropInput.value.trim();
        const vType = vehicleTypeSelect.value;
        const bDate = dateInput.value;
        
        const fare = calculateEstimate();

        if (!pickup || !drop || !vType || !bDate) {
            showToast("Please fill all fields", "warning");
            return;
        }

        try {
            // Check for available driver with that vehicle type
            const drivers = await apiCall("/drivers/");
            const vehicles = await apiCall("/vehicles/");
            
            // Filter drivers who are Available
            const availableDrivers = drivers.filter(d => d.availability === "Available");
            
            // Find an available driver whose vehicle matches the requested type
            let assignedDriver = "Pending";
            for (let d of availableDrivers) {
                const matchVehicle = vehicles.find(v => v.driver_name === d.driver_name && v.vehicle_type === vType);
                if (matchVehicle) {
                    assignedDriver = d.driver_name;
                    break;
                }
            }

            const bookingData = {
                customer_name: user.name,
                driver_name: assignedDriver,
                pickup_location: pickup,
                drop_location: drop,
                booking_date: bDate,
                fare: fare,
                ride_status: assignedDriver === "Pending" ? "Requested" : "Accepted"
            };

            const response = await apiCall("/bookings/add/", "POST", bookingData);
            showToast("Ride Booked Successfully!", "success");
            localStorage.setItem("activeBookingId", response.booking_id);

            // Redirect to Payments to lock down transaction
            setTimeout(() => {
                window.location.href = "payments.html";
            }, 1500);
        } catch (err) {}
    });
}

// DRIVER PAGE INITIALIZER
async function initDriversPage() {
    const listContainer = document.getElementById("driversList");
    if (!listContainer) return;

    try {
        const drivers = await apiCall("/drivers/");
        const vehicles = await apiCall("/vehicles/");

        listContainer.innerHTML = "";
        if (drivers.length === 0) {
            listContainer.innerHTML = `<div class="glass-panel" style="padding:2rem;text-align:center;">No drivers registered yet.</div>`;
            return;
        }

        drivers.forEach(d => {
            // Find their vehicle
            const v = vehicles.find(veh => veh.driver_name === d.driver_name);
            const vehicleInfo = v 
                ? `${v.model} (${v.vehicle_type}) - ${v.vehicle_number} [Seats: ${v.seating_capacity}]` 
                : "No vehicle assigned";

            const availBadge = d.availability === "Available" 
                ? `<span class="badge badge-available">Available</span>`
                : (d.availability === "Busy" 
                    ? `<span class="badge badge-busy">Busy</span>` 
                    : `<span class="badge badge-offline">Offline</span>`);

            // Generate deterministic ratings based on experience
            const rating = Math.min(5, 4.0 + (d.experience % 10) * 0.1).toFixed(1);

            const card = document.createElement("div");
            card.className = "glass-panel card";
            card.innerHTML = `
                <div class="card-icon"><i class="fa-solid fa-id-card"></i></div>
                <h3 style="display:flex; justify-content:space-between; align-items:center;">
                    <span>${d.driver_name}</span>
                    ${availBadge}
                </h3>
                <p style="margin-top:0.5rem;"><strong>Email:</strong> ${d.email}</p>
                <p><strong>Phone:</strong> ${d.phone}</p>
                <p><strong>License:</strong> ${d.license_number}</p>
                <p><strong>Experience:</strong> ${d.experience} Years</p>
                <p><strong>Vehicle:</strong> ${vehicleInfo}</p>
                <div style="margin-top:1rem; color: var(--primary); font-weight:600;">
                    <i class="fa-solid fa-star"></i> ${rating} / 5.0 Rating
                </div>
            `;
            listContainer.appendChild(card);
        });

    } catch (err) {}
}

// PAYMENTS PAGE INITIALIZER
async function initPaymentsPage() {
    const bookingId = localStorage.getItem("activeBookingId");
    const paymentForm = document.getElementById("paymentForm");
    const payFareEl = document.getElementById("payFare");
    const payBookingIdEl = document.getElementById("payBookingId");

    if (!bookingId) {
        showToast("No active booking found for payment.", "warning");
        setTimeout(() => {
            window.location.href = "booking.html";
        }, 1500);
        return;
    }

    try {
        const bookings = await apiCall("/bookings/");
        const booking = bookings.find(b => b.booking_id === int(bookingId));

        if (!booking) {
            showToast("Booking not found.", "danger");
            return;
        }

        payFareEl.innerText = `₹${booking.fare}`;
        payBookingIdEl.innerText = `#${booking.booking_id} (${booking.pickup_location} ➜ ${booking.drop_location})`;

        paymentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const method = document.getElementById("paymentMethod").value;
            const user = getCurrentUser();

            const paymentData = {
                booking_id: booking.booking_id,
                customer_name: user.name,
                amount: booking.fare,
                payment_method: method,
                payment_status: "Success",
                transaction_id: "TXN" + Math.floor(Math.random() * 900000000 + 100000000),
                payment_date: new Date().toISOString().split("T")[0]
            };

            try {
                // Post payment
                await apiCall("/payments/add/", "POST", paymentData);
                
                // Update booking status to Accepted/Completed depending on driver assignment
                const nextStatus = booking.driver_name === "Pending" ? "Requested" : "Accepted";
                await apiCall(`/bookings/update/${booking.booking_id}/`, "PUT", {
                    ride_status: nextStatus
                });

                // Set driver status to Busy if driver is assigned
                if (booking.driver_name !== "Pending") {
                    const drivers = await apiCall("/drivers/");
                    const driver = drivers.find(d => d.driver_name === booking.driver_name);
                    if (driver) {
                        await apiCall(`/drivers/update/${driver.driver_id}/`, "PUT", {
                            availability: "Busy"
                        });
                    }
                }

                showToast("Payment Successful!", "success");
                localStorage.removeItem("activeBookingId"); // clear paid booking

                setTimeout(() => {
                    window.location.href = "ride_history.html";
                }, 1500);
            } catch (err) {}
        });

    } catch (err) {}
}

// Helper parsing integer
function int(val) {
    return parseInt(val, 10);
}

// RIDE HISTORY PAGE INITIALIZER
async function initRideHistoryPage() {
    const listBody = document.getElementById("historyList");
    if (!listBody) return;

    const user = getCurrentUser();

    try {
        const bookings = await apiCall("/bookings/");
        const payments = await apiCall("/payments/");

        // Filter bookings by Customer Name or Driver Name depending on current role
        let userBookings = [];
        if (user.role === "customer") {
            userBookings = bookings.filter(b => b.customer_name === user.name);
        } else if (user.role === "driver") {
            userBookings = bookings.filter(b => b.driver_name === user.name);
        } else {
            userBookings = bookings;
        }

        listBody.innerHTML = "";
        if (userBookings.length === 0) {
            listBody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No ride history found.</td></tr>`;
            return;
        }

        userBookings.forEach(b => {
            // Find corresponding payment
            const pay = payments.find(p => p.booking_id === b.booking_id);
            const payStatus = pay ? pay.payment_status : "Pending";
            
            const payBadge = payStatus === "Success" 
                ? `<span class="badge badge-completed">Paid</span>` 
                : `<span class="badge badge-pending">Pending</span>`;

            const rideBadge = b.ride_status === "Requested" 
                ? `<span class="badge badge-requested">Requested</span>`
                : (b.ride_status === "Accepted" 
                    ? `<span class="badge badge-accepted">Accepted</span>` 
                    : (b.ride_status === "In Progress" 
                        ? `<span class="badge badge-inprogress">In Progress</span>` 
                        : (b.ride_status === "Completed" 
                            ? `<span class="badge badge-completed">Completed</span>` 
                            : `<span class="badge badge-cancelled">Cancelled</span>`)));

            let actionHTML = "";
            if (user.role === "customer" && b.ride_status === "Requested") {
                actionHTML = `<button onclick="cancelRide(${b.booking_id})" class="btn-action delete">Cancel</button>`;
            } else if (user.role === "customer" && !pay) {
                actionHTML = `<button onclick="payPendingRide(${b.booking_id})" class="btn-primary" style="padding:0.25rem 0.75rem; font-size:0.8rem; border-radius:6px;">Pay Now</button>`;
            }

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>#${b.booking_id}</td>
                <td>${user.role === "customer" ? b.driver_name : b.customer_name}</td>
                <td>${b.pickup_location} ➜ ${b.drop_location}</td>
                <td>${b.booking_date}</td>
                <td>₹${b.fare}</td>
                <td>${rideBadge}</td>
                <td>${payBadge}</td>
                <td>${actionHTML}</td>
            `;
            listBody.appendChild(tr);
        });

    } catch (err) {}
}

async function cancelRide(id) {
    if (!confirm("Are you sure you want to cancel this ride request?")) return;
    try {
        await apiCall(`/bookings/update/${id}/`, "PUT", { ride_status: "Cancelled" });
        showToast("Ride Cancelled", "success");
        initRideHistoryPage();
    } catch (err) {}
}

function payPendingRide(id) {
    localStorage.setItem("activeBookingId", id);
    window.location.href = "payments.html";
}

// CUSTOMER DASHBOARD INITIALIZER
async function initCustomerDashboard() {
    const user = getCurrentUser();
    const metrics = {
        total: document.getElementById("custTotalRides"),
        completed: document.getElementById("custCompletedRides"),
        upcoming: document.getElementById("custUpcomingRides"),
        history: document.getElementById("custHistoryBody")
    };

    try {
        const bookings = await apiCall("/bookings/");
        const payments = await apiCall("/payments/");

        const userBookings = bookings.filter(b => b.customer_name === user.name);
        const completed = userBookings.filter(b => b.ride_status === "Completed");
        const upcoming = userBookings.filter(b => ["Requested", "Accepted", "In Progress"].includes(b.ride_status));
        const userPayments = payments.filter(p => p.customer_name === user.name);

        metrics.total.innerText = userBookings.length;
        metrics.completed.innerText = completed.length;
        metrics.upcoming.innerText = upcoming.length;

        // Populate recent payment history
        metrics.history.innerHTML = "";
        if (userPayments.length === 0) {
            metrics.history.innerHTML = `<tr><td colspan="5" style="text-align:center;">No transactions found.</td></tr>`;
            return;
        }

        userPayments.slice(0, 5).forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>#${p.payment_id}</td>
                <td>#${p.booking_id}</td>
                <td>₹${p.amount}</td>
                <td>${p.payment_method}</td>
                <td><span class="badge badge-completed">${p.payment_status}</span></td>
            `;
            metrics.history.appendChild(tr);
        });

    } catch (err) {}
}

// DRIVER DASHBOARD INITIALIZER
async function initDriverDashboard() {
    const user = getCurrentUser();
    const dbStatusBtn = document.getElementById("driverStatusToggle");
    const assignedList = document.getElementById("assignedRidesList");
    const totalTripsEl = document.getElementById("drvTotalTrips");
    const earningsEl = document.getElementById("drvEarnings");
    const currentStatusEl = document.getElementById("drvCurrentStatus");

    // Load Driver Info
    try {
        const drivers = await apiCall("/drivers/");
        const driverObj = drivers.find(d => d.driver_name === user.name);

        if (!driverObj) {
            showToast("Driver details not found in database.", "danger");
            return;
        }

        // Display current status details
        currentStatusEl.innerText = driverObj.availability;
        dbStatusBtn.value = driverObj.availability;

        dbStatusBtn.addEventListener("change", async () => {
            const newStatus = dbStatusBtn.value;
            try {
                await apiCall(`/drivers/update/${driverObj.driver_id}/`, "PUT", {
                    availability: newStatus
                });
                showToast(`Status updated to ${newStatus}`, "success");
                currentStatusEl.innerText = newStatus;
            } catch (e) {}
        });

        // Load Driver's Rides & Earnings
        const bookings = await apiCall("/bookings/");
        const driverBookings = bookings.filter(b => b.driver_name === user.name);
        const completed = driverBookings.filter(b => b.ride_status === "Completed");

        totalTripsEl.innerText = completed.length;
        
        // Sum completed bookings fare
        const earnings = completed.reduce((sum, b) => sum + parseFloat(b.fare), 0);
        earningsEl.innerText = `₹${earnings}`;

        // Assigned Active rides
        const activeRides = driverBookings.filter(b => ["Accepted", "In Progress"].includes(b.ride_status));
        
        // Any Requested Ride that has no driver yet
        const unassignedRequests = bookings.filter(b => b.ride_status === "Requested" && b.driver_name === "Pending");

        assignedList.innerHTML = "";
        
        const allAssigned = [...activeRides, ...unassignedRequests];
        if (allAssigned.length === 0) {
            assignedList.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 2rem;">No active ride requests.</td></tr>`;
            return;
        }

        allAssigned.forEach(b => {
            let actions = "";
            if (b.ride_status === "Requested") {
                actions = `<button onclick="updateRideStatus(${b.booking_id}, 'Accepted')" class="btn-primary" style="padding:0.35rem 0.8rem; font-size:0.8rem; border-radius:6px;">Accept Ride</button>`;
            } else if (b.ride_status === "Accepted") {
                actions = `<button onclick="updateRideStatus(${b.booking_id}, 'In Progress')" class="btn-secondary" style="padding:0.35rem 0.8rem; font-size:0.8rem; border-radius:6px; border-color:var(--primary); color:var(--primary)">Start Trip</button>`;
            } else if (b.ride_status === "In Progress") {
                actions = `<button onclick="updateRideStatus(${b.booking_id}, 'Completed')" class="btn-primary" style="padding:0.35rem 0.8rem; font-size:0.8rem; border-radius:6px; background:var(--success); box-shadow:none;">Complete Trip</button>`;
            }

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>#${b.booking_id}</td>
                <td>${b.customer_name}</td>
                <td>${b.pickup_location} ➜ ${b.drop_location}</td>
                <td>₹${b.fare}</td>
                <td><span class="badge badge-${b.ride_status.toLowerCase().replace(" ", "")}">${b.ride_status}</span></td>
                <td>${actions}</td>
            `;
            assignedList.appendChild(tr);
        });

    } catch (err) {}
}

async function updateRideStatus(bookingId, status) {
    const user = getCurrentUser();
    try {
        const updateObj = { ride_status: status };
        if (status === "Accepted") {
            updateObj.driver_name = user.name;
        }

        await apiCall(`/bookings/update/${bookingId}/`, "PUT", updateObj);

        // Update driver availability states
        const drivers = await apiCall("/drivers/");
        const driverObj = drivers.find(d => d.driver_name === user.name);

        if (driverObj) {
            let nextAvail = "Available";
            if (status === "Accepted" || status === "In Progress") {
                nextAvail = "Busy";
            }
            await apiCall(`/drivers/update/${driverObj.driver_id}/`, "PUT", {
                availability: nextAvail
            });
        }

        showToast(`Trip Status: ${status}`, "success");
        initDriverDashboard();
    } catch (err) {}
}

// ----------------------------------------------------
// ADMIN DASHBOARD & MASTER CRUD CONTROLLER
// ----------------------------------------------------
let currentAdminTable = "customers";
let editTargetId = null;

function initAdminDashboard() {
    switchAdminTab("customers");
    initSearchHandler();
    initModalHandlers();
}

function switchAdminTab(tabName) {
    currentAdminTable = tabName;
    document.querySelectorAll(".tab-link").forEach(btn => {
        btn.classList.remove("active");
        if (btn.getAttribute("data-tab") === tabName) btn.classList.add("active");
    });

    // Update section titles and table headers
    const panelTitleText = document.getElementById("adminPanelTitle");
    const tableHeaderRow = document.getElementById("adminTableHeader");

    const headers = {
        customers: `
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Actions</th>
        `,
        drivers: `
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>License</th>
            <th>Experience</th>
            <th>Availability</th>
            <th>Actions</th>
        `,
        vehicles: `
            <th>ID</th>
            <th>Driver Name</th>
            <th>Type</th>
            <th>Plate Number</th>
            <th>Model</th>
            <th>Seats</th>
            <th>Actions</th>
        `,
        bookings: `
            <th>ID</th>
            <th>Customer</th>
            <th>Driver</th>
            <th>Route</th>
            <th>Date</th>
            <th>Fare</th>
            <th>Status</th>
            <th>Actions</th>
        `,
        payments: `
            <th>ID</th>
            <th>Booking ID</th>
            <th>Customer</th>
            <th>Amount</th>
            <th>Method</th>
            <th>Status</th>
            <th>Txn ID</th>
            <th>Date</th>
            <th>Actions</th>
        `
    };

    panelTitleText.innerText = tabName.charAt(0).toUpperCase() + tabName.slice(1) + " Management";
    tableHeaderRow.innerHTML = headers[tabName];
    
    loadAdminData();
}

async function loadAdminData(searchQuery = "") {
    const listBody = document.getElementById("adminTableBody");
    listBody.innerHTML = "";

    try {
        let endpoint = `/${currentAdminTable}/`;
        if (searchQuery) endpoint += `?search=${encodeURIComponent(searchQuery)}`;
        
        const data = await apiCall(endpoint);

        if (data.length === 0) {
            listBody.innerHTML = `<tr><td colspan="10" style="text-align:center;">No records found.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            let rowHTML = "";

            if (currentAdminTable === "customers") {
                rowHTML = `
                    <td>#${item.customer_id}</td>
                    <td>${item.full_name}</td>
                    <td>${item.email}</td>
                    <td>${item.phone}</td>
                    <td>${item.address}</td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="openEditModal(${item.customer_id})" class="btn-action edit">Edit</button>
                            <button onclick="deleteAdminItem(${item.customer_id})" class="btn-action delete">Delete</button>
                        </div>
                    </td>
                `;
            } else if (currentAdminTable === "drivers") {
                const availBadge = item.availability === "Available" 
                    ? `<span class="badge badge-available">Available</span>`
                    : (item.availability === "Busy" 
                        ? `<span class="badge badge-busy">Busy</span>` 
                        : `<span class="badge badge-offline">Offline</span>`);
                rowHTML = `
                    <td>#${item.driver_id}</td>
                    <td>${item.driver_name}</td>
                    <td>${item.email}</td>
                    <td>${item.phone}</td>
                    <td>${item.license_number}</td>
                    <td>${item.experience} yrs</td>
                    <td>${availBadge}</td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="openEditModal(${item.driver_id})" class="btn-action edit">Edit</button>
                            <button onclick="deleteAdminItem(${item.driver_id})" class="btn-action delete">Delete</button>
                        </div>
                    </td>
                `;
            } else if (currentAdminTable === "vehicles") {
                rowHTML = `
                    <td>#${item.vehicle_id}</td>
                    <td>${item.driver_name}</td>
                    <td>${item.vehicle_type}</td>
                    <td>${item.vehicle_number}</td>
                    <td>${item.model}</td>
                    <td>${item.seating_capacity} seats</td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="openEditModal(${item.vehicle_id})" class="btn-action edit">Edit</button>
                            <button onclick="deleteAdminItem(${item.vehicle_id})" class="btn-action delete">Delete</button>
                        </div>
                    </td>
                `;
            } else if (currentAdminTable === "bookings") {
                const rideBadge = `<span class="badge badge-${item.ride_status.toLowerCase().replace(" ", "")}">${item.ride_status}</span>`;
                rowHTML = `
                    <td>#${item.booking_id}</td>
                    <td>${item.customer_name}</td>
                    <td>${item.driver_name}</td>
                    <td>${item.pickup_location} ➜ ${item.drop_location}</td>
                    <td>${item.booking_date}</td>
                    <td>₹${item.fare}</td>
                    <td>${rideBadge}</td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="openEditModal(${item.booking_id})" class="btn-action edit">Edit</button>
                            <button onclick="deleteAdminItem(${item.booking_id})" class="btn-action delete">Delete</button>
                        </div>
                    </td>
                `;
            } else if (currentAdminTable === "payments") {
                const payBadge = item.payment_status === "Success" 
                    ? `<span class="badge badge-completed">Success</span>` 
                    : `<span class="badge badge-pending">${item.payment_status}</span>`;
                rowHTML = `
                    <td>#${item.payment_id}</td>
                    <td>#${item.booking_id}</td>
                    <td>${item.customer_name}</td>
                    <td>₹${item.amount}</td>
                    <td>${item.payment_method}</td>
                    <td>${payBadge}</td>
                    <td>${item.transaction_id || 'N/A'}</td>
                    <td>${item.payment_date}</td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="openEditModal(${item.payment_id})" class="btn-action edit">Edit</button>
                            <button onclick="deleteAdminItem(${item.payment_id})" class="btn-action delete">Delete</button>
                        </div>
                    </td>
                `;
            }

            tr.innerHTML = rowHTML;
            listBody.appendChild(tr);
        });

    } catch (err) {}
}

function initSearchHandler() {
    const searchInput = document.getElementById("adminSearchInput");
    if (!searchInput) return;

    let debounceTimer;
    searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            loadAdminData(e.target.value.trim());
        }, 300);
    });
}

// MODAL POPUPS FOR ADD & EDIT
function initModalHandlers() {
    const modal = document.getElementById("adminModal");
    const closeBtn = document.querySelector(".modal-close");
    const cancelBtn = document.getElementById("modalCancel");
    
    if (closeBtn) closeBtn.onclick = () => modal.style.display = "none";
    if (cancelBtn) cancelBtn.onclick = () => modal.style.display = "none";

    window.onclick = (e) => {
        if (e.target === modal) modal.style.display = "none";
    };

    // Form submit inside modal
    const crudForm = document.getElementById("modalCrudForm");
    if (crudForm) {
        crudForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            // Collect Form Values dynamically
            const payload = {};
            const elements = crudForm.elements;
            for (let i = 0; i < elements.length; i++) {
                const el = elements[i];
                if (el.name) {
                    payload[el.name] = el.value.trim();
                }
            }

            // Convert numbers
            const numberFields = ["experience", "seating_capacity", "fare", "amount", "booking_id", "customer_id", "driver_id", "vehicle_id", "payment_id"];
            numberFields.forEach(f => {
                if (f in payload && payload[f] !== "") {
                    payload[f] = parseFloat(payload[f]);
                }
            });

            try {
                if (editTargetId === null) {
                    // ADD MODE
                    await apiCall(`/${currentAdminTable}/add/`, "POST", payload);
                    showToast("Record added successfully", "success");
                } else {
                    // EDIT MODE
                    await apiCall(`/${currentAdminTable}/update/${editTargetId}/`, "PUT", payload);
                    showToast("Record updated successfully", "success");
                }
                modal.style.display = "none";
                loadAdminData();
            } catch (err) {}
        });
    }
}

// Generate the proper dynamic fields inside the modal form based on the current tab
function setupModalFields(item = null) {
    const formFields = document.getElementById("modalFormFields");
    formFields.innerHTML = "";

    const templates = {
        customers: [
            { label: "Customer ID (Optional)", name: "customer_id", type: "number", placeholder: "e.g. 101" },
            { label: "Full Name", name: "full_name", type: "text", required: true },
            { label: "Email", name: "email", type: "email", required: true },
            { label: "Phone", name: "phone", type: "text" },
            { label: "Address", name: "address", type: "text" },
            { label: "Password", name: "password", type: "password", required: true }
        ],
        drivers: [
            { label: "Driver ID (Optional)", name: "driver_id", type: "number", placeholder: "e.g. 201" },
            { label: "Driver Name", name: "driver_name", type: "text", required: true },
            { label: "Email", name: "email", type: "email", required: true },
            { label: "Phone", name: "phone", type: "text" },
            { label: "License Number", name: "license_number", type: "text", required: true },
            { label: "Experience (Years)", name: "experience", type: "number" },
            { label: "Availability", name: "availability", type: "select", options: ["Available", "Busy", "Offline"] }
        ],
        vehicles: [
            { label: "Vehicle ID (Optional)", name: "vehicle_id", type: "number", placeholder: "e.g. 301" },
            { label: "Driver Name", name: "driver_name", type: "text", required: true },
            { label: "Vehicle Type", name: "vehicle_type", type: "select", options: ["Sedan", "Hatchback", "SUV", "Auto", "Bike", "Luxury"] },
            { label: "Plate Number", name: "vehicle_number", type: "text", required: true },
            { label: "Model Description", name: "model", type: "text" },
            { label: "Seating Capacity", name: "seating_capacity", type: "number", val: 4 }
        ],
        bookings: [
            { label: "Booking ID (Optional)", name: "booking_id", type: "number", placeholder: "e.g. 401" },
            { label: "Customer Name", name: "customer_name", type: "text", required: true },
            { label: "Driver Name", name: "driver_name", type: "text" },
            { label: "Pickup Location", name: "pickup_location", type: "text", required: true },
            { label: "Drop Location", name: "drop_location", type: "text", required: true },
            { label: "Booking Date", name: "booking_date", type: "date", required: true },
            { label: "Fare Amount (₹)", name: "fare", type: "number", required: true },
            { label: "Ride Status", name: "ride_status", type: "select", options: ["Requested", "Accepted", "In Progress", "Completed", "Cancelled"] }
        ],
        payments: [
            { label: "Payment ID (Optional)", name: "payment_id", type: "number", placeholder: "e.g. 501" },
            { label: "Booking ID", name: "booking_id", type: "number", required: true },
            { label: "Customer Name", name: "customer_name", type: "text", required: true },
            { label: "Amount Paid (₹)", name: "amount", type: "number", required: true },
            { label: "Payment Method", name: "payment_method", type: "select", options: ["UPI", "Credit Card", "Debit Card", "Wallet", "Cash"] },
            { label: "Payment Status", name: "payment_status", type: "select", options: ["Success", "Pending", "Failed"] },
            { label: "Transaction ID", name: "transaction_id", type: "text" },
            { label: "Payment Date", name: "payment_date", type: "date" }
        ]
    };

    const fields = templates[currentAdminTable];
    fields.forEach(f => {
        const group = document.createElement("div");
        group.className = "form-group";
        
        const label = document.createElement("label");
        label.className = "form-label";
        label.innerText = f.label;
        group.appendChild(label);

        let value = item ? item[f.name] : (f.val !== undefined ? f.val : "");
        
        // Format dates for input type date
        if (item && f.type === "date" && value) {
            value = value.split("T")[0]; 
        }

        if (f.type === "select") {
            const select = document.createElement("select");
            select.name = f.name;
            select.className = "form-select";
            if (f.required) select.required = true;
            
            f.options.forEach(opt => {
                const o = document.createElement("option");
                o.value = opt;
                o.innerText = opt;
                if (value === opt) o.selected = true;
                select.appendChild(o);
            });
            group.appendChild(select);
        } else {
            const input = document.createElement("input");
            input.name = f.name;
            input.type = f.type;
            input.className = "form-input";
            input.placeholder = f.placeholder || "";
            if (f.required) input.required = true;
            input.value = value;
            
            // If in edit mode, hide ID field because IDs cannot be edited
            if (item && f.name.endsWith("_id")) {
                input.readOnly = true;
                input.style.opacity = "0.6";
            }

            group.appendChild(input);
        }
        formFields.appendChild(group);
    });
}

function openAddModal() {
    editTargetId = null;
    const title = document.getElementById("modalTitle");
    title.innerText = `Add New ${currentAdminTable.slice(0, -1)}`;
    setupModalFields();
    document.getElementById("adminModal").style.display = "flex";
}

async function openEditModal(id) {
    editTargetId = id;
    const title = document.getElementById("modalTitle");
    title.innerText = `Edit ${currentAdminTable.slice(0, -1)} #${id}`;

    try {
        const data = await apiCall(`/${currentAdminTable}/`);
        const targetField = `${currentAdminTable.slice(0, -1)}_id`;
        const item = data.find(i => i[targetField] === id);

        if (!item) {
            showToast("Item details not found", "danger");
            return;
        }

        setupModalFields(item);
        document.getElementById("adminModal").style.display = "flex";
    } catch (err) {}
}

async function deleteAdminItem(id) {
    if (!confirm(`Are you sure you want to delete this ${currentAdminTable.slice(0, -1)}?`)) return;
    try {
        await apiCall(`/${currentAdminTable}/delete/${id}/`, "DELETE");
        showToast("Record deleted", "success");
        loadAdminData();
    } catch (err) {}
}
