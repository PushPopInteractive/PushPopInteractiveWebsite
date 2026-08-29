// Returnity site — small progressive enhancements. No dependencies.
(function () {
  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('nav.primary');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Mark the current page in the navigation
  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav.primary a').forEach(function (a) {
    var target = a.getAttribute('href');
    if (target === here || (here === 'index.html' && target === './')) {
      a.setAttribute('aria-current', 'page');
    }
  });
})();
