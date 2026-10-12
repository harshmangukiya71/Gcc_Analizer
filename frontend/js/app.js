let rentChartInstance = null;
let gccChartInstance = null;
let currentSalaryData = null;

const EXP_LABELS = ['0–2 years', '3–7 years', '7–12 years', '12–18 years', '18+ years'];
const EXP_KEYS   = ['0-2 yr', '3-7 yr', '7-12 yr', '12-18 yr', '18+ yr'];

document.addEventListener("DOMContentLoaded", () => {
    loadSummary();
    loadGCCs();
    loadRents();
    loadRentChart();
    loadGCCChart();
    fetchSalaryBenchmark();
    loadIncentives();
});

function switchTab(tab) {
    ['gcc', 'rent', 'talent', 'incentives'].forEach(t => {
        document.getElementById(`tab-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}-btn`).classList.remove('active', 'text-blue-600');
        document.getElementById(`tab-${t}-btn`).classList.add('text-slate-500');
        const nav = document.getElementById(`nav-${t}`);
        if (nav) {
            nav.classList.remove('bg-blue-600', 'text-white');
            nav.classList.add('text-slate-400');
        }
    });
    document.getElementById(`tab-${tab}`).classList.remove('hidden');
    document.getElementById(`tab-${tab}-btn`).classList.add('active', 'text-blue-600');
    document.getElementById(`tab-${tab}-btn`).classList.remove('text-slate-500');

    const navActive = document.getElementById(`nav-${tab}`);
    if (navActive) {
        navActive.classList.add('bg-blue-600', 'text-white');
        navActive.classList.remove('text-slate-400');
    }

    const breadcrumbMap = {
        gcc: 'GCC Companies Registry',
        rent: 'Office Rent Benchmarks',
        talent: 'Talent Salary Benchmarks (Sansovi)',
        incentives: 'Incentive Schemes'
    };
    document.getElementById('header-breadcrumb').innerText = breadcrumbMap[tab];
}

async function loadSummary() {
    try {
        const res = await fetch('/api/summary');
        const data = await res.json();
        document.getElementById('kpi-gccs').innerText = data.gcc_companies;
        document.getElementById('kpi-rents').innerText = data.office_rents;
        if (data.talent_benchmarks) {
            document.getElementById('kpi-talent').innerText = data.talent_benchmarks;
        }
        if (data.incentive_schemes !== undefined) {
            document.getElementById('kpi-incentives').innerText = data.incentive_schemes;
        }
    } catch (err) {
        console.error("Summary error:", err);
    }
}

async function loadGCCs() {
    const city = document.getElementById('gcc-city').value;
    const sector = document.getElementById('gcc-sector').value;
    const search = document.getElementById('gcc-search').value;

    const url = new URL('/api/gccs', window.location.origin);
    if (city && city !== 'all') url.searchParams.append('city', city);
    if (sector && sector !== 'all') url.searchParams.append('sector', sector);
    if (search) url.searchParams.append('search', search);

    try {
        const res = await fetch(url);
        const data = await res.json();
        document.getElementById('gcc-count-badge').innerText = data.length;

        const tbody = document.getElementById('gcc-table-body');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-400">No GCC records matching your filters</td></tr>`;
            return;
        }

        data.forEach(r => {
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-50 transition";
            tr.innerHTML = `
                <td class="py-3 px-6 font-semibold text-slate-900">${r.company_name}</td>
                <td class="py-3 px-4"><span class="px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-xs font-medium">${r.city}</span></td>
                <td class="py-3 px-4 text-xs">${r.sector}</td>
                <td class="py-3 px-4"><span class="font-medium text-slate-800 text-xs">${r.india_headcount}</span></td>
                <td class="py-3 px-6 text-xs text-slate-500 max-w-xs truncate" title="${r.key_roles_hired}">${r.key_roles_hired}</td>
                <td class="py-3 px-4 text-right">
                    ${r.website && r.website !== '#' ? `<a href="${r.website}" target="_blank" class="text-blue-600 hover:text-blue-800 text-xs font-medium"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>` : '-'}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading GCCs:", err);
    }
}

function resetGCCFilters() {
    document.getElementById('gcc-city').value = 'all';
    document.getElementById('gcc-sector').value = 'all';
    document.getElementById('gcc-search').value = '';
    loadGCCs();
}

async function loadRents() {
    const city = document.getElementById('rent-city').value;
    const rentLevel = document.getElementById('rent-level').value;

    const url = new URL('/api/rents', window.location.origin);
    if (city && city !== 'all') url.searchParams.append('city', city);
    if (rentLevel && rentLevel !== 'all') url.searchParams.append('rent_level', rentLevel);

    try {
        const res = await fetch(url);
        const data = await res.json();
        document.getElementById('rent-count-badge').innerText = data.length;

        const tbody = document.getElementById('rent-table-body');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center py-8 text-slate-400">No rent records found</td></tr>`;
            return;
        }

        data.forEach(r => {
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-50 transition";
            const isAvg = r.rent_level === 'city_average';
            tr.innerHTML = `
                <td class="py-3 px-6 font-semibold text-slate-900">${r.city}</td>
                <td class="py-3 px-6 text-sm ${isAvg ? 'font-bold text-blue-600' : 'text-slate-700'}">${r.micro_market}</td>
                <td class="py-3 px-4">
                    <span class="px-2 py-0.5 rounded text-xs font-medium ${isAvg ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-600'}">
                        ${r.rent_level}
                    </span>
                </td>
                <td class="py-3 px-6 text-right font-bold text-slate-900">₹ ${r.rent_inr_per_sqft_per_month.toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading rents:", err);
    }
}

function resetRentFilters() {
    document.getElementById('rent-city').value = 'all';
    document.getElementById('rent-level').value = 'all';
    loadRents();
}

async function loadRentChart() {
    try {
        const res = await fetch('/api/rent-chart');
        const data = await res.json();
        const ctx = document.getElementById('rentChart').getContext('2d');
        if (rentChartInstance) rentChartInstance.destroy();
        rentChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.city),
                datasets: [{
                    label: 'City Average Rent (₹ / sq ft / month)',
                    data: data.map(d => d.rent),
                    backgroundColor: ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#a78bfa', '#c084fc', '#e879f9'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: '₹ / sq ft / month' } }
                }
            }
        });
    } catch (err) {
        console.error("Rent chart error:", err);
    }
}

async function loadGCCChart() {
    try {
        const res = await fetch('/api/gcc-chart');
        const data = await res.json();
        const ctx = document.getElementById('gccChart').getContext('2d');
        if (gccChartInstance) gccChartInstance.destroy();
        gccChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.city),
                datasets: [{
                    label: 'Number of GCCs',
                    data: data.map(d => d.count),
                    backgroundColor: '#8b5cf6',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'GCC Count' } }
                }
            }
        });
    } catch (err) {
        console.error("GCC chart error:", err);
    }
}

// =====================================================================
// SANSOVI SALARY BENCHMARK LOGIC
// =====================================================================

function updateExpSlider(val) {
    document.getElementById('s-exp-label').innerText = EXP_LABELS[val];
    fetchSalaryBenchmark();
}

async function fetchSalaryBenchmark() {
    const role = document.getElementById('s-role').value;
    const city = document.getElementById('s-city').value;
    const expIdx = parseInt(document.getElementById('s-exp-slider').value);
    const expBand = EXP_KEYS[expIdx];

    const url = `/api/salary-benchmark?role=${encodeURIComponent(role)}&city=${encodeURIComponent(city)}&experienceBand=${encodeURIComponent(expBand)}`;
    try {
        const res = await fetch(url);
        const data = await res.json();
        currentSalaryData = data;
        renderSalaryBenchmark(data);
    } catch (err) {
        console.error("Salary benchmark fetch error:", err);
    }
}

function renderSalaryBenchmark(d) {
    if (!d || d.error) return;

    const sr = d.salaryRange || {};
    const p10 = sr.p10 || 10;
    const p25 = sr.p25 || 15;
    const med = sr.median || 25;
    const p75 = sr.p75 || 40;
    const p90 = sr.p90 || 55;

    // Update Header & Chips
    document.getElementById('res-role-title').innerText = `${d.role} • ${d.experienceBand}`;
    document.getElementById('res-chip-city').innerText = d.city;
    document.getElementById('res-sample-points').innerText = `${(d.dataPoints || 0).toLocaleString()} data points`;

    // Update KPI Values
    document.getElementById('val-p25').innerText = `₹${p25}L`;
    document.getElementById('val-median').innerText = `₹${med}L`;
    document.getElementById('val-p75').innerText = `₹${p75}L`;
    document.getElementById('val-p90').innerText = `₹${p90}L`;

    // Update Bar Labels
    document.getElementById('bar-p10').innerText = `₹${p10}L`;
    document.getElementById('bar-typical').innerText = `₹${p25}L – ₹${p75}L`;
    document.getElementById('bar-p90').innerText = `₹${p90}L`;

    // Calculate Visual Bar Positions
    const leftPct = (p25 / p90) * 88 + 4;
    const rightPct = (p75 / p90) * 88 + 4;
    const widthPct = Math.max(5, rightPct - leftPct);
    const medPct = (med / p90) * 88 + 4;

    document.getElementById('range-highlight-bar').style.left = `${leftPct}%`;
    document.getElementById('range-highlight-bar').style.width = `${widthPct}%`;
    document.getElementById('range-median-tick').style.left = `${medPct}%`;

    // Check if user salary input is present
    renderYourSalaryComparison();

    // Render Industry Vertical Multipliers
    const vBody = document.getElementById('res-verticals-body');
    vBody.innerHTML = '';
    const verticals = d.verticalBreakdown || [];
    verticals.forEach(v => {
        const tr = document.createElement('tr');
        const isPos = v.vsAvgPct > 0;
        const isNeu = v.vsAvgPct === 0;
        const badgeClass = isNeu ? 'bg-slate-100 text-slate-700' : (isPos ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800');
        const badgeText = isNeu ? '0%' : (isPos ? `+${v.vsAvgPct}%` : `${v.vsAvgPct}%`);

        tr.innerHTML = `
            <td class="py-2.5 px-6 font-medium text-slate-800">${v.vertical}</td>
            <td class="py-2.5 px-4 text-center">₹${v.p25}L</td>
            <td class="py-2.5 px-4 text-center font-bold text-slate-900">₹${v.median}L</td>
            <td class="py-2.5 px-4 text-center">₹${v.p75}L</td>
            <td class="py-2.5 px-6 text-right">
                <span class="px-2 py-0.5 rounded text-xs font-bold ${badgeClass}">${badgeText}</span>
            </td>
        `;
        vBody.appendChild(tr);
    });

    // Render Multi-City Cost Comparison Grid
    const cGrid = document.getElementById('res-city-grid');
    cGrid.innerHTML = '';
    const cities = d.cityBreakdown || [];
    cities.forEach(c => {
        const card = document.createElement('div');
        const isCur = c.city.toLowerCase() === d.city.toLowerCase();
        const isBase = c.index === 'Base city';
        card.className = `p-3 rounded-xl border text-center transition ${isCur ? 'border-indigo-500 bg-indigo-50/50 ring-2 ring-indigo-200' : 'border-slate-200 bg-slate-50'}`;
        card.innerHTML = `
            <div class="font-bold text-xs text-slate-800">${c.city}</div>
            <div class="text-sm font-extrabold text-slate-900 mt-0.5">₹${c.median}L</div>
            <div class="text-[11px] text-slate-500">₹${c.p25}–₹${c.p75}L</div>
            <span class="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] font-semibold ${isBase ? 'bg-slate-200 text-slate-700' : (c.vsBasePct > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800')}">
                ${c.index}
            </span>
        `;
        cGrid.appendChild(card);
    });
}

function renderYourSalaryComparison() {
    const val = parseFloat(document.getElementById('s-your-salary').value);
    const alertBox = document.getElementById('res-your-alert');
    const yourTick = document.getElementById('range-your-tick');

    if (!val || val <= 0 || !currentSalaryData) {
        alertBox.classList.add('hidden');
        yourTick.classList.add('hidden');
        return;
    }

    const valLakhs = val / 100000;
    const sr = currentSalaryData.salaryRange || {};
    const p25 = sr.p25 || 15;
    const med = sr.median || 25;
    const p75 = sr.p75 || 40;
    const p90 = sr.p90 || 55;

    // Calculate placement
    let pct = Math.round(((valLakhs - p25) / (p90 - p25)) * 100);
    pct = Math.max(5, Math.min(95, pct));

    let placement = '';
    if (valLakhs < p25) placement = 'below lower quartile (P25)';
    else if (valLakhs < med) placement = 'below market median';
    else if (valLakhs < p75) placement = 'above median, below upper quartile (P75)';
    else placement = 'above upper quartile (P75) - highly compensated';

    document.getElementById('res-pct-badge').innerText = `P${pct}`;
    document.getElementById('res-pct-text').innerHTML = `
        Your CTC of <strong>₹${valLakhs.toFixed(1)}L</strong> places you at the <strong>P${pct} percentile (${placement})</strong> for this role in ${currentSalaryData.city}. Market median is ₹${med}L.
    `;
    alertBox.classList.remove('hidden');

    // Position Tick
    const yourPct = Math.min(96, Math.max(4, (valLakhs / p90) * 88 + 4));
    yourTick.style.left = `${yourPct}%`;
    yourTick.classList.remove('hidden');
}

function resetSalaryFilters() {
    document.getElementById('s-role').value = 'data-engineer';
    document.getElementById('s-city').value = 'bengaluru';
    document.getElementById('s-exp-slider').value = 1;
    document.getElementById('s-your-salary').value = '';
    updateExpSlider(1);
}

// ==========================================
// INCENTIVE POLICIES LOGIC
// ==========================================
async function loadIncentives() {
    const state = document.getElementById('incentive-state').value;
    const cat = document.getElementById('incentive-cat').value;
    const search = document.getElementById('incentive-search').value;

    const url = new URL('/api/incentives', window.location.origin);
    if (state && state !== 'all') url.searchParams.append('state', state);
    if (cat && cat !== 'all') url.searchParams.append('category', cat);
    if (search) url.searchParams.append('search', search);

    try {
        const res = await fetch(url);
        const data = await res.json();
        document.getElementById('incentive-count-badge').innerText = data.length;

        const tbody = document.getElementById('incentive-table-body');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-400">No incentive policies match the selected criteria</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-50 transition border-b border-slate-100";

            // Badge color by category
            let catColor = "bg-slate-100 text-slate-700 border-slate-200";
            if (item.incentive_category === "Skill Development") catColor = "bg-blue-50 text-blue-700 border-blue-200";
            else if (item.incentive_category === "Employment Generation") catColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
            else if (item.incentive_category === "Research & Development") catColor = "bg-purple-50 text-purple-700 border-purple-200";
            else if (item.incentive_category === "Intellectual Property") catColor = "bg-amber-50 text-amber-700 border-amber-200";
            else if (item.incentive_category === "Physical Infrastructure") catColor = "bg-indigo-50 text-indigo-700 border-indigo-200";
            else if (item.incentive_category === "Vision / Strategic Impact") catColor = "bg-rose-50 text-rose-700 border-rose-200";

            tr.innerHTML = `
                <td class="py-3 px-6">
                    <div class="font-bold text-slate-900">${item.state_or_ut}</div>
                    <div class="text-xs text-slate-500">${item.policy_name}</div>
                </td>
                <td class="py-3 px-4">
                    <span class="inline-block px-2 py-0.5 rounded text-xs font-semibold border ${catColor}">
                        ${item.incentive_category}
                    </span>
                </td>
                <td class="py-3 px-6 text-slate-800 font-medium max-w-md">
                    ${item.benefit_description}
                </td>
                <td class="py-3 px-4 text-xs text-slate-600">
                    ${item.eligibility_criteria || 'General Eligibility'}
                </td>
                <td class="py-3 px-4">
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> ${item.policy_status}
                    </span>
                </td>
                <td class="py-3 px-4 text-right">
                    <a href="${item.official_source_url}" target="_blank" class="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-semibold hover:underline">
                        Official Portal <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                    </a>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading incentives:", err);
    }
}

function resetIncentiveFilters() {
    document.getElementById('incentive-state').value = 'all';
    document.getElementById('incentive-cat').value = 'all';
    document.getElementById('incentive-search').value = '';
    loadIncentives();
}
