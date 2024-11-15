/*
	Miniport by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

function initMap() {
  var map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 53.4808, lng: -2.2426 }, // Center the map over the UK
    zoom: 6,
  });
  // Add more map functionality here as needed
}

(function ($) {
  var $window = $(window),
    $body = $('body'),
    $nav = $('#nav');

  // Breakpoints.
  breakpoints({
    xlarge: ['1281px', '1680px'],
    large: ['981px', '1280px'],
    medium: ['737px', '980px'],
    small: [null, '736px'],
  });

  // Play initial animations on page load.
  $window.on('load', function () {
    window.setTimeout(function () {
      $body.removeClass('is-preload');
    }, 100);
  });

  // Scrolly.
  $('#nav a, .scrolly').scrolly({
    speed: 1000,
    offset: function () {
      return $nav.height();
    },
  });
})(jQuery);
