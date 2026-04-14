/* ═══════════════════════════════════════════════════════════════════════════
   GUARDRAILS LOCAL RAG BOT — Frontend Logic
   ═══════════════════════════════════════════════════════════════════════════ */
'use strict';

const API_BASE = window.location.origin;

// ─── Default Ollama endpoint ──────────────────────────────────────────────────
const DEFAULT_OLLAMA_ENDPOINT = 'http://localhost:11434';

// ─── App state ────────────────────────────────────────────────────────────────
const state = {
  sessionId: null,
  ollamaRunning: false,
  models: [],
  selectedFiles: [],
  isProcessing: false,
  isChatting: false,
  uploadOpen: true,
  currentDbId: null,
  serverConfig: null,
};

// ─── DOM refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const sidebar = $('sidebar');
const sidebarBackdrop = $('sidebarBackdrop');
const sidebarOpen = $('sidebarOpen');
const sidebarClose = $('sidebarClose');
const sidebarCollapseBtn = $('sidebarCollapseBtn');
const sidebarExpandBtn = $('sidebarExpandBtn');
const sidebarBody = $('sidebarBody');
const sidebarRail = $('sidebarRail');
const railStatusDot = $('railStatusDot');
const railClearBtn = $('railClearBtn');

const ollamaEndpointInput = $('ollamaEndpoint');
const ollamaStatus = $('ollamaStatus');
const ollamaStatusText = $('ollamaStatusText');
const btnStartOllama = $('btnStartOllama');
const railStartOllama = $('railStartOllama');
const startOllamaHint = $('startOllamaHint');
const providerSelect = $('providerSelect');
const providerEndpointGroup = $('providerEndpointGroup');
const providerApiKeyGroup = $('providerApiKeyGroup');
const apiKeyInput = $('apiKey');
const modelSelect = $('modelSelect');
const connectionBadge = $('connectionBadge');

const guardrailsToggle = $('guardrailsToggle');
const sensitivitySelect = $('sensitivitySelect');
const sensitivityBadge = $('sensitivityBadge');
const sensitivityBadgeLabel = $('sensitivityBadgeLabel');
const sensitivityDesc = $('sensitivityDesc');
const sensitivityHint = $('sensitivityHint');
const guardrailsIndicator = $('guardrailsIndicator');

const chunkSize = $('chunkSize');
const chunkOverlap = $('chunkOverlap');

const storagePool = $('storagePool');
const storageEmpty = $('storageEmpty');
const btnRefreshStorage = $('btnRefreshStorage');

const fileInput = $('fileInput');
const fileList = $('fileList');
const btnProcess = $('btnProcess');
const btnReset = $('btnReset');
const uploadStatus = $('uploadStatus');
const dropZone = $('dropZone');
const dropClick = $('dropClick');

const emptyState = $('emptyState');
const chatMessages = $('chatMessages');
const chatSection = $('chatSection');
const readyBanner = $('readyBanner');
const inputBarWrapper = $('inputBarWrapper');
const typingIndicator = $('typingIndicator');
const chatInput = $('chatInput');
const btnSend = $('btnSend');
const btnClear = $('btnClear');
const toastContainer = $('toastContainer');

const tunnelModal = $('tunnelModal');
const tunnelModalClose = $('tunnelModalClose');

const ollamaStartModal = $('ollamaStartModal');
const ollamaStartModalClose = $('ollamaStartModalClose');
const ollamaStartRetry = $('ollamaStartRetry');

// ─── Ollama endpoint (stored in localStorage) ─────────────────────────────────
function getOllamaEndpoint() {
  return (ollamaEndpointInput.value || '').trim() || DEFAULT_OLLAMA_ENDPOINT;
}

/**
 * Fetch server-side config (/api/config).
 * - If the user has never saved a custom endpoint, we use the server's OLLAMA_HOST.
 * - If the user previously saved a custom endpoint in localStorage, we keep it.
 * - The server config is cached in state.serverConfig for later use.
 */
async function fetchConfig() {
  try {
    const cfg = await apiFetch('/api/config');
    state.serverConfig = cfg;
    // Only auto-apply server host if user hasn't manually overridden it
    const saved = localStorage.getItem('ragbot_ollama_endpoint');
    const userOverrode = saved && saved !== DEFAULT_OLLAMA_ENDPOINT;
    if (!userOverrode && cfg.server_ollama_host) {
      // Server has a non-default host configured (e.g. ngrok tunnel)
      ollamaEndpointInput.value = cfg.server_ollama_host;
      localStorage.setItem('ragbot_ollama_endpoint', cfg.server_ollama_host);
    } else {
      // User's choice wins — restore from localStorage
      loadSavedEndpoint();
    }
  } catch {
    // Config fetch failed (offline?) — just restore whatever was saved
    loadSavedEndpoint();
  }
}

function loadSavedEndpoint() {
  const saved = localStorage.getItem('ragbot_ollama_endpoint');
  if (saved) ollamaEndpointInput.value = saved;
  else ollamaEndpointInput.value = DEFAULT_OLLAMA_ENDPOINT;
}

ollamaEndpointInput.addEventListener('change', () => {
  const val = ollamaEndpointInput.value.trim();
  localStorage.setItem('ragbot_ollama_endpoint', val || DEFAULT_OLLAMA_ENDPOINT);
  // Re-check health immediately when endpoint changes
  refreshHealth();
});

// Show tunnel modal when endpoint looks remote (not localhost)
ollamaEndpointInput.addEventListener('blur', () => {
  const val = (ollamaEndpointInput.value || '').trim();
  const isLocal = !val || val.includes('localhost') || val.includes('127.0.0.1');
  if (!isLocal && val) {
    // No-op: just silently accept remote URLs. Modal is shown from the hint link.
  }
});

// ─── Provider logic ──────────────────────────────────────────────────────────
const PRESET_MODELS = {
  ollama: [],
  openai: ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-5-sonnet-20240620'],
  gemini: ['gemini-1.5-flash', 'gemini-1.5-pro']
};

function getProvider() {
  return providerSelect.value;
}

function getApiKey() {
  return apiKeyInput.value.trim();
}

providerSelect.addEventListener('change', () => {
  const p = getProvider();
  if (p === 'ollama') {
    providerEndpointGroup.style.display = '';
    providerApiKeyGroup.style.display = 'none';
    ollamaStatus.style.display = '';
    refreshHealth();
  } else {
    providerEndpointGroup.style.display = 'none';
    providerApiKeyGroup.style.display = '';
    ollamaStatus.style.display = 'none';
    btnStartOllama.style.display = 'none';
    if (railStartOllama) railStartOllama.style.display = 'none';
    if (startOllamaHint) startOllamaHint.style.display = 'none';
    
    // Set cloud badge
    connectionBadge.textContent = p.toUpperCase() + ' CLOUD';
    connectionBadge.style.filter = 'none';
    connectionBadge.style.color = 'var(--accent-hover)';
    connectionBadge.style.borderColor = 'var(--accent-border)';
    connectionBadge.style.background = 'var(--accent-dim)';

    // Set preset models
    modelSelect.innerHTML = '';
    PRESET_MODELS[p].forEach(m => {
      const opt = document.createElement('option');
      opt.value = m; opt.textContent = m;
      modelSelect.appendChild(opt);
    });
  }
});

// ─── Utility ──────────────────────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const res = await fetch(API_BASE + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function toast(msg, type = 'info', duration = 3400) {
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  toastContainer.appendChild(el);
  setTimeout(() => {
    el.style.animation = 'toastOut 0.22s ease forwards';
    el.addEventListener('animationend', () => el.remove(), { once: true });
  }, duration);
}

// ─── Tunnel modal ─────────────────────────────────────────────────────────────
tunnelModalClose.addEventListener('click', () => { tunnelModal.style.display = 'none'; });
tunnelModal.addEventListener('click', e => { if (e.target === tunnelModal) tunnelModal.style.display = 'none'; });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && tunnelModal.style.display !== 'none') tunnelModal.style.display = 'none';
  if (e.key === 'Escape' && ollamaStartModal && ollamaStartModal.style.display !== 'none') {
    ollamaStartModal.style.display = 'none';
    if (_ollamaPoller) { clearInterval(_ollamaPoller); _ollamaPoller = null; }
  }
});

// ─── Start Ollama modal ───────────────────────────────────────────────────────
if (ollamaStartModalClose) {
  ollamaStartModalClose.addEventListener('click', () => {
    ollamaStartModal.style.display = 'none';
    if (_ollamaPoller) { clearInterval(_ollamaPoller); _ollamaPoller = null; }
  });
}
if (ollamaStartModal) {
  ollamaStartModal.addEventListener('click', e => {
    if (e.target === ollamaStartModal) {
      ollamaStartModal.style.display = 'none';
      if (_ollamaPoller) { clearInterval(_ollamaPoller); _ollamaPoller = null; }
    }
  });
}
if (ollamaStartRetry) {
  ollamaStartRetry.addEventListener('click', async () => {
    ollamaStartRetry.disabled = true;
    ollamaStartRetry.innerHTML = '<span class="btn-spinner"></span> Checking…';
    const { running } = await checkOllamaDirectly(getOllamaEndpoint());
    if (running) {
      if (_ollamaPoller) { clearInterval(_ollamaPoller); _ollamaPoller = null; }
      ollamaStartModal.style.display = 'none';
      await refreshHealth();
      toast('Ollama is now running!', 'success');
    } else {
      toast('Ollama not detected yet — make sure you ran the command above.', 'warn', 4000);
      ollamaStartRetry.disabled = false;
      ollamaStartRetry.innerHTML = 'Check Again';
    }
  });
}

// ─── SIDEBAR — Tabs ──────────────────────────────────────────────────────────
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    
    // Update buttons
    tabBtns.forEach(b => b.classList.toggle('active', b === btn));
    
    // Update content
    tabContents.forEach(content => {
      content.classList.toggle('active', content.id === `tab-${tab}`);
    });
  });
});

function updateActiveModelLabel() {
  const model = modelSelect.value;
  const p = getProvider();
  const label = $('activeModelLabel');
  if (label) {
    if (model) {
      label.innerHTML = `<span style="color:var(--accent)">${p.toUpperCase()}</span> &middot; ${model}`;
    } else {
      label.textContent = 'No model active';
    }
  }
}

modelSelect.addEventListener('change', updateActiveModelLabel);
providerSelect.addEventListener('change', updateActiveModelLabel);

// ─── SIDEBAR — Mobile drawer ───────────────────────────────────────────────────
function openMobileSidebar() {
  sidebar.classList.add('open');
  sidebarBackdrop.classList.add('visible');
  sidebarOpen.setAttribute('aria-expanded', 'true');
}
function closeMobileSidebar() {
  sidebar.classList.remove('open');
  sidebarBackdrop.classList.remove('visible');
  sidebarOpen.setAttribute('aria-expanded', 'false');
}

sidebarOpen.addEventListener('click', openMobileSidebar);
sidebarClose.addEventListener('click', closeMobileSidebar);
sidebarBackdrop.addEventListener('click', closeMobileSidebar);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && sidebar.classList.contains('open')) closeMobileSidebar();
});

// ─── SIDEBAR — Desktop collapse / expand ──────────────────────────────────────
function collapseSidebar() {
  state.sidebarCollapsed = true;
  sidebar.classList.add('collapsed');
  sidebarExpandBtn.style.display = 'flex';
  sidebarCollapseBtn.setAttribute('aria-label', 'Expand sidebar');
  syncRailStatus();
}

function expandSidebar() {
  state.sidebarCollapsed = false;
  sidebar.classList.remove('collapsed');
  sidebarExpandBtn.style.display = 'none';
  sidebarCollapseBtn.setAttribute('aria-label', 'Collapse sidebar');
}

if (sidebarCollapseBtn) sidebarCollapseBtn.addEventListener('click', collapseSidebar);
if (sidebarExpandBtn) sidebarExpandBtn.addEventListener('click', expandSidebar);

if (railStartOllama) {
  railStartOllama.addEventListener('click', () => btnStartOllama.click());
}

if (railClearBtn) { railClearBtn.addEventListener('click', clearConversation); }

function syncRailStatus() {
  if (!railStatusDot) return;
  railStatusDot.className = 'status-dot';
  if (state.ollamaRunning) {
    railStatusDot.style.background = 'var(--accent)';
    railStatusDot.style.boxShadow = '0 0 5px var(--accent)';
  } else {
    railStatusDot.style.background = 'var(--danger)';
    railStatusDot.style.boxShadow = '0 0 5px var(--danger)';
  }
}

// ─── SIDEBAR — Mobile drawer ───────────────────────────────────────────────────
function openMobileSidebar() {
  sidebar.classList.add('open');
  sidebarBackdrop.classList.add('visible');
  sidebarOpen.setAttribute('aria-expanded', 'true');
}

// ─── OLLAMA HEALTH — checked directly from the browser (client → localhost) ────
// The browser pings Ollama directly. This works even when the app is hosted
// on Railway because Ollama allows cross-origin requests from any page.
// The backend is NOT used as a proxy here — that way the status always
// reflects whether Ollama is running on THIS user's machine.
async function checkOllamaDirectly(endpoint) {
  try {
    const url = endpoint.replace(/\/$/, '') + '/api/tags';
    // Ollama's CORS headers allow browser fetches from any origin
    const res = await fetch(url, { method: 'GET', signal: AbortSignal.timeout(3000) });
    if (!res.ok) return { running: false, models: [] };
    const data = await res.json();
    return {
      running: true,
      models: (data.models || []).map(m => m.name),
    };
  } catch {
    return { running: false, models: [] };
  }
}

async function refreshHealth() {
  const p = getProvider();
  if (p !== 'ollama') return;

  const endpoint = getOllamaEndpoint();
  const isLocal = endpoint.includes('localhost') || endpoint.includes('127.0.0.1');

  // Set loading state briefly if we were offline
  if (!state.ollamaRunning) {
    ollamaStatus.className = 'status-badge status-loading';
    ollamaStatusText.textContent = 'Checking Connection…';
  }

  const { running, models } = await checkOllamaDirectly(endpoint);

  // Update state
  const changed = state.ollamaRunning !== running;
  state.ollamaRunning = running;
  state.models = models;

  if (running) {
    ollamaStatus.className = 'status-badge status-online';
    ollamaStatusText.textContent = isLocal ? 'Ollama — Running' : 'Ollama — Connected';

    // Hide start buttons
    btnStartOllama.style.display = 'none';
    if (railStartOllama) railStartOllama.style.display = 'none';
    if (startOllamaHint) startOllamaHint.style.display = 'none';

    // Update badge in header
    connectionBadge.textContent = isLocal ? 'LOCAL / SECURE' : 'REMOTE / TUNNEL';
    connectionBadge.style.filter = 'none';
    connectionBadge.style.color = 'var(--accent-hover)';
    connectionBadge.style.borderColor = 'var(--accent-border)';
    connectionBadge.style.background = 'var(--accent-dim)';

    // Update model list
    const currentModel = modelSelect.value;
    modelSelect.innerHTML = '';

    if (models.length === 0) {
      const opt = document.createElement('option');
      opt.value = ''; opt.textContent = 'No models found'; opt.disabled = true; opt.selected = true;
      modelSelect.appendChild(opt);
    } else {
      models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m; opt.textContent = m;
        if (m === currentModel) opt.selected = true;
        modelSelect.appendChild(opt);
      });
      // If gemma3 exists but isn't selected, maybe select it? 
      // User manual choice is better, but let's ensure something is selected.
      if (!modelSelect.value && models.length > 0) modelSelect.selectedIndex = 0;
    }

    if (changed) toast('Ollama connection established.', 'success');
  } else {
    ollamaStatus.className = 'status-badge status-offline';
    ollamaStatusText.textContent = isLocal ? 'Ollama — Not running' : 'Ollama — Unreachable';

    btnStartOllama.style.display = 'flex';
    if (railStartOllama) railStartOllama.style.display = 'flex';

    if (startOllamaHint) {
      startOllamaHint.style.display = 'block';
      startOllamaHint.textContent = isLocal
        ? 'Ollama is offline. Click above to try starting it.'
        : 'Remote server unreachable. Check URL or tunnel.';
    }

    connectionBadge.textContent = 'OFFLINE';
    connectionBadge.style.filter = 'none';
    connectionBadge.style.color = '';
    connectionBadge.style.borderColor = '';
    connectionBadge.style.background = '';
  }
  syncRailStatus();
}

// ─── START OLLAMA — shows instructions & polls until Ollama comes online ─────
// Browsers cannot spawn OS processes, so we show the command to run and
// keep retrying until Ollama responds at the user's localhost.
btnStartOllama.addEventListener('click', async () => {
  const endpoint = getOllamaEndpoint();
  const isLocal = endpoint.includes('localhost') || endpoint.includes('127.0.0.1');

  if (!isLocal) {
    tunnelModal.style.display = 'flex';
    return;
  }

  // Attempt to start via backend first
  btnStartOllama.disabled = true;
  if (railStartOllama) railStartOllama.classList.add('loading');
  btnStartOllama.innerHTML = '<span class="btn-spinner"></span> Starting…';

  try {
    toast('Telling backend to start Ollama...', 'info');
    const data = await apiFetch('/api/ollama/start', { method: 'POST' });
    if (data.started) {
      toast('Ollama starting! Waiting to connect...', 'success');
      // Wait a moment for it to actually bind the port
      setTimeout(async () => {
        await refreshHealth();
        if (state.ollamaRunning) {
          btnStartOllama.disabled = false;
          if (railStartOllama) railStartOllama.classList.remove('loading');
          btnStartOllama.innerHTML = '🚀 LAUNCH OLLAMA';
        } else {
          // If still not running, show instructions modal
          showOllamaStartModal(endpoint);
        }
      }, 1500);
    }
  } catch (e) {
    console.warn('Backend start failed:', e);
    // If backend fails (e.g. not on the same machine), show manual instructions
    showOllamaStartModal(endpoint);
  } finally {
    // Reset button after a delay if modal didn't close
    setTimeout(() => {
      btnStartOllama.disabled = false;
      if (railStartOllama) railStartOllama.classList.remove('loading');
      btnStartOllama.innerHTML = '🚀 LAUNCH OLLAMA';
    }, 3000);
  }
});

function showOllamaStartModal(endpoint) {
  const epLabel = document.getElementById('ollamaStartModalEndpoint');
  if (epLabel) epLabel.textContent = endpoint;
  ollamaStartModal.style.display = 'flex';
  startOllamaPoller();
}

// Poll every 2 s until Ollama comes online (called after modal is shown)
let _ollamaPoller = null;
function startOllamaPoller() {
  if (_ollamaPoller) return; // already polling
  _ollamaPoller = setInterval(async () => {
    const endpoint = getOllamaEndpoint();
    const { running } = await checkOllamaDirectly(endpoint);
    if (running) {
      clearInterval(_ollamaPoller); _ollamaPoller = null;
      ollamaStartModal.style.display = 'none';
      await refreshHealth();
      toast('Ollama is now running!', 'success');
    }
  }, 2000);
}

// ─── SENSITIVITY / GUARDRAILS ─────────────────────────────────────────────────
const SENSITIVITY_META = {
  Public: { badge: 'badge-public', hint: 'No extra filters — jailbreak protection only.' },
  Internal: { badge: 'badge-internal', hint: '🛡 <strong>Internal</strong> — API keys &amp; credentials protected.' },
  Confidential: { badge: 'badge-confidential', hint: '🛡 <strong>Confidential</strong> — PII (SSN, email, phone) protected.' },
  Restricted: { badge: 'badge-restricted', hint: '🛡 <strong>Restricted</strong> — Medical, financial, HIPAA/GDPR protected.' },
};
const SENSITIVITY_DESC = {
  Public: 'No data classification restrictions. Basic jailbreak protection only.',
  Internal: 'Suitable for internal business data. Blocks credential and API key exposure.',
  Confidential: 'For confidential data. Adds PII protection (emails, phone, SSNs).',
  Restricted: 'Maximum protection for HIPAA/GDPR/financial data.',
};

function updateSensitivityUI() {
  const level = sensitivitySelect.value;
  const meta = SENSITIVITY_META[level];
  sensitivityBadge.className = `sensitivity-badge ${meta.badge}`;
  sensitivityBadgeLabel.textContent = level.toUpperCase();
  sensitivityDesc.textContent = SENSITIVITY_DESC[level];
  sensitivityHint.innerHTML = guardrailsToggle.checked ? meta.hint : '⚪ Guardrails disabled.';
}

sensitivitySelect.addEventListener('change', updateSensitivityUI);
guardrailsToggle.addEventListener('change', () => {
  sensitivitySelect.disabled = !guardrailsToggle.checked;
  guardrailsIndicator.classList.toggle('active', guardrailsToggle.checked);
  updateSensitivityUI();
});

// ─── STORAGE POOL (Document Library) ─────────────────────────────────────────
async function loadStoragePool() {
  storageEmpty.textContent = 'Loading…';
  storageEmpty.style.display = 'block';
  // Remove old collection cards
  storagePool.querySelectorAll('.storage-card').forEach(c => c.remove());

  try {
    const data = await apiFetch('/api/storage');
    const collections = data.collections || [];

    if (collections.length === 0) {
      storageEmpty.textContent = 'No indexed collections yet.';
      return;
    }

    storageEmpty.style.display = 'none';

    collections.forEach(col => {
      const card = document.createElement('div');
      card.className = 'storage-card' + (col.available ? '' : ' unavailable');
      card.dataset.dbId = col.db_id;

      const names = col.files.join(', ') || 'Unknown files';
      const date = col.created_at ? new Date(col.created_at).toLocaleDateString() : '—';

      card.innerHTML = `
        <div class="storage-card-header">
          <span class="storage-card-name" title="${escapeHtml(names)}">${escapeHtml(truncate(names, 34))}</span>
          <button class="storage-del-btn" data-db-id="${col.db_id}" title="Delete this collection" aria-label="Delete">✕</button>
        </div>
        <div class="storage-card-meta">
          <span class="storage-meta-tag">${col.model || '?'}</span>
          <span class="storage-meta-tag">${date}</span>
          ${!col.available ? '<span class="storage-meta-tag unavail">⚠ Missing</span>' : ''}
        </div>
        <button class="btn btn-secondary storage-load-btn" data-db-id="${col.db_id}" ${!col.available ? 'disabled' : ''}>
          ↩ Load Session
        </button>
      `;

      card.querySelector('.storage-load-btn').addEventListener('click', () => loadStoredSession(col));
      card.querySelector('.storage-del-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        deleteStoredSession(col.db_id, card);
      });

      storagePool.appendChild(card);
    });
  } catch (e) {
    storageEmpty.textContent = `Error loading library: ${e.message}`;
  }
}

async function loadStoredSession(col) {
  const p = getProvider();
  if (p === 'ollama' && !state.ollamaRunning) {
    toast('Ollama is not connected. Set the endpoint in the sidebar.', 'error');
    return;
  }
  if (p !== 'ollama' && !getApiKey()) {
    toast('Please enter your API key in the sidebar.', 'error');
    return;
  }

  // Highlight active card
  storagePool.querySelectorAll('.storage-card').forEach(c => c.classList.remove('active'));
  const card = storagePool.querySelector(`[data-db-id="${col.db_id}"]`);
  if (card) {
    card.classList.add('active');
    card.querySelector('.storage-load-btn').textContent = '⏳ Loading…';
    card.querySelector('.storage-load-btn').disabled = true;
  }

  try {
    const data = await apiFetch('/api/sessions/load', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        db_id: col.db_id,
        model: modelSelect.value,
        provider: getProvider(),
        api_key: getApiKey(),
        ollama_host: getOllamaEndpoint(),
      }),
    });

    state.sessionId = data.session_id;
    state.currentDbId = col.db_id;

    // Update upload status text
    setUploadStatus(`✓ Loaded: ${data.files.join(', ')}`, 'success');
    toast(`Loaded "${data.files.join(', ')}" from library.`, 'success');
    showChatReady();
    if (window.innerWidth <= 900) closeMobileSidebar();
  } catch (e) {
    toast(`Failed to load: ${e.message}`, 'error', 6000);
    if (card) {
      card.classList.remove('active');
      card.querySelector('.storage-load-btn').textContent = '↩ Load Session';
      card.querySelector('.storage-load-btn').disabled = false;
    }
  }
}

async function deleteStoredSession(dbId, cardEl) {
  if (!confirm('Delete this indexed collection from disk? This cannot be undone.')) return;
  try {
    await apiFetch('/api/storage/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ db_id: dbId }),
    });
    cardEl.style.animation = 'toastOut 0.2s ease forwards';
    setTimeout(() => { cardEl.remove(); checkStorageEmpty(); }, 220);
    toast('Collection deleted.', 'info');
  } catch (e) {
    toast(`Delete failed: ${e.message}`, 'error');
  }
}

function checkStorageEmpty() {
  if (!storagePool.querySelector('.storage-card')) {
    storageEmpty.textContent = 'No indexed collections yet.';
    storageEmpty.style.display = 'block';
  }
}

btnRefreshStorage.addEventListener('click', loadStoragePool);

// ─── FILE HANDLING ────────────────────────────────────────────────────────────
const getExt = name => name.split('.').pop().toLowerCase();
const truncate = (s, n) => s.length > n ? s.slice(0, n) + '…' : s;

function renderFileList() {
  const n = state.selectedFiles.length;
  if (n === 0) {
    fileList.style.display = 'none';
    btnProcess.disabled = true;
    btnReset.style.display = 'none';
    uploadFileCount.style.display = 'none';
    return;
  }
  fileList.style.display = 'flex';
  btnProcess.disabled = false;
  btnReset.style.display = 'inline-flex';
  uploadFileCount.textContent = `${n} file${n > 1 ? 's' : ''}`;
  uploadFileCount.style.display = 'inline-flex';

  fileList.innerHTML = '';
  state.selectedFiles.forEach(f => {
    const chip = document.createElement('div');
    chip.className = 'file-chip';
    chip.setAttribute('role', 'listitem');
    chip.innerHTML = `<span class="ext-tag">${getExt(f.name)}</span>${f.name}`;
    fileList.appendChild(chip);
  });
}

function addFiles(files) {
  const allowed = new Set(['pdf', 'txt', 'doc', 'docx']);
  const incoming = Array.from(files);
  const valid = incoming.filter(f => allowed.has(getExt(f.name)));
  if (valid.length < incoming.length) toast('Some files skipped (unsupported format).', 'warn');
  const names = new Set(state.selectedFiles.map(f => f.name));
  valid.filter(f => !names.has(f.name)).forEach(f => state.selectedFiles.push(f));
  renderFileList();
}

const homeDropZone = $('homeDropZone');

// Add files handler
function handleDrop(e) {
  e.preventDefault();
  const dz = e.currentTarget;
  dz.classList.remove('drag-over');
  addFiles(e.dataTransfer.files);
  
  // If dropped in the home zone, switch to docs tab so user sees the progress
  if (dz.id === 'homeDropZone') {
    const docsTabBtn = document.querySelector('.tab-btn[data-tab="docs"]');
    if (docsTabBtn) docsTabBtn.click();
  }
}

function handleDragOver(e) {
  e.preventDefault();
  e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
  if (!e.currentTarget.contains(e.relatedTarget)) {
    e.currentTarget.classList.remove('drag-over');
  }
}

[dropZone, homeDropZone].forEach(dz => {
  if (!dz) return;
  dz.addEventListener('dragover', handleDragOver);
  dz.addEventListener('dragleave', handleDragLeave);
  dz.addEventListener('drop', handleDrop);
  if (dz.id === 'homeDropZone') {
    dz.addEventListener('click', () => fileInput.click());
  }
});

dropZone.addEventListener('click', () => fileInput.click());
dropClick.addEventListener('click', e => { e.stopPropagation(); fileInput.click(); });
fileInput.addEventListener('change', () => { addFiles(fileInput.files); fileInput.value = ''; });

btnReset.addEventListener('click', () => {
  state.selectedFiles = [];
  state.sessionId = null;
  state.currentDbId = null;
  renderFileList();
  setUploadStatus('');
  showEmptyState();
});

// ─── UPLOAD / PROCESS ─────────────────────────────────────────────────────────
function setUploadStatus(msg, type = '') {
  uploadStatus.textContent = msg;
  uploadStatus.className = `upload-status ${type}`.trim();
}

btnProcess.addEventListener('click', processDocuments);

async function processDocuments() {
  if (state.isProcessing || !state.selectedFiles.length) return;
  const p = getProvider();
  if (p === 'ollama' && !state.ollamaRunning) {
    toast('Ollama is not running. Set the Ollama Endpoint in the sidebar.', 'error');
    return;
  }
  if (p !== 'ollama' && !getApiKey()) {
    toast('Please enter your API key in the sidebar.', 'error');
    return;
  }

  state.isProcessing = true;
  btnProcess.disabled = true;
  btnReset.disabled = true;
  setUploadStatus('⏳ Embedding documents — please wait…', 'loading');

  const form = new FormData();
  state.selectedFiles.forEach(f => form.append('files', f));
  form.append('model', modelSelect.value);
  form.append('provider', getProvider());
  form.append('api_key', getApiKey());
  form.append('chunk_size', chunkSize.value);
  form.append('chunk_overlap', chunkOverlap.value);
  form.append('ollama_host', getOllamaEndpoint());

  try {
    const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    state.sessionId = data.session_id;
    state.currentDbId = data.db_id;
    setUploadStatus(`${data.files.length} document(s) indexed.`, 'success');
    toast('Documents ready — start chatting!', 'success');
    showChatReady();
    // Refresh the library so the new collection appears
    await loadStoragePool();
  } catch (e) {
    setUploadStatus(`✗ ${e.message}`, 'error');
    toast(e.message, 'error', 6000);
  } finally {
    state.isProcessing = false;
    btnProcess.disabled = false;
    btnReset.disabled = false;
  }
}

// ─── CHAT STATE TRANSITIONS ───────────────────────────────────────────────────
function showEmptyState() {
  emptyState.style.display = '';
  chatMessages.style.display = 'none';
  readyBanner.style.display = 'none';
  typingIndicator.style.display = 'none';
  inputBarWrapper.style.display = 'none';
  chatInput.disabled = true;
  btnSend.disabled = true;
  chatMessages.innerHTML = '';
}

function showChatReady() {
  emptyState.style.display = 'none';
  chatMessages.style.display = 'flex';
  readyBanner.style.display = 'flex';
  inputBarWrapper.style.display = 'block';
  chatInput.disabled = false;
  btnSend.disabled = false;
  requestAnimationFrame(() => chatInput.focus());
}

// ─── CLEAR CONVERSATION ───────────────────────────────────────────────────────
async function clearConversation() {
  if (state.sessionId) {
    try {
      await apiFetch('/api/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: state.sessionId }),
      });
    } catch { /* best-effort */ }
  }
  chatMessages.innerHTML = '';
  if (state.sessionId) readyBanner.style.display = 'flex';
  toast('Conversation cleared.', 'info');
  if (window.innerWidth <= 900) closeMobileSidebar();
}

btnClear.addEventListener('click', clearConversation);

// ─── CHAT INPUT ────────────────────────────────────────────────────────────────
chatInput.addEventListener('input', () => {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 130) + 'px';
  btnSend.disabled = !chatInput.value.trim() || state.isChatting;
});

chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
btnSend.addEventListener('click', sendMessage);

// ─── SEND MESSAGE ─────────────────────────────────────────────────────────────
async function sendMessage() {
  const question = chatInput.value.trim();
  if (!question || state.isChatting || !state.sessionId) return;

  state.isChatting = true;
  chatInput.value = '';
  chatInput.style.height = 'auto';
  btnSend.disabled = true;
  chatInput.disabled = true;
  readyBanner.style.display = 'none';

  appendMessage('user', question);
  typingIndicator.style.display = 'flex';
  scrollToBottom();

  try {
    const data = await apiFetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        question,
        model: modelSelect.value,
        provider: getProvider(),
        api_key: getApiKey(),
        enable_guardrails: guardrailsToggle.checked,
        sensitivity_level: sensitivitySelect.value,
        ollama_host: getOllamaEndpoint(),
      }),
    });
    typingIndicator.style.display = 'none';
    appendMessage('assistant', data.answer, data.blocked);
  } catch (e) {
    typingIndicator.style.display = 'none';
    appendMessage('assistant', `Error: ${e.message}`, false, true);
    toast(e.message, 'error', 6000);
  } finally {
    state.isChatting = false;
    chatInput.disabled = false;
    btnSend.disabled = false;
    requestAnimationFrame(() => chatInput.focus());
  }
}

// ─── RENDER MESSAGE ───────────────────────────────────────────────────────────
function appendMessage(role, text, blocked = false, isError = false) {
  const wrap = document.createElement('div');
  wrap.className = `chat-message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = `msg-avatar ${role === 'user' ? 'user-av' : 'bot-av'}`;
  avatar.setAttribute('aria-hidden', 'true');
  avatar.textContent = role === 'user' ? 'U' : 'NV';

  const bubble = document.createElement('div');
  bubble.className = `msg-bubble${blocked || isError ? ' blocked' : ''}`;

  if (blocked) {
    const label = document.createElement('div');
    label.className = 'guard-label';
    label.textContent = 'GUARDRAIL TRIGGERED';
    bubble.appendChild(label);
  }

  const content = document.createElement('div');
  content.innerHTML = role === 'assistant'
    ? marked.parse(text)
    : escapeHtml(text);
  bubble.appendChild(content);

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatMessages.appendChild(wrap);
  scrollToBottom();
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    if (chatSection) chatSection.scrollTop = chatSection.scrollHeight;
  });
}

// ─── INIT ─────────────────────────────────────────────────────────────────────
(async function init() {
  // 1. Fetch server config → auto-populate endpoint URL from server or localStorage
  await fetchConfig();
  updateSensitivityUI();

  state.sidebarCollapsed = false;
  sidebarExpandBtn.style.display = 'none';

  // 2. Check Ollama health with whatever endpoint was loaded
  await refreshHealth();

  // 3. Load stored document library
  await loadStoragePool();

  // 4. Poll health every 12 s
  setInterval(refreshHealth, 12_000);
})();
