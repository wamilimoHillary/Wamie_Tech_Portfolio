"use strict";

document.addEventListener("DOMContentLoaded", function () {
  var sidebar = document.getElementById("sidebar");
  var menuBtn = document.querySelector(".menu-btn");
  var links = document.querySelectorAll("#sidebar a"); // Toggle sidebar

  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("active");
  }); // Remove 'active' class from all links, then add to clicked link

  links.forEach(function (link) {
    link.addEventListener("click", function () {
      links.forEach(function (l) {
        return l.classList.remove("active");
      }); // Remove from others

      this.classList.add("active"); // Add to clicked link
    });
  });
});
var toggleSwitch = document.getElementById('toggle-dark-mode'); // Check if dark mode was previously enabled and apply it

if (localStorage.getItem('dark-mode') === 'enabled') {
  document.body.classList.add('dark-mode');
  toggleSwitch.checked = true; // Set the checkbox to checked if dark mode is enabled
} else {
  document.body.classList.remove('dark-mode');
  toggleSwitch.checked = false; // Set the checkbox to unchecked if dark mode is disabled
} // Add event listener to toggle dark mode


toggleSwitch.addEventListener('change', function () {
  document.body.classList.toggle('dark-mode'); // Save the current state of dark mode in localStorage

  if (document.body.classList.contains('dark-mode')) {
    localStorage.setItem('dark-mode', 'enabled');
  } else {
    localStorage.setItem('dark-mode', 'disabled');
  }
});
document.addEventListener("DOMContentLoaded", function () {
  // Open Hire Me Modal
  document.querySelector(".hire-me").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("hireModal").style.display = "block";
  }); // Open Coffee Modal

  document.querySelector(".buy_me_coffee").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("coffeeModal").style.display = "block";
  }); // Close modals on &times;

  document.querySelectorAll(".close-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var modalId = e.target.dataset.modal;
      document.getElementById(modalId).style.display = "none";
    });
  }); // Optional: Close modal when clicking outside

  window.addEventListener("click", function (e) {
    document.querySelectorAll(".modal").forEach(function (modal) {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });
  });
}); // Close sidebar only when × is clicked

document.querySelector("#sidebar .close-sidebar").addEventListener("click", function () {
  document.getElementById("sidebar").classList.remove("active");
}); //Security functionality to display yhe admin login form
// Admin dashboard link functionality hide the admin form 

document.addEventListener("DOMContentLoaded", function () {
  var tapCount = 0; // Get the admin button and its data-url attribute

  var adminButton = document.getElementById("hidden_admin_function");
  var adminLoginUrl = adminButton.getAttribute('data-url'); // Get the URL from the data attribute

  adminButton.addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default link behavior

    tapCount++;

    if (tapCount === 4) {
      // Redirect to the admin login page using the Flask-generated URL
      window.location.href = adminLoginUrl;
    } // Reset the tap count after 2 seconds of inactivity


    setTimeout(function () {
      tapCount = 0;
    }, 2000);
  });
});
//# sourceMappingURL=base.dev.js.map
