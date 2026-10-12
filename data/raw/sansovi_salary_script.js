
/* ══════════════════════════════════════════════════════════════
   SALARY BENCHMARK — API-DRIVEN SCRIPT
   Drop this entire <script> block in place of the old one.
   All static benchmarkData is removed; every update hits the API.
══════════════════════════════════════════════════════════════ */

/* ── Nav scroll ── */
(function(){
  var nav = document.getElementById('nav');
  if(nav) window.addEventListener('scroll', function(){
    nav.classList.toggle('scrolled', window.scrollY > 40);
  });
})();

/* ══════════════════════════════════
   CONSTANTS & MAPPINGS
══════════════════════════════════ */
var API_BASE = 'https://sansovi-gcc-platform-492263949881.asia-south1.run.app/api/v1/intelligence/salary-benchmark';

/* Map <select> values → API param strings */
var ROLE_MAP = {
  'data-engineer'  : 'data-engineer',
  'ml-engineer'    : 'ml-engineer',
  'swe'            : 'swe',
  'cloud-devops'   : 'cloud-devops',
  'risk-analyst'   : 'risk-analyst',
  'product-manager': 'product-manager',
  'cybersecurity'  : 'cybersecurity',
  'adas'           : 'adas',
  'finance'        : 'finance',
  'hr-bp'          : 'hr-bp',
  'vp-tech'        : 'vp-tech',
  'cto'            : 'cto'
};

var CITY_MAP = {
  'bengaluru' : 'bengaluru',
  'hyderabad' : 'hyderabad',
  'pune'      : 'pune',
  'mumbai'    : 'mumbai',
  'chennai'   : 'chennai',
  'ncr'       : 'ncr'
};

/* Slider index → API experienceBand string */
var EXP_LABELS  = ['0–2 years', '3–7 years', '7–12 years', '12–18 years', '18+ years'];
var EXP_API     = ['0-2 yr',    '3-7 yr',    '7-12 yr',    '12-18 yr',    '18+ yr'];

/* Human-readable city labels */
var CITY_LABELS = {
  'bengaluru':'Bengaluru','hyderabad':'Hyderabad','pune':'Pune',
  'mumbai':'Mumbai','chennai':'Chennai','ncr':'NCR'
};

/* Debounce timer */
var _debounceTimer = null;

/* ══════════════════════════════════
   SALARY INPUT VALIDATION
   Returns a clean lakhs value (>0) or 0 when empty/invalid.
   Shows an inline error only for an actual negative/invalid entry.
══════════════════════════════════ */
function readYourSalary(){
  var input   = document.getElementById('your-salary');
  var errEl   = document.getElementById('cys-error');
  var raw     = input.value.trim();

  // Empty field → no comparison, no error
  if(raw === ''){
    input.classList.remove('invalid');
    if(errEl) errEl.classList.remove('show');
    return 0;
  }

  var rupees = parseFloat(raw);

  // Invalid or <= 0 → flag error, return 0 so nothing bogus renders
  if(isNaN(rupees) || rupees <= 0){
    input.classList.add('invalid');
    if(errEl) errEl.classList.add('show');
    // Auto-correct a typed negative back to empty so the spinner can't keep it
    if(rupees < 0) input.value = '';
    return 0;
  }

  // Valid
  input.classList.remove('invalid');
  if(errEl) errEl.classList.remove('show');
  return rupees / 100000; // → lakhs
}

/* ══════════════════════════════════
   MOBILE FILTER TOGGLE
══════════════════════════════════ */
function toggleFilters(){
  var inner  = document.getElementById('filters-inner');
  var arrow  = document.getElementById('mft-arrow');
  var label  = document.getElementById('mft-label');
  var btn    = document.getElementById('filter-toggle');
  var isOpen = inner.classList.contains('is-open');

  if(isOpen){
    inner.classList.remove('is-open');
    arrow.classList.remove('open');
    label.textContent = 'Show';
    btn.setAttribute('aria-expanded','false');
  } else {
    inner.classList.add('is-open');
    arrow.classList.add('open');
    label.textContent = 'Hide';
    btn.setAttribute('aria-expanded','true');
  }
}

function handleResize(){
  var inner = document.getElementById('filters-inner');
  if(window.innerWidth > 768) inner.classList.add('is-open');
}
window.addEventListener('resize', handleResize);
handleResize();

/* ══════════════════════════════════
   EXP LABEL
══════════════════════════════════ */
function updateExpLabel(v){
  document.getElementById('exp-val').textContent = EXP_LABELS[parseInt(v)];
}

/* ══════════════════════════════════
   LOADING / ERROR STATE HELPERS
══════════════════════════════════ */
function setLoading(on){
  var btn = document.querySelector('.run-btn');
  if(!btn) return;
  btn.disabled = on;
  btn.textContent = on ? 'Loading…' : 'Update benchmark';

  /* Dim result card while fetching */
  var col = document.querySelector('.results-col');
  if(col) col.style.opacity = on ? '0.45' : '1';
}

function showError(msg){
  var el = document.getElementById('api-error-banner');
  if(!el){
    el = document.createElement('div');
    el.id = 'api-error-banner';
    el.style.cssText = [
      'background:#FEF2F2','border:1.5px solid #FECACA','border-radius:10px',
      'padding:12px 16px','font-size:13px','color:#B91C1C',
      'display:flex','gap:8px','align-items:flex-start','margin-bottom:12px'
    ].join(';');
    var rc = document.querySelector('.results-col');
    if(rc) rc.insertBefore(el, rc.firstChild);
  }
  el.innerHTML = '<span>⚠️</span><span>' + msg + '</span>';
  el.style.display = 'flex';
}

function clearError(){
  var el = document.getElementById('api-error-banner');
  if(el) el.style.display = 'none';
}

/* ══════════════════════════════════
   RENDER FUNCTIONS
══════════════════════════════════ */

/* ── Percentile bar ── */
function renderBar(d, yourLakhs){
  var p90 = d.salaryRange.p90 || 1;

  /* range bar: P25 → P75 */
  document.getElementById('rv-range').style.left  = ((d.salaryRange.p25 / p90) * 88 + 4) + '%';
  document.getElementById('rv-range').style.right = (100 - ((d.salaryRange.p75 / p90) * 88 + 4)) + '%';

  /* median tick */
  document.getElementById('rv-median').style.left = ((d.salaryRange.median / p90) * 88 + 4) + '%';

  /* your salary tick */
  var yourEl  = document.getElementById('rv-your');
  var yourLeg = document.getElementById('your-legend');
  if(yourLakhs > 0){
    yourEl.style.display  = 'block';
    yourLeg.style.display = 'flex';
    yourEl.style.left     = Math.min(96, (yourLakhs / p90) * 88 + 4) + '%';
  } else {
    yourEl.style.display  = 'none';
    yourLeg.style.display = 'none';
  }
}

/* ── KPI band labels ── */
function renderKPIs(d){
  var sr = d.salaryRange;
  document.getElementById('p25-val').textContent    = '₹' + sr.p25 + 'L';
  document.getElementById('med-val').textContent    = '₹' + sr.median + 'L';
  document.getElementById('p75-val').textContent    = '₹' + sr.p75 + 'L';
  document.getElementById('p90-val').textContent    = '₹' + sr.p90 + 'L';
  document.getElementById('kpi-median').textContent = '₹' + sr.median + 'L';
  document.getElementById('kpi-range').textContent  = '₹' + sr.p25 + '–' + sr.p75 + 'L';
  document.getElementById('kpi-sample').textContent = (d.dataPoints || 0).toLocaleString();
}

/* ── Header chips ── */
function renderHeader(d, cityKey){
  document.getElementById('result-role').textContent  = d.role + ' — ' + d.experienceBand;
  document.getElementById('ctx-city').textContent     = d.city || CITY_LABELS[cityKey] || cityKey;
  document.getElementById('ctx-vertical').textContent = d.vertical || 'All verticals';
  document.getElementById('ctx-size').textContent     = d.gccSize || 'All sizes';
}

/* ── Your salary comparison ── */
function renderYourSalary(d, yourLakhs, cityKey){
  var wrap = document.getElementById('your-salary-result');
  if(yourLakhs <= 0){ wrap.style.display = 'none'; return; }

  var sr      = d.salaryRange;
  var p25     = sr.p25, med = sr.median, p75 = sr.p75, p90 = sr.p90;
  var pctRaw  = Math.round(((yourLakhs - p25) / (p90 - p25)) * 100);
  var pct     = Math.max(5, Math.min(95, pctRaw));
  var pos     = yourLakhs < p25 ? 'below the P25 (lower quartile)'
              : yourLakhs < med ? 'below the median'
              : yourLakhs < p75 ? 'above the median, below P75'
              :                   'above P75 — well compensated';

  document.getElementById('ysr-pct').textContent = 'P' + pct;
  document.getElementById('ysr-text').innerHTML  =
    'Your CTC of ₹' + yourLakhs.toFixed(0) + 'L places you <strong>' + pos +
    '</strong> for this role in ' + (d.city || CITY_LABELS[cityKey] || cityKey) +
    '. Market median is ₹' + med + 'L.';
  wrap.style.display = 'flex';
}

/* ── Vertical breakdown table ── */
function renderVerticalTable(verticals){
  var tbody = document.querySelector('.breakdown-table tbody');
  if(!tbody || !verticals) return;

  tbody.innerHTML = '';
  verticals.forEach(function(v){
    var isPositive  = v.vsAvgPct > 0;
    var isNeutral   = v.vsAvgPct === 0;
    var pctColor    = isNeutral ? 'var(--ink-light)' : isPositive ? 'var(--teal)' : 'var(--amber)';
    var pctLabel    = isNeutral ? '+0%' : (isPositive ? '+' : '') + v.vsAvgPct + '%';
    var barWidth    = Math.min(100, Math.max(10, 50 + v.vsAvgPct * 1.5));

    var tr = document.createElement('tr');
    tr.innerHTML =
      '<td>' + v.vertical + '</td>' +
      '<td class="td-range">₹' + v.p25 + 'L</td>' +
      '<td class="td-range">₹' + v.median + 'L</td>' +
      '<td class="td-range">₹' + v.p75 + 'L</td>' +
      '<td>' +
        '<div class="td-bar">' +
          '<div class="td-bar-track"><div class="td-bar-fill" style="width:' + barWidth + '%"></div></div>' +
          '<span style="font-size:11px;color:' + pctColor + ';font-weight:600">' + pctLabel + '</span>' +
        '</div>' +
      '</td>';
    tbody.appendChild(tr);
  });
}

/* ── City comparison grid ── */
function renderCityGrid(cities, selectedCityKey){
  var grid = document.querySelector('.city-comp-grid');
  if(!grid || !cities) return;

  grid.innerHTML = '';
  cities.forEach(function(c){
    var isBase    = c.vsBasePct === 0 && c.index === 'Base city';
    var isCurrent = c.city.toLowerCase() === (CITY_LABELS[selectedCityKey]||selectedCityKey).toLowerCase();
    var idxClass  = isBase ? 'base' : c.vsBasePct > 0 ? 'high' : 'low';

    var div = document.createElement('div');
    div.className = 'cc-city' + (isCurrent ? ' current' : '');
    div.innerHTML =
      '<div class="cc-name">'  + c.city + '</div>' +
      '<div class="cc-range">₹' + c.p25 + '–' + c.p75 + 'L</div>' +
      '<div class="cc-median">Median: ₹' + c.median + 'L</div>' +
      '<div class="cc-index ' + idxClass + '">' + c.index + '</div>';
    grid.appendChild(div);
  });
}

/* ══════════════════════════════════
   MAIN FETCH + RENDER
══════════════════════════════════ */
function updateBenchmark(){
  var roleKey   = document.getElementById('f-role').value;
  var cityKey   = document.getElementById('f-city').value;
  var expIdx    = parseInt(document.getElementById('exp-slider').value);
  var yourLakhs = readYourSalary();   // validated: always 0 or a positive number

  /* Build query string */
  var params = new URLSearchParams({
    role           : ROLE_MAP[roleKey]  || roleKey,
    city           : CITY_MAP[cityKey]  || cityKey,
    experienceBand : EXP_API[expIdx]
  });
  if(yourLakhs > 0) params.set('yourSalary', yourLakhs.toFixed(2));

  setLoading(true);
  clearError();

  fetch(API_BASE + '?' + params.toString())
    .then(function(res){
      if(!res.ok) throw new Error('API returned ' + res.status);
      return res.json();
    })
    .then(function(d){
      setLoading(false);
      renderHeader(d, cityKey);
      renderKPIs(d);
      renderBar(d, yourLakhs);
      renderYourSalary(d, yourLakhs, cityKey);
      renderVerticalTable(d.verticalBreakdown);
      renderCityGrid(d.cityBreakdown, cityKey);
    })
    .catch(function(err){
      setLoading(false);
      showError('Could not load benchmark data. Please try again in a moment. (' + err.message + ')');
      console.error('[Salary Benchmark]', err);
    });
}

/* Debounced wrapper — avoids hammering the API on fast slider moves */
function updateBenchmarkDebounced(){
  clearTimeout(_debounceTimer);
  _debounceTimer = setTimeout(updateBenchmark, 350);
}

/* ══════════════════════════════════
   RESET
══════════════════════════════════ */
function resetFilters(){
  document.getElementById('f-role').value     = 'data-engineer';
  document.getElementById('f-city').value     = 'bengaluru';
  document.getElementById('f-vertical').selectedIndex = 0;
  document.getElementById('f-size').selectedIndex     = 0;
  document.getElementById('exp-slider').value = 1;
  document.getElementById('your-salary').value = '';
  document.getElementById('your-salary').classList.remove('invalid');
  document.getElementById('cys-error').classList.remove('show');
  updateExpLabel(1);
  updateBenchmark();
}

/* ══════════════════════════════════
   WIRE UP EVENTS
   (replaces inline onchange / oninput
    attrs — keeps HTML cleaner)
══════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function(){
  document.getElementById('f-role').addEventListener('change', updateBenchmark);
  document.getElementById('f-city').addEventListener('change', updateBenchmark);
  document.getElementById('f-vertical').addEventListener('change', updateBenchmark);
  document.getElementById('f-size').addEventListener('change', updateBenchmark);
  document.getElementById('exp-slider').addEventListener('input', function(){
    updateExpLabel(this.value);
    updateBenchmarkDebounced();
  });

  var yourSalaryEl = document.getElementById('your-salary');
  yourSalaryEl.addEventListener('input', updateBenchmarkDebounced);
  // On blur, normalise a negative/invalid entry immediately (don't wait for debounce)
  yourSalaryEl.addEventListener('blur', function(){
    readYourSalary();
  });
  // Block the "-" and "e" characters at keypress so a negative can't even be typed
  yourSalaryEl.addEventListener('keydown', function(e){
    if(e.key === '-' || e.key === 'e' || e.key === 'E' || e.key === '+'){
      e.preventDefault();
    }
  });

  document.querySelector('.run-btn').addEventListener('click', updateBenchmark);

  /* Initial load */
  updateBenchmark();
});
