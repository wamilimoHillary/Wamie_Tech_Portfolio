"use strict";

document.addEventListener("DOMContentLoaded", function () {
  var sidebar = document.getElementById("sidebar");
  var menuBtn = document.getElementById("Hamburger-menu-btn");
  var closeBtn = document.getElementById("close-btn");
  var links = document.querySelectorAll("#sidebar a"); // Toggle sidebar when hamburger is clicked

  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("active");
  }); // Close sidebar when X button is clicked

  closeBtn.addEventListener("click", function () {
    sidebar.classList.remove("active");
  }); // Close sidebar when clicking outside (mobile only)

  document.addEventListener("click", function (e) {
    if (window.innerWidth <= 768) {
      if (!sidebar.contains(e.target) && e.target !== menuBtn) {
        sidebar.classList.remove("active");
      }
    }
  });
});
//# sourceMappingURL=admin_base.dev.js.map
