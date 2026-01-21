const CHANGELOG_URL = 'data/changelog.json';
const WEEKS_PER_PAGE = 8;

let allWeeks = [];
let displayedWeeks = 0;
let observer = null;

async function init() {
  try {
    const response = await fetch(CHANGELOG_URL);
    const data = await response.json();
    allWeeks = data.weeks || [];
    
    if (allWeeks.length === 0) {
      showEmpty();
      return;
    }

    renderNextBatch();
    setupIntersectionObserver();
  } catch (error) {
    console.error('Failed to load changelog:', error);
    showError();
  }
}

function renderNextBatch() {
  const changelog = document.getElementById('changelog');
  const end = Math.min(displayedWeeks + WEEKS_PER_PAGE, allWeeks.length);

  for (let i = displayedWeeks; i < end; i++) {
    const week = allWeeks[i];
    const weekEl = createWeekElement(week);
    changelog.appendChild(weekEl);
    
    // Trigger fade-in after a brief delay
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        weekEl.classList.add('visible');
      });
    });
  }

  displayedWeeks = end;

  // Hide loading indicator if all weeks are displayed
  if (displayedWeeks >= allWeeks.length) {
    document.getElementById('loading').classList.add('hidden');
    if (observer) observer.disconnect();
  }
}

function toStardate(date) {
  // TNG-era stardate: year + fractional day of year
  const year = date.getFullYear();
  const startOfYear = new Date(year, 0, 0);
  const diff = date - startOfYear;
  const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));
  const stardate = (year - 2323) * 1000 + (dayOfYear / 365.25) * 1000;
  return stardate.toFixed(1);
}

function createWeekElement(week) {
  const section = document.createElement('section');
  section.className = 'fade-in';

  const weekDate = new Date(week.weekOf + 'T00:00:00');
  const formattedDate = weekDate.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });
  const stardate = toStardate(weekDate);

  section.innerHTML = `
    <h2 class="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4 cursor-default week-header"
        data-normal="Week of ${formattedDate}"
        data-stardate="Stardate ${stardate}">
      Week of ${formattedDate}
    </h2>
    <ul class="space-y-3">
      ${week.entries.map(entry => `
        <li class="flex gap-3">
          <span class="text-gray-300 select-none">•</span>
          <div class="flex-1">
            <p class="text-gray-700">${escapeHtml(entry.summary)}</p>
            ${entry.repo ? `
              <a href="${escapeHtml(entry.url)}" 
                 class="text-sm text-gray-400 hover:text-gray-600 transition-colors"
                 target="_blank" rel="noopener">
                ${escapeHtml(entry.repo)}
              </a>
            ` : ''}
          </div>
        </li>
      `).join('')}
    </ul>
  `;

  return section;
}

function setupIntersectionObserver() {
  const loading = document.getElementById('loading');
  loading.classList.remove('hidden');

  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && displayedWeeks < allWeeks.length) {
      renderNextBatch();
    }
  }, {
    rootMargin: '200px'
  });

  observer.observe(loading);
}

function showEmpty() {
  document.getElementById('changelog').innerHTML = `
    <p class="text-gray-400">No changelog entries yet.</p>
  `;
}

function showError() {
  document.getElementById('changelog').innerHTML = `
    <p class="text-red-500">Failed to load changelog. Please try again later.</p>
  `;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Easter egg: swap to stardate on hover
document.addEventListener('mouseover', (e) => {
  const header = e.target.closest('.week-header');
  if (header) header.textContent = header.dataset.stardate;
});
document.addEventListener('mouseout', (e) => {
  const header = e.target.closest('.week-header');
  if (header) header.textContent = header.dataset.normal;
});

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
