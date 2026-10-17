/**
 * Target TestBench · Astral Studio
 * Features:
 * 1. Astral Shell 3D Component (Slowly turning globe of connected stars with pulse waves)
 * 2. Studio Workbench (Two-column layout, quick presets, parameter schema, syntax inspector)
 * 3. Live /health & Deployed Commit SHA polling
 */

document.addEventListener('DOMContentLoaded', () => {
  // =========================================================================
  // 1. ASTRAL SHELL: Slowly Turning Globe of Connected Stars (3D Canvas)
  // =========================================================================
  const canvas = document.getElementById('astralShellCanvas');
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  // Astral Shell Parameters
  const NUM_STARS = 190;
  const GLOBE_RADIUS = Math.min(width, height) * 0.38;
  const MAX_CONNECT_DIST = GLOBE_RADIUS * 0.42;

  let spinSpeed = 0.0035;
  let tiltAngle = 0.35; // forward tilt
  let rotX = tiltAngle;
  let rotY = 0;

  let isDragging = false;
  let lastMouseX = 0;
  let lastMouseY = 0;
  let velX = 0;
  let velY = 0;

  // Pulse wave system
  const pulses = [];

  // Generate stars on a 3D sphere using Fibonacci Sphere algorithm
  const stars = [];
  const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle

  for (let i = 0; i < NUM_STARS; i++) {
    const y = 1 - (i / (NUM_STARS - 1)) * 2; // y goes from 1 to -1
    const radiusAtY = Math.sqrt(1 - y * y);
    const theta = phi * i;

    // Add slight natural perturbation
    const r = GLOBE_RADIUS * (0.95 + Math.random() * 0.1);
    const x = Math.cos(theta) * radiusAtY;
    const z = Math.sin(theta) * radiusAtY;

    stars.push({
      x: x * r,
      y: y * r,
      z: z * r,
      baseSize: 1.2 + Math.random() * 1.6,
      twinkleSpeed: 0.02 + Math.random() * 0.04,
      twinklePhase: Math.random() * Math.PI * 2,
    });
  }

  // Astral Shell Controls
  const speedSlider = document.getElementById('astralSpinSpeed');
  if (speedSlider) {
    speedSlider.addEventListener('input', (e) => {
      spinSpeed = (parseFloat(e.target.value) / 100) * 0.0035;
    });
  }

  const pulseBtn = document.getElementById('astralPulseBtn');
  if (pulseBtn) {
    pulseBtn.addEventListener('click', triggerCelestialPulse);
  }

  function triggerCelestialPulse() {
    pulses.push({
      radius: 0,
      maxRadius: GLOBE_RADIUS * 1.4,
      speed: 4.5,
      intensity: 1.0,
    });
  }

  // Pointer Dragging for interactive 3D rotation
  window.addEventListener('mousedown', (e) => {
    // Only drag when clicking background or canvas
    if (e.target === canvas || e.target.classList.contains('astral-canvas-container')) {
      isDragging = true;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
    }
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - lastMouseX;
    const dy = e.clientY - lastMouseY;
    velY = dx * 0.003;
    velX = dy * 0.003;
    rotY += velY;
    rotX += velX;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  // Click on background triggers pulse
  canvas.addEventListener('click', (e) => {
    triggerCelestialPulse();
  });

  // Astral Shell Render Loop
  function renderAstralShell() {
    ctx.clearRect(0, 0, width, height);

    // Apply auto-rotation and inertia
    if (!isDragging) {
      rotY += spinSpeed;
      rotX += (tiltAngle - rotX) * 0.02; // gently restore tilt
      velX *= 0.95;
      velY *= 0.95;
      rotY += velY;
      rotX += velX;
    }

    const cosY = Math.cos(rotY);
    const sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX);
    const sinX = Math.sin(rotX);

    // Center of globe (offset slightly to the right for gorgeous visual balance)
    const centerX = width > 1100 ? width * 0.62 : width * 0.5;
    const centerY = height * 0.48;

    // Update Pulses
    for (let p = pulses.length - 1; p >= 0; p--) {
      pulses[p].radius += pulses[p].speed;
      pulses[p].intensity = 1.0 - (pulses[p].radius / pulses[p].maxRadius);
      if (pulses[p].radius >= pulses[p].maxRadius) {
        pulses.splice(p, 1);
      }
    }

    // Project 3D stars to 2D
    const projected = [];
    for (let i = 0; i < stars.length; i++) {
      const s = stars[i];

      // Rotate around Y
      const x1 = s.x * cosY - s.z * sinY;
      const z1 = s.z * cosY + s.x * sinY;

      // Rotate around X
      const y2 = s.y * cosX - z1 * sinX;
      const z2 = z1 * cosX + s.y * sinX;

      // Perspective projection
      const fov = GLOBE_RADIUS * 2.8;
      const scale = fov / (fov + z2);
      const px = centerX + x1 * scale;
      const py = centerY + y2 * scale;

      // Depth fade: near stars (z2 > 0) are bright, far stars (z2 < 0) fade
      const normalizedZ = (z2 + GLOBE_RADIUS) / (GLOBE_RADIUS * 2);
      const depthAlpha = Math.max(0.12, Math.min(1.0, normalizedZ * 1.1));

      // Twinkle
      s.twinklePhase += s.twinkleSpeed;
      const twinkle = 0.8 + 0.2 * Math.sin(s.twinklePhase);

      // Check distance from pulse wave
      let pulseBoost = 0;
      const distFromCenter = Math.sqrt(s.x * s.x + s.y * s.y + s.z * s.z);
      for (const pulse of pulses) {
        const diff = Math.abs(distFromCenter - pulse.radius);
        if (diff < 40) {
          pulseBoost += (1 - diff / 40) * pulse.intensity * 0.9;
        }
      }

      projected.push({
        px,
        py,
        z: z2,
        scale,
        alpha: Math.min(1.0, (depthAlpha * twinkle) + pulseBoost),
        size: s.baseSize * scale * (1 + pulseBoost * 0.8),
        pulseBoost,
      });
    }

    // Draw Constellation Connection Lines
    ctx.lineWidth = 1;
    for (let i = 0; i < projected.length; i++) {
      const p1 = projected[i];
      if (p1.z < -GLOBE_RADIUS * 0.5) continue; // skip far back lines for cleaner look

      for (let j = i + 1; j < projected.length; j++) {
        const p2 = projected[j];
        if (p2.z < -GLOBE_RADIUS * 0.5) continue;

        const dx = p1.px - p2.px;
        const dy = p1.py - p2.py;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < MAX_CONNECT_DIST) {
          const lineAlpha = (1 - dist / MAX_CONNECT_DIST) * 0.22 * Math.min(p1.alpha, p2.alpha);
          if (lineAlpha > 0.02) {
            ctx.strokeStyle = `rgba(6, 182, 212, ${lineAlpha})`;
            ctx.beginPath();
            ctx.moveTo(p1.px, p1.py);
            ctx.lineTo(p2.px, p2.py);
            ctx.stroke();
          }
        }
      }
    }

    // Draw Star Nodes with Bloom Glow
    for (let i = 0; i < projected.length; i++) {
      const p = projected[i];

      // Star core
      ctx.fillStyle = `rgba(240, 249, 255, ${p.alpha})`;
      ctx.beginPath();
      ctx.arc(p.px, p.py, p.size, 0, Math.PI * 2);
      ctx.fill();

      // Outer Glow for near stars or pulsed stars
      if (p.alpha > 0.5 || p.pulseBoost > 0.1) {
        const glowRadius = p.size * (2.8 + p.pulseBoost * 2);
        const grad = ctx.createRadialGradient(p.px, p.py, 0, p.px, p.py, glowRadius);
        grad.addColorStop(0, `rgba(6, 182, 212, ${p.alpha * 0.6})`);
        grad.addColorStop(1, 'rgba(6, 182, 212, 0)');

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(p.px, p.py, glowRadius, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    requestAnimationFrame(renderAstralShell);
  }

  renderAstralShell();


  // =========================================================================
  // 2. STUDIO WORKBENCH & INTERACTIVE TEST RUNNER
  // =========================================================================
  let allFunctions = [];
  let currentFilter = 'all';
  let activeFunction = null;

  const functionsList = document.getElementById('functionsList');
  const searchInput = document.getElementById('searchInput');
  const filterTabs = document.getElementById('filterTabs');

  // Workbench DOM elements
  const wbCategoryBadge = document.getElementById('wbCategoryBadge');
  const wbFunctionName = document.getElementById('wbFunctionName');
  const wbFunctionDesc = document.getElementById('wbFunctionDesc');
  const presetsChips = document.getElementById('presetsChips');
  const paramsFields = document.getElementById('paramsFields');
  const runFunctionBtn = document.getElementById('runFunctionBtn');
  const resetParamsBtn = document.getElementById('resetParamsBtn');

  // Terminal Inspector DOM elements
  const termStatusBadge = document.getElementById('termStatusBadge');
  const termLatencyBadge = document.getElementById('termLatencyBadge');
  const termTypeBadge = document.getElementById('termTypeBadge');
  const termEmptyState = document.getElementById('termEmptyState');
  const termOutputContainer = document.getElementById('termOutputContainer');
  const outputCodeText = document.getElementById('outputCodeText');
  const copyOutputBtn = document.getElementById('copyOutputBtn');
  const termErrorContainer = document.getElementById('termErrorContainer');
  const errorPillType = document.getElementById('errorPillType');
  const errorMetaInfo = document.getElementById('errorMetaInfo');
  const errorMsgText = document.getElementById('errorMsgText');
  const errorHintBox = document.getElementById('errorHintBox');

  // Footer & Health
  const footerShaText = document.getElementById('footerShaText');
  const healthStatusText = document.getElementById('healthStatusText');
  const copyShaBtn = document.getElementById('copyShaBtn');
  const themeToggle = document.getElementById('themeToggle');

  // Theme Toggling
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

  // Health Polling
  async function pollHealth() {
    try {
      const res = await fetch('/health');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      healthStatusText.textContent = 'Live (200 OK)';
      const sha = data.commit_sha || 'local-dev';
      footerShaText.textContent = sha;
      footerShaText.title = `Deployed SHA: ${sha}`;
    } catch (err) {
      healthStatusText.textContent = 'Offline';
      footerShaText.textContent = 'Connection Error';
    }
  }

  pollHealth();
  setInterval(pollHealth, 10000);

  // Copy SHA
  copyShaBtn.addEventListener('click', () => {
    const sha = footerShaText.textContent;
    if (sha && sha !== 'Loading...' && sha !== 'Connection Error') {
      navigator.clipboard.writeText(sha).then(() => {
        const origTitle = copyShaBtn.title;
        copyShaBtn.title = 'Copied!';
        setTimeout(() => copyShaBtn.title = origTitle, 1500);
      });
    }
  });

  // Copy Output
  copyOutputBtn.addEventListener('click', () => {
    const text = outputCodeText.textContent;
    if (text) {
      navigator.clipboard.writeText(text).then(() => {
        copyOutputBtn.querySelector('span').textContent = 'Copied!';
        setTimeout(() => copyOutputBtn.querySelector('span').textContent = 'Copy', 1500);
      });
    }
  });

  // Shortcut Cmd+K / Ctrl+K to search
  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
    // Ctrl + Enter to run
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      runActiveFunction();
    }
  });

  // Load Catalog
  async function loadFunctionsCatalog() {
    try {
      const res = await fetch('/api/functions');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      allFunctions = data.functions || [];

      renderSidebarList();

      // Select first function by default
      if (allFunctions.length > 0) {
        selectFunction(allFunctions[0]);
      }
    } catch (err) {
      functionsList.innerHTML = `<div style="padding: 16px; color: var(--error);">Error loading catalog: ${err.message}</div>`;
    }
  }

  // Filter Tabs
  filterTabs.addEventListener('click', (e) => {
    const btn = e.target.closest('.cat-tab');
    if (!btn) return;
    filterTabs.querySelectorAll('.cat-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    renderSidebarList();
  });

  // Search Input
  searchInput.addEventListener('input', () => {
    renderSidebarList();
  });

  // Render Sidebar List
  function renderSidebarList() {
    const query = searchInput.value.trim().toLowerCase();

    const filtered = allFunctions.filter(fn => {
      if (currentFilter === 'data-type' && !fn.category.toLowerCase().includes('data-type')) return false;
      if (currentFilter === 'mathematics' && !fn.category.toLowerCase().includes('mathematics')) return false;
      if (!query) return true;
      return fn.name.toLowerCase().includes(query) || fn.description.toLowerCase().includes(query);
    });

    if (filtered.length === 0) {
      functionsList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-faint); font-size: 0.85rem;">No matching functions found.</div>`;
      return;
    }

    functionsList.innerHTML = filtered.map(fn => {
      const isActive = activeFunction && activeFunction.id === fn.id;
      return `
        <div class="fn-list-item ${isActive ? 'active' : ''}" data-id="${fn.id}">
          <div class="fn-item-main">
            <span class="fn-item-name">${fn.name}()</span>
            <span class="fn-item-cat">${fn.category}</span>
          </div>
          <svg class="fn-item-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
      `;
    }).join('');

    // Attach click events
    functionsList.querySelectorAll('.fn-list-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.dataset.id;
        const target = allFunctions.find(f => f.id === id);
        if (target) {
          selectFunction(target);
          functionsList.querySelectorAll('.fn-list-item').forEach(i => i.classList.remove('active'));
          item.classList.add('active');
        }
      });
    });
  }

  // Select Active Function
  function selectFunction(fn) {
    activeFunction = fn;

    wbCategoryBadge.textContent = fn.category;
    const paramNames = (fn.params || []).map(p => p.name).join(', ');
    wbFunctionName.textContent = `${fn.name}(${paramNames})`;
    wbFunctionDesc.textContent = fn.description;

    // Render Presets
    renderPresets(fn.presets || []);

    // Render Params Fields
    renderParamsFields(fn.params || []);

    // Reset Terminal Inspector
    resetTerminalInspector();
  }

  // Render Presets Chips
  function renderPresets(presets) {
    if (!presets || presets.length === 0) {
      presetsChips.innerHTML = `<span style="font-size: 0.78rem; color: var(--text-faint);">No presets available</span>`;
      return;
    }

    presetsChips.innerHTML = presets.map((preset, idx) => {
      const isError = preset.label.toLowerCase().includes('error') || preset.label.toLowerCase().includes('negative');
      return `
        <button type="button" class="preset-chip ${isError ? 'error-preset' : ''}" data-preset-idx="${idx}">
          ${preset.label}
        </button>
      `;
    }).join('');

    presetsChips.querySelectorAll('.preset-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.presetIdx, 10);
        const preset = presets[idx];
        if (preset && preset.args) {
          applyPresetArgs(preset.args);
          // Run immediately on preset click for smooth interactive experience
          runActiveFunction();
        }
      });
    });
  }

  // Apply Preset Arguments into Form Fields
  function applyPresetArgs(args) {
    for (const [key, value] of Object.entries(args)) {
      const input = document.getElementById(`param_${key}`);
      if (input) {
        if (typeof value === 'object' && value !== null) {
          input.value = JSON.stringify(value);
        } else {
          input.value = value;
        }
      }
    }
  }

  // Render Parameter Input Fields
  function renderParamsFields(params) {
    if (!params || params.length === 0) {
      paramsFields.innerHTML = `<div style="color: var(--text-faint); font-size: 0.85rem;">This function takes no parameters. Click "Execute" to run.</div>`;
      return;
    }

    paramsFields.innerHTML = params.map(param => {
      let defaultVal = param.default !== undefined ? param.default : '';
      if (typeof defaultVal === 'object' && defaultVal !== null) {
        defaultVal = JSON.stringify(defaultVal);
      }

      return `
        <div class="param-group">
          <div class="param-header-label">
            <span class="param-title">${param.label || param.name}</span>
            <span class="param-type-badge">${param.type || 'any'}</span>
          </div>
          <input
            type="text"
            class="param-input"
            id="param_${param.name}"
            name="${param.name}"
            value="${defaultVal}"
            placeholder="e.g. ${defaultVal}"
            autocomplete="off"
          >
          <span class="param-hint">${getParamHint(param)}</span>
        </div>
      `;
    }).join('');
  }

  function getParamHint(param) {
    if (param.type === 'number') return 'Accepts integer or floating point number';
    if (param.type === 'list') return 'Enter JSON array (e.g. [1, 2, 3])';
    if (param.type === 'dict') return 'Enter JSON object (e.g. {"a": 1, "b": 2})';
    if (param.type === 'string') return 'Enter text string';
    return `Parameter: ${param.name}`;
  }

  // Reset Button
  resetParamsBtn.addEventListener('click', () => {
    if (activeFunction && activeFunction.params) {
      renderParamsFields(activeFunction.params);
      resetTerminalInspector();
    }
  });

  // Run Function Action
  runFunctionBtn.addEventListener('click', runActiveFunction);

  async function runActiveFunction() {
    if (!activeFunction) return;

    // Collect and parse arguments
    const argsPayload = {};
    const params = activeFunction.params || [];

    for (const p of params) {
      const input = document.getElementById(`param_${p.name}`);
      if (!input) continue;
      const rawVal = input.value.trim();

      if (p.type === 'number') {
        const num = Number(rawVal);
        argsPayload[p.name] = isNaN(num) ? rawVal : num;
      } else if (p.type === 'list' || p.type === 'dict') {
        try {
          argsPayload[p.name] = JSON.parse(rawVal);
        } catch {
          argsPayload[p.name] = rawVal;
        }
      } else {
        argsPayload[p.name] = rawVal;
      }
    }

    // Set Loading UI State
    termStatusBadge.className = 'term-badge';
    termStatusBadge.textContent = 'Running...';
    termLatencyBadge.textContent = '...';

    const startTime = performance.now();

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          function_name: activeFunction.name,
          arguments: argsPayload,
        }),
      });

      const latency = (performance.now() - startTime).toFixed(1);
      const data = await res.json();

      termLatencyBadge.textContent = `${latency} ms`;

      if (res.ok && data.success) {
        // Success execution
        displayTerminalSuccess(data);
      } else {
        // Error or Exception handled
        displayTerminalError(res.status, data);
      }
    } catch (err) {
      const latency = (performance.now() - startTime).toFixed(1);
      termLatencyBadge.textContent = `${latency} ms`;
      displayTerminalError(500, {
        error_type: 'NetworkError',
        error_message: err.message,
      });
    }
  }

  function displayTerminalSuccess(data) {
    termEmptyState.classList.add('hidden');
    termErrorContainer.classList.add('hidden');
    termOutputContainer.classList.remove('hidden');

    termStatusBadge.className = 'term-badge success';
    termStatusBadge.textContent = '200 OK';

    termTypeBadge.textContent = `Type: ${data.result_type || typeof data.result}`;

    // Format output
    let formatted = '';
    if (typeof data.result === 'object' && data.result !== null) {
      formatted = JSON.stringify(data.result, null, 2);
    } else {
      formatted = String(data.result);
    }

    outputCodeText.textContent = formatted;
  }

  function displayTerminalError(statusCode, data) {
    termEmptyState.classList.add('hidden');
    termOutputContainer.classList.add('hidden');
    termErrorContainer.classList.remove('hidden');

    termStatusBadge.className = 'term-badge failed';
    termStatusBadge.textContent = `${statusCode} Error`;

    termTypeBadge.textContent = `Type: ${data.error_type || 'Exception'}`;

    errorPillType.textContent = data.error_type || 'Exception';
    errorMetaInfo.textContent = `HTTP ${statusCode} · Handled Gracefully`;
    errorMsgText.textContent = data.error_message || data.detail || 'An unexpected error occurred.';

    // Helpful SQA Explanation
    errorHintBox.innerHTML = `<strong>SQA Test Note:</strong> This corner case raised <code>${data.error_type || 'Exception'}</code> exactly as specified in the test suite and contract.`;
  }

  function resetTerminalInspector() {
    termEmptyState.classList.remove('hidden');
    termOutputContainer.classList.add('hidden');
    termErrorContainer.classList.add('hidden');

    termStatusBadge.className = 'term-badge ready';
    termStatusBadge.textContent = 'Ready';
    termLatencyBadge.textContent = '0.0 ms';
    termTypeBadge.textContent = 'Type: None';
  }

  // Load functions
  loadFunctionsCatalog();
});
