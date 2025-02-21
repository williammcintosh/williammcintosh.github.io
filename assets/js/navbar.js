document.addEventListener('DOMContentLoaded', function () {
  console.log('DOM fully loaded and parsed');

  // Load Navbar HTML before running any dropdown logic
  fetch('/navbar.html')
    .then((response) => response.text())
    .then((data) => {
      let navbarContainer = document.getElementById('navbar');
      if (navbarContainer) {
        navbarContainer.innerHTML = data;
        console.log('Navbar loaded successfully');

        // Now that the navbar is loaded, initialize dropdown functionality
        attachDropdownListeners();
        setupHamburgerMenu();
      } else {
        console.error('Navbar container not found.');
      }
    })
    .catch((error) => console.error('Error loading navbar:', error));
});

// Function to initialize dropdown event listeners
function attachDropdownListeners() {
  console.log('Attaching event listeners to dropdowns...');

  document.querySelectorAll('.dropdown > a').forEach(function (dropdownToggle) {
    console.log('Adding click event to:', dropdownToggle.textContent.trim());

    dropdownToggle.addEventListener('click', function (event) {
      event.preventDefault(); // Prevents jumping to top
      let dropdownContent = this.nextElementSibling;

      console.log('Toggling dropdown:', dropdownContent);

      // Close all other dropdowns first
      document.querySelectorAll('.dropdown-content').forEach((dropdown) => {
        if (dropdown !== dropdownContent) {
          dropdown.classList.remove('active'); // Hide other dropdowns
          console.log('Hiding:', dropdown);
        }
      });

      // Toggle active class on clicked dropdown
      dropdownContent.classList.toggle('active');
      console.log(
        'Dropdown now:',
        dropdownContent.classList.contains('active') ? 'OPEN' : 'CLOSED'
      );
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function (event) {
    if (!event.target.closest('.dropdown')) {
      document.querySelectorAll('.dropdown-content').forEach((dropdown) => {
        dropdown.classList.remove('active');
      });
    }
  });
  // console.log('Dropdown event listeners attached.');
}

function setupHamburgerMenu() {
  console.log('Setting up hamburger menu...');

  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.querySelector('nav#nav ul.container');

  if (!navToggle) {
    console.error('Hamburger menu button (#nav-toggle) not found.');
    return;
  }

  if (!navMenu) {
    console.error('Navbar menu (ul.container) not found.');
    return;
  }

  navToggle.addEventListener('click', function () {
    console.log('Hamburger menu clicked!');
    navMenu.classList.toggle('nav-menu-visible');
  });

  // Close menu if user clicks outside it
  document.addEventListener('click', function (event) {
    if (
      !event.target.closest('#nav-toggle') &&
      !event.target.closest('nav#nav')
    ) {
      navMenu.classList.remove('nav-menu-visible');
    }
  });

  console.log('Hamburger menu setup complete.');
}
