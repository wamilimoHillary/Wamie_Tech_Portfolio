// ── Sidebar ────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const menuBtn = document.querySelector(".menu-btn");
    const links   = document.querySelectorAll("#sidebar a");

    menuBtn.addEventListener("click", function () {
        sidebar.classList.toggle("active");
    });

    links.forEach(link => {
        link.addEventListener("click", function () {
            links.forEach(l => l.classList.remove("active"));
            this.classList.add("active");
        });
    });
});

// ── Dark Mode ───────────────────────────────────────────────
const toggleSwitch = document.getElementById('toggle-dark-mode');

if (localStorage.getItem('dark-mode') === 'enabled') {
    document.body.classList.add('dark-mode');
    toggleSwitch.checked = true;
} else {
    document.body.classList.remove('dark-mode');
    toggleSwitch.checked = false;
}

toggleSwitch.addEventListener('change', () => {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('dark-mode', 'enabled');
    } else {
        localStorage.setItem('dark-mode', 'disabled');
    }
});

// ── Modals + Coffee STK feedback ───────────────────────────
document.addEventListener("DOMContentLoaded", () => {

    // Open Hire Me Modal
    document.querySelector(".hire-me").addEventListener("click", e => {
        e.preventDefault();
        document.getElementById("hireModal").style.display = "block";
    });

    // Open Coffee Modal
    document.querySelector(".buy_me_coffee").addEventListener("click", e => {
        e.preventDefault();
        document.getElementById("coffeeModal").style.display = "block";
    });

    // Close modals on × button
    document.querySelectorAll(".close-btn").forEach(btn => {
        btn.addEventListener("click", e => {
            const modalId = e.target.dataset.modal;
            document.getElementById(modalId).style.display = "none";
        });
    });

    // Close modal when clicking outside
    window.addEventListener("click", e => {
        document.querySelectorAll(".modal").forEach(modal => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });
    });

    // ── Coffee STK Push feedback ────────────────────────────
    const coffeeForm   = document.getElementById('coffee-form');
    const coffeeBtn    = document.getElementById('coffee-pay-btn');
    const coffeeStatus = document.getElementById('coffee-status');

    if (coffeeForm) {
        coffeeForm.addEventListener('submit', function (e) {
            e.preventDefault(); // stop instant submit

            const phone  = document.getElementById('mpesa-number').value.trim();
            const amount = document.getElementById('amount').value.trim();

            if (!phone || !amount) return;

            // Show alert inside modal immediately
            coffeeStatus.style.display    = 'block';
            coffeeStatus.style.background = 'rgba(0, 255, 13, 0.33)';
            coffeeStatus.style.border     = '1px solid #00aeff';
            coffeeStatus.style.color      = '#000000';
            coffeeStatus.innerHTML        = '⏳ Sending STK Push...<br><strong>📱 Check your phone and enter your M-Pesa PIN!</strong>';

            // Disable button to prevent double submit
            coffeeBtn.disabled  = true;
            coffeeBtn.innerHTML = '⏳ Processing...';

            // Submit after 1.5s so user sees the message
            setTimeout(() => {
                coffeeForm.submit();
            }, 1500);
        });
    }

});

// ── Close Sidebar ───────────────────────────────────────────
document.querySelector("#sidebar .close-sidebar").addEventListener("click", function () {
    document.getElementById("sidebar").classList.remove("active");
});

// ── Admin secret tap (4 taps to reveal) ────────────────────
document.addEventListener("DOMContentLoaded", () => {
    let tapCount = 0;
    const adminButton   = document.getElementById("hidden_admin_function");
    const adminLoginUrl = adminButton.getAttribute('data-url');

    adminButton.addEventListener("click", (event) => {
        event.preventDefault();
        tapCount++;

        if (tapCount === 4) {
            window.location.href = adminLoginUrl;
        }

        setTimeout(() => { tapCount = 0; }, 2000);
    });
});