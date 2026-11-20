'use strict';

document.body.classList.add('interactive');
const menu = document.querySelector('.mobile-menu');
const sidebar = document.querySelector('.sidebar');
const launch = document.querySelector('.search-launch');
const dialog = document.getElementById('search-dialog');
const input = document.getElementById('search-input');
const status = document.getElementById('search-status');
const results = document.getElementById('search-results');
let indexRequest;

menu.addEventListener('click', () => {
  const open = sidebar.classList.toggle('is-open');
  menu.setAttribute('aria-expanded', String(open));
});

function openSearch() {
  if (!dialog.open) dialog.showModal();
  input.focus();
  input.select();
  void search();
}

launch.addEventListener('click', openSearch);
document.querySelector('.close-search').addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => launch.focus());
document.addEventListener('keydown', event => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    openSearch();
  } else if (event.key === 'Escape' && !dialog.open && sidebar.classList.contains('is-open')) {
    sidebar.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.focus();
  }
});

function loadIndex() {
  indexRequest ??= fetch(document.body.dataset.search).then(response => {
    if (!response.ok) throw Error('Search index is unavailable');
    return response.json();
  }).catch(error => {
    indexRequest = undefined;
    throw error;
  });
  return indexRequest;
}

async function search() {
  const value = input.value.trim().toLowerCase();
  results.replaceChildren();
  if (!value) {
    status.textContent = 'Try duplicate review, partial payment or field capture.';
    return;
  }
  try {
    const entries = await loadIndex();
    if (input.value.trim().toLowerCase() !== value) return;
    const terms = value.split(/\s+/);
    const matching = entries.map(entry => {
      const title = entry.title.toLowerCase();
      const lead = (entry.description + ' ' + entry.section).toLowerCase();
      const body = entry.body.toLowerCase();
      const counts = terms.map(term => title.includes(term) ? 6 : lead.includes(term) ? 3 : body.includes(term) ? 1 : 0);
      const score = counts.every(Boolean) ? counts.reduce((a, b) => a + b, 0) + (title.includes(value) ? 4 : 0) : 0;
      return {entry, score};
    }).filter(match => match.score).sort((a, b) => b.score - a.score);
    status.textContent = matching.length ? `${matching.length} matching page${matching.length === 1 ? '' : 's'}` : 'No matching pages.';
    for (const {entry} of matching.slice(0, 20)) {
      const li = document.createElement('li');
      const link = document.createElement('a');
      const section = document.createElement('small');
      const summary = document.createElement('span');
      link.href = entry.url;
      section.textContent = entry.section;
      summary.textContent = entry.description;
      link.append(section, entry.title, summary);
      li.append(link);
      results.append(li);
    }
  } catch {
    if (input.value.trim().toLowerCase() === value) status.textContent = 'Search is unavailable. Use the service list to browse the guides.';
  }
}

input.addEventListener('input', search);
input.addEventListener('keydown', event => {
  if (event.key === 'ArrowDown') results.querySelector('a')?.focus();
  if (event.key === 'Enter') results.querySelector('a')?.click();
});

// The link also opens the original capture when the dialog API is unavailable.
if (document.querySelector('.screen-link') && typeof HTMLDialogElement !== 'undefined') {
  const viewer = document.createElement('dialog');
  viewer.className = 'image-viewer';
  viewer.setAttribute('aria-label', 'Enlarged screenshot');
  viewer.innerHTML = '<div class="viewer-bar"><button type="button" class="viewer-zoom" aria-pressed="false">Actual size</button><button type="button" class="viewer-close" autofocus>Close</button></div><div class="viewer-scroll" tabindex="0" role="region" aria-label="Screenshot"><img alt=""></div><p class="viewer-caption"></p>';
  document.body.append(viewer);
  const scrollArea = viewer.querySelector('.viewer-scroll');
  const enlarged = scrollArea.querySelector('img');
  const zoom = viewer.querySelector('.viewer-zoom');
  const close = viewer.querySelector('.viewer-close');
  let trigger;
  document.addEventListener('click', event => {
    const link = event.target.closest('.screen-link');
    if (!link || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    trigger = link;
    const caption = link.closest('figure').querySelector('figcaption').textContent;
    enlarged.src = link.href;
    enlarged.alt = caption;
    viewer.querySelector('.viewer-caption').textContent = caption;
    scrollArea.classList.remove('full-size');
    zoom.setAttribute('aria-pressed', 'false');
    viewer.showModal();
    scrollArea.scrollTo(0, 0);
    close.focus();
  });
  zoom.addEventListener('click', () => {
    const full = scrollArea.classList.toggle('full-size');
    zoom.setAttribute('aria-pressed', String(full));
    scrollArea.scrollTo(0, 0);
  });
  close.addEventListener('click', () => viewer.close());
  viewer.addEventListener('close', () => trigger?.focus({preventScroll:true}));
}
