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
    d.style.background = j === i ? '#C2456E' : 'rgba(255,255,255,.1)';
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

/* Preselect the booth on the quote form from ?booth=open-air|enclosed|360|glam */
(function(){try{var b=new URLSearchParams(window.location.search).get('booth');var s=document.getElementById('booth');
if(b&&s){for(var i=0;i<s.options.length;i++){if(s.options[i].value===b){s.selectedIndex=i;break;}}}}catch(e){}})();

/* Quote form: number the request (1, 2, 3...), send in the background, show a thank-you message */
(function(){var f=document.querySelector('form.si-form');if(!f)return;
var COUNTER='https://abacus.jasoncameron.dev/hit/siphotoboothatl/quotes';
function fallback(){var n=new Date(),z=function(x){return ('0'+x).slice(-2);};return 'SI-'+z(n.getMonth()+1)+z(n.getDate())+z(n.getHours())+z(n.getMinutes());}
function nextNumber(){var c=new AbortController();var t=setTimeout(function(){c.abort();},6000);
return fetch(COUNTER,{signal:c.signal}).then(function(r){return r.json();}).then(function(d){clearTimeout(t);return (d&&d.value)?'SI-'+d.value:fallback();}).catch(function(){clearTimeout(t);return fallback();});}
f.addEventListener('submit',function(e){e.preventDefault();var b=f.querySelector('.si-form-btn');b.disabled=true;b.textContent='Sending...';
var g=function(n){var el=f.elements[n];return el?el.value.trim():'';};
var d=g('event_date');if(d){var q=d.split('-');if(q.length===3)d=q[1]+'/'+q[2]+'/'+q[0];}
nextNumber().then(function(num){
var h=f.elements['quote_number'];if(!h){h=document.createElement('input');h.type='hidden';h.name='quote_number';f.appendChild(h);}h.value=num;
(function(){var BOOK_PATH='/preview-book/';var ss=document.querySelector('link[rel=stylesheet][href*="assets/main.css"]');var base=ss?ss.getAttribute('href').split('/assets/')[0]:'';
var bk=g('booth');var parts=[['q',num],['name',g('name')],['email',g('email')],['phone',g('phone')],['event_date',g('event_date')],['event_type',g('event_type')],['venue',g('venue')],['city',g('city')],['zip',g('zip')]];
if(bk&&bk!=='unsure')parts.push(['booth',bk]);
var qs=parts.filter(function(x){return x[1];}).map(function(x){return x[0]+'='+encodeURIComponent(x[1]);}).join('&');
var l=f.elements['booking_link'];if(!l){l=document.createElement('input');l.type='hidden';l.name='booking_link';f.appendChild(l);}
l.value=location.origin+base+BOOK_PATH+'#'+qs;})();
f.elements['_subject'].value='Quote #'+num+' | '+(d||'No date yet')+' | '+g('city')+' '+g('zip');
var u=f.getAttribute('action').replace('formsubmit.co/','formsubmit.co/ajax/');
return fetch(u,{method:'POST',body:new FormData(f),headers:{'Accept':'application/json'}});
}).then(function(r){return r.json();}).then(function(d2){
if(d2&&(d2.success===true||d2.success==='true')){var lt=f.classList.contains('qf');f.innerHTML='<div style="text-align:center;padding:48px 16px;"><h3 style="font-family:var(--fd);font-size:28px;color:'+(lt?'#8E2B4D':'#F0EBE1')+';margin:0 0 12px;">Thank you!</h3><p style="color:'+(lt?'#6E5A62':'rgba(255,255,255,.6)')+';line-height:1.8;margin:0;">We received your request and will get back to you shortly. Your quote number is in the email we send you.</p></div>';if(lt){f.scrollIntoView({behavior:'smooth',block:'center'});}}else{throw new Error('x');}
}).catch(function(){b.disabled=false;b.textContent='Get My Free Quote';alert('Sorry, something went wrong. Please call or text (943) 255-2632.');});});})();

/* Event date: open the calendar when the field is clicked anywhere */
(function(){document.querySelectorAll('input[type=date]').forEach(function(el){
var open=function(){try{if(el.showPicker)el.showPicker();}catch(e){}};
el.addEventListener('click',open);el.addEventListener('focus',open);});})();

/* quote form: collect add-on checkboxes into one field */
(function(){var h=document.getElementById('addons-val');if(!h)return;var bs=document.querySelectorAll('.qa');
function up(){var v=[];bs.forEach(function(b){if(b.checked)v.push(b.value);});h.value=v.join(', ');}
bs.forEach(function(b){b.addEventListener('change',up);});})();
