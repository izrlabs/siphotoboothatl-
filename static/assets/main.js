// SI Photo Booth - Main JavaScript

// Sticky nav
window.addEventListener('scroll', function() {
  document.getElementById('si-nav').classList.toggle('scrolled', window.scrollY > 50);
});

// Active nav link
(function() {
  var path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(function(link) {
    var href = link.getAttribute('href');
    if (href && path.includes(href.replace(/.*\//, '').replace('/', ''))) {
      link.classList.add('active');
    }
    if ((path === '/' || path === '') && link.dataset.home) {
      link.classList.add('active');
    }
  });
})();

// Testimonial slider
var tests = [
  {t: "Absolutely magical. Our guests are STILL talking about the photo booth months later. The prints were stunning quality and every detail was perfect.", n: "Sarah & Michael", e: "Wedding Reception · Ritz-Carlton"},
  {t: "Professional, seamless, and our branding looked incredible. The social sharing feature drove massive engagement — best investment of the night.", n: "TechVentures Inc.", e: "Annual Gala · Four Seasons"},
  {t: "Made our daughter's celebration unforgettable. The props, the backdrops, the attendants — everything was absolutely perfect.", n: "The Castillo Family", e: "Quinceañera · Private Estate"},
  {t: "We booked the 360° booth and it was the highlight of our 25th anniversary. Every guest left with amazing videos.", n: "Jennifer & David", e: "Anniversary Party · Ponce City Market"}
];
var ti = 0;
function setTest(i) {
  ti = i;
  var tt = document.getElementById('t-text');
  var tn = document.getElementById('t-name');
  var te = document.getElementById('t-event');
  if (tt) tt.textContent = tests[i].t;
  if (tn) tn.textContent = tests[i].n;
  if (te) te.textContent = tests[i].e;
  document.querySelectorAll('.test-dot').forEach(function(d, j) {
    d.style.width = j === i ? '28px' : '7px';
    d.style.background = j === i ? '#C9A96E' : 'rgba(255,255,255,.1)';
  });
}
if (document.querySelector('.test-dot')) {
  setInterval(function() { setTest((ti + 1) % tests.length); }, 5500);
}

// Gallery filter
function filterGallery(cat, btn) {
  document.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
  document.querySelectorAll('.gal-item').forEach(function(item) {
    item.style.display = (cat === 'all' || item.dataset.cat === cat) ? '' : 'none';
  });
}

// Lightbox
function openLb(src, title, loc) {
  document.getElementById('lb-img').src = src;
  document.getElementById('lb-title').textContent = title;
  document.getElementById('lb-loc').textContent = loc;
  document.getElementById('si-lightbox').classList.add('open');
}
function closeLb() {
  document.getElementById('si-lightbox').classList.remove('open');
}
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeLb();
});

// FAQ
function toggleFaq(i) {
  var ans = document.getElementById('fa' + i);
  var icon = document.getElementById('fi' + i);
  var isOpen = ans && ans.classList.contains('open');
  document.querySelectorAll('.faq-ans').forEach(function(a) { a.classList.remove('open'); });
  document.querySelectorAll('.faq-icon').forEach(function(ic) { ic.classList.remove('open'); });
  if (!isOpen && ans) {
    ans.classList.add('open');
    icon.classList.add('open');
  }
}

// Fade in on scroll
var fadeEls = document.querySelectorAll('.fade-in');
if (fadeEls.length && 'IntersectionObserver' in window) {
  var obs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  fadeEls.forEach(function(el) { obs.observe(el); });
}
