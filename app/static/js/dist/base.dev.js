"use strict";

// ── Sidebar ────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
  var sidebar = document.getElementById("sidebar");
  var menuBtn = document.querySelector(".menu-btn");
  var links = document.querySelectorAll("#sidebar a");
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("active");
  });
  links.forEach(function (link) {
    link.addEventListener("click", function () {
      links.forEach(function (l) {
        return l.classList.remove("active");
      });
      this.classList.add("active");
    });
  });
}); // ── Dark Mode ───────────────────────────────────────────────

var toggleSwitch = document.getElementById('toggle-dark-mode');

if (localStorage.getItem('dark-mode') === 'enabled') {
  document.body.classList.add('dark-mode');
  toggleSwitch.checked = true;
} else {
  document.body.classList.remove('dark-mode');
  toggleSwitch.checked = false;
}

toggleSwitch.addEventListener('change', function () {
  document.body.classList.toggle('dark-mode');

  if (document.body.classList.contains('dark-mode')) {
    localStorage.setItem('dark-mode', 'enabled');
  } else {
    localStorage.setItem('dark-mode', 'disabled');
  }
}); // ── Modals + Coffee STK feedback ───────────────────────────

document.addEventListener("DOMContentLoaded", function () {
  // Open Hire Me Modal
  document.querySelector(".hire-me").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("hireModal").style.display = "block";
  }); // Open Coffee Modal

  document.querySelector(".buy_me_coffee").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("coffeeModal").style.display = "block";
  }); // Close modals on × button

  document.querySelectorAll(".close-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var modalId = e.target.dataset.modal;
      document.getElementById(modalId).style.display = "none";
    });
  }); // Close modal when clicking outside

  window.addEventListener("click", function (e) {
    document.querySelectorAll(".modal").forEach(function (modal) {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });
  }); // ── Coffee STK Push feedback ────────────────────────────

  var coffeeForm = document.getElementById('coffee-form');
  var coffeeBtn = document.getElementById('coffee-pay-btn');
  var coffeeStatus = document.getElementById('coffee-status');

  if (coffeeForm) {
    coffeeForm.addEventListener('submit', function (e) {
      e.preventDefault(); // stop instant submit

      var phone = document.getElementById('mpesa-number').value.trim();
      var amount = document.getElementById('amount').value.trim();
      if (!phone || !amount) return; // Show alert inside modal immediately

      coffeeStatus.style.display = 'block';
      coffeeStatus.style.background = 'rgba(0, 255, 13, 0.33)';
      coffeeStatus.style.border = '1px solid #00aeff';
      coffeeStatus.style.color = '#000000';
      coffeeStatus.innerHTML = '⏳ Sending STK Push...<br><strong>📱 Check your phone and enter your M-Pesa PIN!</strong>'; // Disable button to prevent double submit

      coffeeBtn.disabled = true;
      coffeeBtn.innerHTML = '⏳ Processing...'; // Submit after 1.5s so user sees the message

      setTimeout(function () {
        coffeeForm.submit();
      }, 1500);
    });
  }
}); // ── Close Sidebar ───────────────────────────────────────────

document.querySelector("#sidebar .close-sidebar").addEventListener("click", function () {
  document.getElementById("sidebar").classList.remove("active");
}); // ── Admin secret tap (4 taps to reveal) ────────────────────

document.addEventListener("DOMContentLoaded", function () {
  var tapCount = 0;
  var adminButton = document.getElementById("hidden_admin_function");
  var adminLoginUrl = adminButton.getAttribute('data-url');
  adminButton.addEventListener("click", function (event) {
    event.preventDefault();
    tapCount++;

    if (tapCount === 4) {
      window.location.href = adminLoginUrl;
    }

    setTimeout(function () {
      tapCount = 0;
    }, 2000);
  });
});
//# sourceMappingURL=base.dev.js.map
