/**
 * Frontend JavaScript for Target TestBench
 * Handles function catalog rendering, live health polling,
 * preset loading, interactive execution, and theme toggling.
 */

document.addEventListener('DOMContentLoaded', () => {
  let allFunctions = [];
  let currentFilter = 'all';

  const functionsGrid = document.getElementById('functionsGrid');
  const searchInput = document.getElementById('searchInput');
  const filterTabs = document.getElementById('filterTabs');
  const footerShaText = document.getElementById('footerShaText');
  const healthStatusText = document.getElementById('healthStatusText');
  const copyShaBtn = document.getElementById('copyShaBtn');
  const themeToggle = document.getElementById('themeToggle');

  // --- Theme Toggle ---
  const savedTheme = localStorage.getItem('target_theme') || 'dark';
  if (savedTheme === 'light') {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
  }

  themeToggle.addEventListener('click', () => {
    const isLight = document.body.classList.toggle('light-theme');
    document.body.classList.toggle('dark-theme', !isLight);
    localStorage.setItem('target_theme', isLight ? 'light' : 'dark');
  });

  // --- Health & Commit SHA Polling ---
  async function fetchHealth() {
    try {
      const res = await fetch('/health');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      healthStatusText.textContent = 'Live (200 OK)';
      const sha = data.commit_sha || 'unknown';
      footerShaText.textContent = sha;
      footerShaText.title = `Full SHA: ${sha}`;
    } catch (err) {
      healthStatusText.textContent = 'Offline';
      footerShaText.textContent = 'Connection Error';
    }
  }

  // Initial fetch and poll every 10 seconds
  fetchHealth();
  setInterval(fetchHealth, 10000);

  // Copy SHA
  copyShaBtn.addEventListener('click', () => {
    const text = footerShaText.textContent;
    if (text && text !== 'Loading...' && text !== 'Connection Error') {
      navigator.clipboard.writeText(text).then(() => {
        const originalTitle = copyShaBtn.title;
        copyShaBtn.title = 'Copied!';
        setTimeout(() => {
          copyShaBtn.title = originalTitle;
        }, 1500);
      });
    }
  });

  // --- Functions Catalog Loading ---
  async function loadFunctions() {
    try {
      const res = await fetch('/api/functions');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      allFunctions = data.functions || [];
      renderFunctions();
    } catch (err) {
      functionsGrid.innerHTML = `
        <div class="loading-state">
          <p style="color: var(--error);">Failed to load functions: ${err.message}</p>
        </div>
      `;
    }
  }

  // --- Render Functions Grid ---
  function renderFunctions() {
    const query = searchInput.value.trim().toLowerCase();

    const filtered = allFunctions.filter(fn => {
      // Category filter
      if (currentFilter === 'data-type' && !fn.category.toLowerCase().includes('data-type')) {
        return false;
      }
      if (currentFilter === 'mathematics' && !fn.category.toLowerCase().includes('mathematics')) {
        return false;
      }

      // Search query
      if (!query) return true;
      return (
        fn.name.toLowerCase().includes(query) ||
        fn.description.toLowerCase().includes(query) ||
        fn.category.toLowerCase().includes(query)
      );
    });

    if (filtered.length === 0) {
      functionsGrid.innerHTML = `
        <div class="loading-state">
          <p>No functions matched your search query.</p>
        </div>
      `;
      return;
    }

    functionsGrid.innerHTML = '';
    filtered.forEach(fn => {
      functionsGrid.appendChild(createFunctionCard(fn));
    });
  }

  // --- Create Single Function Card ---
  function createFunctionCard(fn) {
    const card = document.createElement('article');
    card.className = 'function-card';
    card.id = `card-${fn.id}`;

    // Header
    const header = document.createElement('div');
    header.className = 'card-header';
    header.innerHTML = `
      <div class="card-title-group">
        <h3 class="function-name">${fn.name}()</h3>
        <span class="function-category">${fn.category}</span>
      </div>
      <span class="category-badge">${fn.category.split(':')[0]}</span>
    `;
    card.appendChild(header);

    // Description
    const desc = document.createElement('p');
    desc.className = 'function-desc';
    desc.textContent = fn.description;
    card.appendChild(desc);

    // Presets
    if (fn.presets && fn.presets.length > 0) {
      const presetsSec = document.createElement('div');
      presetsSec.className = 'presets-section';
      presetsSec.innerHTML = `<span class="presets-label">Quick Test Presets:</span>`;

      const presetsRow = document.createElement('div');
      presetsRow.className = 'presets-row';

      fn.presets.forEach(preset => {
        const pBtn = document.createElement('button');
        pBtn.className = 'preset-btn';
        pBtn.textContent = preset.label;
        pBtn.addEventListener('click', () => {
          applyPreset(card, fn, preset.args);
        });
        presetsRow.appendChild(pBtn);
      });

      presetsSec.appendChild(presetsRow);
      card.appendChild(presetsSec);
    }

    // Input Fields
    const formFields = document.createElement('div');
    formFields.className = 'form-fields';

    fn.params.forEach(param => {
      const grp = document.createElement('div');
      grp.className = 'field-group';

      const label = document.createElement('label');
      label.className = 'field-label';
      label.textContent = param.label || param.name;
      grp.appendChild(label);

      let inputEl;
      if (param.type === 'select') {
        inputEl = document.createElement('select');
        inputEl.className = 'field-input';
        param.options.forEach(opt => {
          const optEl = document.createElement('option');
          optEl.value = opt;
          optEl.textContent = opt;
          if (String(opt) === String(param.default)) optEl.selected = true;
          inputEl.appendChild(optEl);
        });
      } else {
        inputEl = document.createElement('input');
        inputEl.className = 'field-input';
        inputEl.type = param.type === 'number' ? 'number' : 'text';
        if (param.type === 'number') inputEl.step = 'any';
        inputEl.value = param.default !== undefined ? (typeof param.default === 'object' ? JSON.stringify(param.default) : param.default) : '';
      }

      inputEl.dataset.paramName = param.name;
      inputEl.dataset.paramType = param.type;
      grp.appendChild(inputEl);
      formFields.appendChild(grp);
    });

    card.appendChild(formFields);

    // Card Actions
    const actions = document.createElement('div');
    actions.className = 'card-actions';

    const runBtn = document.createElement('button');
    runBtn.className = 'run-btn';
    runBtn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
      Run Function
    `;
    runBtn.addEventListener('click', () => runFunction(card, fn));
    actions.appendChild(runBtn);
    card.appendChild(actions);

    // Result Box
    const resultBox = document.createElement('div');
    resultBox.className = 'result-box';
    resultBox.style.display = 'none';
    card.appendChild(resultBox);

    return card;
  }

  // --- Apply Preset Values to Inputs ---
  function applyPreset(card, fn, args) {
    const inputs = card.querySelectorAll('.field-input');
    inputs.forEach(input => {
      const pName = input.dataset.paramName;
      if (pName in args) {
        const val = args[pName];
        if (typeof val === 'object' && val !== null) {
          input.value = JSON.stringify(val);
        } else if (val === null) {
          input.value = 'null';
        } else {
          input.value = val;
        }
      }
    });

    // Auto-run preset for instant verification
    runFunction(card, fn);
  }

  // --- Execute Function via API ---
  async function runFunction(card, fn) {
    const runBtn = card.querySelector('.run-btn');
    const resultBox = card.querySelector('.result-box');
    const inputs = card.querySelectorAll('.field-input');

    const originalBtnText = runBtn.innerHTML;
    runBtn.innerHTML = `<span class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></span> Running...`;
    runBtn.disabled = true;

    const args = {};
    for (const input of inputs) {
      const pName = input.dataset.paramName;
      const pType = input.dataset.paramType;
      const rawVal = input.value;

      if (rawVal === 'null') {
        args[pName] = null;
      } else if (pType === 'number') {
        args[pName] = rawVal === '' ? null : Number(rawVal);
      } else if (pType === 'select') {
        args[pName] = rawVal;
      } else if (pType === 'json') {
        try {
          args[pName] = JSON.parse(rawVal);
        } catch (e) {
          args[pName] = rawVal; // Pass raw string to let target/server catch invalid syntax
        }
      } else {
        args[pName] = rawVal;
      }
    }

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          function_name: fn.name,
          arguments: args,
        }),
      });

      const data = await res.json();
      resultBox.style.display = 'flex';

      if (data.success) {
        resultBox.className = 'result-box success';
        resultBox.innerHTML = `
          <div class="result-header">
            <span class="result-status">● Success (200 OK)</span>
            <span class="result-type-tag">Return Type: ${data.result_type}</span>
          </div>
          <div class="result-content">${escapeHtml(JSON.stringify(data.result, null, 2))}</div>
        `;
      } else {
        resultBox.className = 'result-box error';
        resultBox.innerHTML = `
          <div class="result-header">
            <span class="result-status">▲ Caught Exception</span>
            <span class="result-type-tag" style="background: rgba(244, 63, 94, 0.25); color: #fecdd3; border: 1px solid rgba(244, 63, 94, 0.4);">${data.error_type}</span>
          </div>
          <div class="result-content">${escapeHtml(data.error_message)}</div>
        `;
      }
    } catch (err) {
      resultBox.style.display = 'flex';
      resultBox.className = 'result-box error';
      resultBox.innerHTML = `
        <div class="result-header">
          <span class="result-status">Network Error</span>
        </div>
        <div class="result-content">${escapeHtml(err.message)}</div>
      `;
    } finally {
      runBtn.innerHTML = originalBtnText;
      runBtn.disabled = false;
    }
  }

  function escapeHtml(str) {
    if (typeof str !== 'string') str = String(str);
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // --- Filtering & Search Event Listeners ---
  filterTabs.addEventListener('click', (e) => {
    if (e.target.classList.contains('filter-tab')) {
      filterTabs.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
      e.target.classList.add('active');
      currentFilter = e.target.dataset.filter;
      renderFunctions();
    }
  });

  searchInput.addEventListener('input', () => {
    renderFunctions();
  });

  // Start initialization
  loadFunctions();
});
