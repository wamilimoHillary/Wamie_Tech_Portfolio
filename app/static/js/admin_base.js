document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const menuBtn = document.getElementById("Hamburger-menu-btn");
    const closeBtn = document.getElementById("close-btn");
    const links = document.querySelectorAll("#sidebar a");

    // Toggle sidebar when hamburger is clicked
    menuBtn.addEventListener("click", function () {
        sidebar.classList.toggle("active");
    });

    // Close sidebar when X button is clicked
    closeBtn.addEventListener("click", function () {
        sidebar.classList.remove("active");
    });

   // Close sidebar when clicking outside (mobile only)
document.addEventListener("click", function (e) {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && e.target !== menuBtn) {
            sidebar.classList.remove("active");
        }
    }
});

});
