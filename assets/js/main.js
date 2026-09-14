/* Columbia Animal Hospital — progressive enhancement only.
   Every section of this site renders and works with this file absent. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Behavior bound to the page shell — attached exactly once. */
  function bindShell() {
  /* ---- mobile navigation ------------------------------------------------ */
  var toggle = document.querySelector('[data-nav-toggle]');
  var panel = document.querySelector('[data-nav-panel]');

  if (toggle && panel) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      panel.setAttribute('data-open', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    };
    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    panel.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });
    // A resize past the desktop breakpoint must not leave the body locked.
    window.matchMedia('(min-width: 62rem)').addEventListener('change', function (e) {
      if (e.matches) setOpen(false);
    });
  }

  /* ---- header shadow on scroll ------------------------------------------ */
  var header = document.querySelector('[data-header]');
  if (header) {
    var onScroll = function () {
      header.setAttribute('data-scrolled', String(window.scrollY > 8));
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  }

  /* Behavior bound to page content. Runs on load, and again whenever the
     single-file preview swaps one page's <main> for another's. */
  function bindContent() {
  /* ---- scroll reveal ----------------------------------------------------
     The .reveal class starts at opacity 0. If this observer never runs the
     stylesheet's html:not(.js) rule keeps everything visible, so a failure
     here cannot blank the page. */
  var reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    if (reduced || !('IntersectionObserver' in window)) {
      reveals.forEach(function (el) { el.classList.add('is-in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      reveals.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---- open / closed indicator -----------------------------------------
     Computed in the hospital's timezone, not the visitor's, so someone
     checking from another state sees the truth. Minutes from midnight. */
  var SCHEDULE = {
    0: null,              // Sunday — closed
    1: [450, 1050],       // Mon–Fri  7:30 AM – 5:30 PM
    2: [450, 1050],
    3: [450, 1050],
    4: [450, 1050],
    5: [450, 1050],
    6: [480, 720]         // Saturday 8:00 AM – 12:00 PM
  };
  var DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function clinicNow() {
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Chicago',
      weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
    }).formatToParts(new Date());
    var get = function (type) {
      var p = parts.find(function (x) { return x.type === type; });
      return p ? p.value : '';
    };
    var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    var hour = parseInt(get('hour'), 10);
    if (hour === 24) hour = 0;
    return { day: days[get('weekday')], minutes: hour * 60 + parseInt(get('minute'), 10) };
  }

  function nextOpening(day) {
    for (var i = 1; i <= 7; i++) {
      var d = (day + i) % 7;
      if (SCHEDULE[d]) {
        return { label: i === 1 ? 'tomorrow' : DAY_NAMES[d], window: SCHEDULE[d] };
      }
    }
    return null;
  }

  function minutesToLabel(m) {
    var h = Math.floor(m / 60), mm = m % 60;
    var suffix = h >= 12 ? 'PM' : 'AM';
    var h12 = h % 12 === 0 ? 12 : h % 12;
    return h12 + (mm ? ':' + String(mm).padStart(2, '0') : ':00') + ' ' + suffix;
  }

  var status = document.querySelector('[data-status]');
  if (status && window.Intl && Intl.DateTimeFormat) {
    try {
      var now = clinicNow();
      var today = SCHEDULE[now.day];
      var label = status.querySelector('[data-status-label]');
      var open = today && now.minutes >= today[0] && now.minutes < today[1];

      status.setAttribute('data-state', open ? 'open' : 'closed');
      if (open) {
        label.textContent = 'Open now · until ' + minutesToLabel(today[1]);
      } else if (today && now.minutes < today[0]) {
        label.textContent = 'Closed · opens today at ' + minutesToLabel(today[0]);
      } else {
        var next = nextOpening(now.day);
        label.textContent = next
          ? 'Closed · opens ' + next.label + ' at ' + minutesToLabel(next.window[0])
          : 'Closed';
      }

      // Mark today's row in any hours list on the page.
      document.querySelectorAll('[data-day]').forEach(function (row) {
        var days = row.getAttribute('data-day').split(',').map(Number);
        if (days.indexOf(now.day) !== -1) row.setAttribute('data-today', 'true');
      });
    } catch (e) {
      /* Leave the server-rendered "Hours" text in place. */
    }
  }

  /* ---- defer the map until it is near the viewport ---------------------- */
  var map = document.querySelector('[data-map]');
  if (map && 'IntersectionObserver' in window) {
    var mapObserver = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var frame = document.createElement('iframe');
        frame.src = map.getAttribute('data-map');
        frame.title = 'Map showing Columbia Animal Hospital at 1409 Hwy 98E, Columbia, Mississippi';
        frame.loading = 'lazy';
        frame.referrerPolicy = 'no-referrer-when-downgrade';
        frame.setAttribute('allowfullscreen', '');
        map.textContent = '';
        map.appendChild(frame);
        obs.disconnect();
      });
    }, { rootMargin: '400px' });
    mapObserver.observe(map);
  }
  }

  bindShell();
  bindContent();
  window.__cahInit = bindContent;
})();
