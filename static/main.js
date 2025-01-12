// Confirmation before approving or rejecting publishing requests
document.addEventListener("DOMContentLoaded", function () {
    const approveButtons = document.querySelectorAll("form[action*='approve_request'] button");
    const rejectButtons = document.querySelectorAll("form[action*='reject_request'] button");

    approveButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            const confirmApprove = confirm("Are you sure you want to approve this publishing request?");
            if (!confirmApprove) {
                event.preventDefault();
            }
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            const confirmReject = confirm("Are you sure you want to reject this publishing request?");
            if (!confirmReject) {
                event.preventDefault();
            }
        });
    });
});

// Client-side form validation (example for registration form)
const registrationForm = document.querySelector("form[action*='register']");
if (registrationForm) {
    registrationForm.addEventListener("submit", function (event) {
        const password = document.getElementById("password").value;
        if (password.length < 6) {
            alert("Password must be at least 6 characters long.");
            event.preventDefault();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const menuButtons = document.querySelectorAll(".menu-button");

    menuButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.stopPropagation();

            // Close other menus
            document.querySelectorAll(".menu-container").forEach((menu) => {
                if (menu !== button.parentElement) {
                    menu.classList.remove("active");
                }
            });

            // Toggle the current menu
            button.parentElement.classList.toggle("active");
        });
    });

    // Close menu when clicking elsewhere
    document.addEventListener("click", () => {
        document.querySelectorAll(".menu-container").forEach((menu) => {
            menu.classList.remove("active");
        });
    });
});
