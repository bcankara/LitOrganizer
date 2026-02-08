/**
 * LitOrganizer Web UI — Client-side JavaScript
 * 
 * Handles Socket.IO communication, directory browsing,
 * processing controls, and search functionality.
 */

// ─── Socket.IO Connection ───────────────────────────────────────────────────

const socket = io();

socket.on('connect', () => {
    console.log('Connected to LitOrganizer server');
    // Fetch global status on connect
    fetchGlobalStatus();
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

// ─── Global Status Tracking ─────────────────────────────────────────────────

let statusPollInterval = null;

function fetchGlobalStatus() {
    fetch('/api/status')
        .then(r => r.json())
        .then(data => {
            updateHeaderIndicators(data);
        })
        .catch(err => console.log('Status fetch error:', err));
}

// ─── Circular Ring Progress Helper ──────────────────────────────────────────
// SVG circle with r=34 => circumference = 2 * PI * 34 ≈ 213.628
const RING_CIRCUMFERENCE = 2 * Math.PI * 34; // ~213.628

function setRingProgress(ringId, pctTextId, percentage) {
    const ring = document.getElementById(ringId);
    const pctEl = document.getElementById(pctTextId);
    if (ring) {
        const offset = RING_CIRCUMFERENCE * (1 - percentage / 100);
        ring.style.strokeDashoffset = offset;
        ring.classList.toggle('active', percentage > 0 && percentage < 100);
    }
    if (pctEl) pctEl.textContent = `${Math.round(percentage)}%`;
}

function updateHeaderIndicators(data) {
    const container = document.getElementById('active-tasks');
    const processingEl = document.getElementById('task-processing');
    const searchingEl = document.getElementById('task-searching');

    if (!container) return;

    const hasActiveTasks = data.processing || data.searching;

    if (hasActiveTasks) {
        container.classList.remove('hidden');

        // Processing ring
        if (data.processing) {
            processingEl.classList.remove('hidden');
            setRingProgress('bp-process-ring', 'task-processing-pct', data.process_progress || 0);
        } else {
            processingEl.classList.add('hidden');
        }

        // Searching ring
        if (data.searching) {
            searchingEl.classList.remove('hidden');
            const searchPct = data.search_progress || 0;
            setRingProgress('bp-search-ring', 'task-searching-pct', searchPct);
            // Keep page-level search progress in sync with polling data
            if (typeof updateSearchProgress === 'function') {
                updateSearchProgress(searchPct);
            }
        } else {
            searchingEl.classList.add('hidden');
        }

        // Start polling if not already
        if (!statusPollInterval) {
            statusPollInterval = setInterval(fetchGlobalStatus, 2000);
        }
    } else {
        container.classList.add('hidden');
        processingEl.classList.add('hidden');
        searchingEl.classList.add('hidden');

        // Stop polling
        if (statusPollInterval) {
            clearInterval(statusPollInterval);
            statusPollInterval = null;
        }
    }
}

// Listen for progress updates to sync bottom panel rings AND page indicators
socket.on('progress_update', (data) => {
    setRingProgress('bp-process-ring', 'task-processing-pct', data.percentage);
    // Also sync page-level progress if on process page
    if (typeof updateProgress === 'function') {
        updateProgress(data.percentage);
    }
});

socket.on('search_progress', (data) => {
    setRingProgress('bp-search-ring', 'task-searching-pct', data.percentage);
    // Also sync page-level search progress if on search page
    if (typeof updateSearchProgress === 'function') {
        updateSearchProgress(data.percentage);
    }
});

// Show/hide bottom panel task indicators on start/complete
socket.on('processing_started', () => {
    const container = document.getElementById('active-tasks');
    const processingEl = document.getElementById('task-processing');
    if (container) container.classList.remove('hidden');
    if (processingEl) processingEl.classList.remove('hidden');
    setRingProgress('bp-process-ring', 'task-processing-pct', 0);
    if (!statusPollInterval) statusPollInterval = setInterval(fetchGlobalStatus, 2000);
});

socket.on('processing_complete', () => {
    setRingProgress('bp-process-ring', 'task-processing-pct', 100);
    // Hide after a delay so user sees 100%
    setTimeout(() => {
        const processingEl = document.getElementById('task-processing');
        if (processingEl) processingEl.classList.add('hidden');
        fetchGlobalStatus();
    }, 3000);
});

socket.on('search_started', () => {
    const container = document.getElementById('active-tasks');
    const searchingEl = document.getElementById('task-searching');
    if (container) container.classList.remove('hidden');
    if (searchingEl) searchingEl.classList.remove('hidden');
    setRingProgress('bp-search-ring', 'task-searching-pct', 0);
    if (!statusPollInterval) statusPollInterval = setInterval(fetchGlobalStatus, 2000);
});

socket.on('search_complete', () => {
    setRingProgress('bp-search-ring', 'task-searching-pct', 100);
    // Hide after a delay
    setTimeout(() => {
        const searchingEl = document.getElementById('task-searching');
        if (searchingEl) searchingEl.classList.add('hidden');
        fetchGlobalStatus();
    }, 3000);
});

// ─── Shared: Log Area ───────────────────────────────────────────────────────

socket.on('log_message', (data) => {
    appendLog(data.message);
});

function appendLog(message) {
    const logArea = document.getElementById('log-area');
    if (!logArea) return;

    // Remove placeholder if present
    const placeholder = logArea.querySelector('.text-gray-400');
    if (placeholder && placeholder.textContent.includes('Waiting')) {
        placeholder.remove();
    }

    const line = document.createElement('div');
    line.className = 'log-line';
    line.textContent = message;
    logArea.appendChild(line);
    logArea.scrollTop = logArea.scrollHeight;
}

function clearLog() {
    const logArea = document.getElementById('log-area');
    if (!logArea) return;
    logArea.innerHTML = '<div class="text-gray-500">Log cleared.</div>';
}

// ─── Native OS Folder Picker ─────────────────────────────────────────────────

function nativeBrowse(inputId) {
    // Show a loading state on the button
    const btn = event ? event.currentTarget : null;
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Opening...';
    }

    fetch('/api/native_browse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
        .then(r => r.json())
        .then(data => {
            if (data.success && data.path) {
                setSelectedPath(inputId, data.path);
            }
        })
        .catch(err => {
            console.error('Native browse error:', err);
            appendLog('Could not open folder picker. Use manual browse instead.');
        })
        .finally(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        });
}

function setSelectedPath(inputId, path) {
    const input = document.getElementById(inputId);
    if (input) input.value = path;

    const isSearch = inputId === 'search-dir-input';
    const displayEl = document.getElementById(isSearch ? 'search-selected-path-display' : 'selected-path-display');
    const textEl = document.getElementById(isSearch ? 'search-selected-path-text' : 'selected-path-text');

    if (displayEl) displayEl.classList.remove('hidden');
    if (textEl) textEl.textContent = path;

    validateDir(inputId);
}

function clearSelectedPath(inputId) {
    const input = document.getElementById(inputId);
    if (input) input.value = '';

    const isSearch = inputId === 'search-dir-input';
    const displayEl = document.getElementById(isSearch ? 'search-selected-path-display' : 'selected-path-display');

    if (displayEl) displayEl.classList.add('hidden');

    const dirInfo = document.getElementById('dir-info');
    if (dirInfo) dirInfo.textContent = '';
}

// ─── Directory Browser Modal ────────────────────────────────────────────────

let currentBrowsePath = '';
let browseTargetInput = null;

function browseDirectory(inputId) {
    browseTargetInput = inputId;
    const currentValue = document.getElementById(inputId).value;
    const modal = document.getElementById('dir-modal');
    modal.classList.remove('hidden');

    // Load quick access shortcuts
    loadQuickAccessPaths();

    // Start browsing from current value or root
    loadDirectory(currentValue || '');
}

function loadQuickAccessPaths() {
    const bar = document.getElementById('quick-access-bar');
    if (!bar) return;

    fetch('/api/quick_paths')
        .then(r => r.json())
        .then(paths => {
            bar.innerHTML = '';
            paths.forEach(p => {
                const btn = document.createElement('button');
                btn.className = 'quick-access-btn';
                const iconMap = {
                    'desktop': '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>',
                    'folder': '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>',
                    'download': '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>',
                    'drive': '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/></svg>',
                };
                btn.innerHTML = `${iconMap[p.icon] || iconMap['folder']} <span>${p.name}</span>`;
                btn.addEventListener('click', () => loadDirectory(p.path));
                bar.appendChild(btn);
            });
        })
        .catch(err => console.log('Quick paths error:', err));
}

function closeDirModal() {
    document.getElementById('dir-modal').classList.add('hidden');
}

function loadDirectory(path) {
    const listing = document.getElementById('dir-listing');
    listing.innerHTML = '<div class="text-gray-400 text-center py-8 text-sm">Loading...</div>';

    fetch('/api/browse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
        .then(r => r.json())
        .then(data => {
            currentBrowsePath = data.current || '';
            document.getElementById('modal-path-input').value = currentBrowsePath;

            if (data.dirs && data.dirs.length > 0) {
                listing.innerHTML = '';
                data.dirs.forEach(dir => {
                    const item = document.createElement('div');
                    item.className = 'dir-item';
                    const dirName = dir.split(/[/\\]/).filter(Boolean).pop() || dir;
                    item.innerHTML = `
                    <svg class="w-4 h-4 text-accent flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                    </svg>
                    <span class="truncate">${dirName}</span>
                `;
                    item.addEventListener('click', () => loadDirectory(dir));
                    listing.appendChild(item);
                });
            } else {
                listing.innerHTML = '<div class="text-gray-400 text-center py-8 text-sm">No subdirectories found.</div>';
            }
        })
        .catch(err => {
            listing.innerHTML = '<div class="text-danger text-center py-8 text-sm">Error loading directory.</div>';
        });
}

function navigateToPath() {
    const path = document.getElementById('modal-path-input').value;
    loadDirectory(path);
}

function navigateUp() {
    if (currentBrowsePath) {
        // Go to parent
        const parts = currentBrowsePath.replace(/\\/g, '/').split('/').filter(Boolean);
        parts.pop();
        const parent = parts.length > 0 ? parts.join('/') : (currentBrowsePath.startsWith('/') ? '/' : '');
        // On Windows, ensure drive letter format
        if (/^[a-zA-Z]:/.test(currentBrowsePath) && parts.length === 1) {
            loadDirectory(parts[0] + '/');
        } else {
            loadDirectory(parent);
        }
    }
}

function selectDirectory() {
    if (browseTargetInput && currentBrowsePath) {
        document.getElementById(browseTargetInput).value = currentBrowsePath;
        // Update selected path display
        if (browseTargetInput === 'dir-input' || browseTargetInput === 'search-dir-input') {
            setSelectedPath(browseTargetInput, currentBrowsePath);
        }
    }
    closeDirModal();
}

function validateDir(inputId) {
    const path = document.getElementById(inputId).value;
    if (!path) return;

    fetch('/api/validate_dir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
        .then(r => r.json())
        .then(data => {
            const info = document.getElementById('dir-info');
            if (info) {
                info.textContent = data.message;
                info.className = data.valid && data.pdf_count > 0
                    ? 'text-xs text-success mt-1'
                    : 'text-xs text-warn mt-1';
            }
        });
}

// ─── Processing Page ────────────────────────────────────────────────────────

let processedCount = 0;
let renamedCount = 0;
let problematicCount = 0;

let lastProcessDirectory = '';

function initProcessingPage() {
    // Validate dir on input change
    const dirInput = document.getElementById('dir-input');
    if (dirInput) {
        dirInput.addEventListener('change', () => validateDir('dir-input'));
        dirInput.addEventListener('blur', () => validateDir('dir-input'));
    }

    // Load existing process state (page reload persistence)
    loadExistingProcessState();

    // Socket events for processing
    socket.on('processing_started', (data) => {
        document.getElementById('btn-start').disabled = true;
        document.getElementById('btn-stop').disabled = false;
        document.getElementById('btn-start').textContent = 'Processing... 0%';
        document.getElementById('progress-summary').classList.remove('hidden');

        // Reset counters
        processedCount = 0;
        renamedCount = 0;
        problematicCount = 0;
        fileStatusCount = 0;
        document.getElementById('stat-processed').textContent = '0';
        document.getElementById('stat-renamed').textContent = '0';
        document.getElementById('stat-problematic').textContent = '0';
    });

    socket.on('file_processed', (data) => {
        addFileStatus(data.filename, data.success);

        // Update stats in real-time
        processedCount++;
        if (data.success) {
            renamedCount++;
        } else {
            problematicCount++;
        }
        document.getElementById('stat-processed').textContent = processedCount;
        document.getElementById('stat-renamed').textContent = renamedCount;
        document.getElementById('stat-problematic').textContent = problematicCount;
    });

    socket.on('progress_update', (data) => {
        updateProgress(data.percentage);
    });

    socket.on('processing_complete', (data) => {
        document.getElementById('btn-start').disabled = false;
        document.getElementById('btn-stop').disabled = true;
        document.getElementById('btn-start').textContent = 'Start Processing';
        updateProgress(100);

        document.getElementById('stat-processed').textContent = data.processed;
        document.getElementById('stat-renamed').textContent = data.renamed;
        document.getElementById('stat-problematic').textContent = data.problematic;

        lastProcessDirectory = data.directory || '';

        appendLog(`Processing completed! Processed: ${data.processed}, Renamed: ${data.renamed}, Unnamed: ${data.problematic}`);

        // Show completion modal
        showCompletionModal(data);
    });
}

function loadExistingProcessState() {
    const overlay = document.getElementById('state-loading-overlay');

    // Fetch current processing state from backend
    fetch('/api/process_status')
        .then(r => r.json())
        .then(data => {
            if (!data) {
                if (overlay) overlay.classList.add('hidden');
                return;
            }

            const hasData = (data.file_statuses && data.file_statuses.length > 0) 
                            || data.processing 
                            || data.last_completed_stats;

            // Show overlay only if there's data to restore
            if (hasData && overlay) {
                overlay.classList.remove('hidden');
            }

            // Restore directory from process_directory or last_completed_stats
            lastProcessDirectory = data.process_directory || '';
            if (!lastProcessDirectory && data.last_completed_stats) {
                lastProcessDirectory = data.last_completed_stats.directory || '';
            }

            // Restore directory input and selected path display
            if (lastProcessDirectory) {
                const dirInput = document.getElementById('dir-input');
                if (dirInput && !dirInput.value) {
                    dirInput.value = lastProcessDirectory;
                }
                if (typeof setSelectedPath === 'function') {
                    setSelectedPath('dir-input', lastProcessDirectory);
                }
            }

            // Restore file statuses
            if (data.file_statuses && data.file_statuses.length > 0) {
                const fileList = document.getElementById('file-list');
                if (fileList) {
                    fileList.innerHTML = '';

                    fileStatusCount = 0;
                    processedCount = 0;
                    renamedCount = 0;
                    problematicCount = 0;

                    data.file_statuses.forEach(status => {
                        addFileStatus(status.filename, status.success);
                        processedCount++;
                        if (status.success) renamedCount++;
                        else problematicCount++;
                    });

                    // Update stats UI
                    const elProcessed = document.getElementById('stat-processed');
                    const elRenamed = document.getElementById('stat-renamed');
                    const elProblematic = document.getElementById('stat-problematic');
                    if (elProcessed) elProcessed.textContent = processedCount;
                    if (elRenamed) elRenamed.textContent = renamedCount;
                    if (elProblematic) elProblematic.textContent = problematicCount;

                    const progressSummary = document.getElementById('progress-summary');
                    if (progressSummary) progressSummary.classList.remove('hidden');
                    updateProgress(data.process_progress || 0);
                }
            }

            // If still processing, update button state
            if (data.processing) {
                const btnStart = document.getElementById('btn-start');
                const btnStop = document.getElementById('btn-stop');
                if (btnStart) {
                    btnStart.disabled = true;
                    btnStart.textContent = `Processing... ${data.process_progress || 0}%`;
                }
                if (btnStop) btnStop.disabled = false;
            }

            // If processing completed (not running anymore) and we have last_completed_stats,
            // restore stats and show completion modal
            if (!data.processing && data.last_completed_stats) {
                const stats = data.last_completed_stats;
                lastProcessDirectory = stats.directory || lastProcessDirectory;

                // Restore counters from completed stats
                processedCount = stats.processed || 0;
                renamedCount = stats.renamed || 0;
                problematicCount = stats.problematic || 0;

                const elProcessed = document.getElementById('stat-processed');
                const elRenamed = document.getElementById('stat-renamed');
                const elProblematic = document.getElementById('stat-problematic');
                if (elProcessed) elProcessed.textContent = processedCount;
                if (elRenamed) elRenamed.textContent = renamedCount;
                if (elProblematic) elProblematic.textContent = problematicCount;

                const progressSummary = document.getElementById('progress-summary');
                if (progressSummary) progressSummary.classList.remove('hidden');
                updateProgress(100);

                // Show completion modal after a brief delay so overlay can fade
                setTimeout(() => {
                    showCompletionModal(stats);
                }, 400);
            }

            // Hide overlay with a small fade
            if (overlay) {
                overlay.classList.add('fade-out');
                setTimeout(() => {
                    overlay.classList.add('hidden');
                    overlay.classList.remove('fade-out');
                }, 300);
            }
        })
        .catch(err => {
            console.log('No existing process state:', err);
            if (overlay) overlay.classList.add('hidden');
        });
}

function showCompletionModal(data) {
    const modal = document.getElementById('completion-modal');
    if (!modal) return;

    const successRate = data.processed > 0 ? Math.round((data.renamed / data.processed) * 100) : 0;
    const totalTime = data.stats ? data.stats.total_time : 0;

    document.getElementById('cm-processed').textContent = data.processed;
    document.getElementById('cm-renamed').textContent = data.renamed;
    document.getElementById('cm-unnamed').textContent = data.problematic;
    document.getElementById('cm-success-rate').textContent = successRate + '%';
    document.getElementById('cm-time').textContent = totalTime > 60
        ? `${Math.floor(totalTime / 60)}m ${Math.round(totalTime % 60)}s`
        : `${totalTime.toFixed(1)}s`;

    // Set success rate bar
    const rateBar = document.getElementById('cm-rate-bar');
    if (rateBar) {
        rateBar.style.width = successRate + '%';
        rateBar.className = 'h-full rounded-full transition-all duration-700 ' +
            (successRate >= 70 ? 'bg-green-500' : successRate >= 40 ? 'bg-yellow-500' : 'bg-red-500');
    }

    modal.classList.remove('hidden');
}

function closeCompletionModal() {
    const modal = document.getElementById('completion-modal');
    if (modal) modal.classList.add('hidden');
}

function openProcessedFolder() {
    const dir = lastProcessDirectory;
    if (!dir) {
        console.warn('openProcessedFolder: No lastProcessDirectory set');
        return;
    }

    // Normalize path separator (use / for cross-platform, Python handles conversion)
    const cleanDir = dir.replace(/[/\\]$/, '');
    const namedDir = cleanDir + '/Named Article';

    console.log('openProcessedFolder: Trying', namedDir);

    fetch('/api/open_folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: namedDir })
    })
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                console.log('openProcessedFolder: Named Article not found, falling back to', cleanDir);
                // Fallback: try opening the main directory
                return fetch('/api/open_folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: cleanDir })
                }).then(r => r.json());
            }
            return data;
        })
        .then(data => {
            if (data && !data.success) {
                appendLog('Could not open folder: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(err => {
            console.error('openProcessedFolder error:', err);
        });
}

function goToStatistics() {
    closeCompletionModal();
    window.location.href = '/statistics';
}

function startProcessing() {
    const directory = document.getElementById('dir-input').value;
    if (!directory) {
        appendLog('Please select a directory first.');
        return;
    }

    // Clear previous results
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-text').textContent = '0%';
    document.getElementById('file-count').textContent = '0 files';

    const options = {
        directory: directory,
        unnamed_dir: document.getElementById('unnamed-dir-input').value,
        use_ocr: document.getElementById('opt-ocr').checked,
        create_references: document.getElementById('opt-references').checked,
        create_backups: document.getElementById('opt-backups').checked,
        move_problematic: document.getElementById('opt-move-unnamed').checked,
        separate_ai_folder: document.getElementById('opt-separate-ai').checked,
        by_journal: document.getElementById('cat-journal').checked,
        by_author: document.getElementById('cat-author').checked,
        by_year: document.getElementById('cat-year').checked,
        by_subject: document.getElementById('cat-subject').checked,
    };

    socket.emit('start_processing', options);
}

function stopProcessing() {
    socket.emit('stop_processing');
    document.getElementById('btn-start').textContent = 'Stopping...';
}

function updateProgress(pct) {
    const bar = document.getElementById('progress-bar');
    const text = document.getElementById('progress-text');
    if (bar) bar.style.width = pct + '%';
    if (text) text.textContent = pct + '%';

    const btn = document.getElementById('btn-start');
    if (btn && btn.disabled && pct < 100) {
        btn.textContent = `Processing... ${pct}%`;
    }
}

let fileStatusCount = 0;
function addFileStatus(filename, success) {
    const fileList = document.getElementById('file-list');
    if (!fileList) return;

    // Remove placeholder
    const placeholder = fileList.querySelector('.text-gray-400');
    if (placeholder) placeholder.remove();

    const item = document.createElement('div');
    item.className = `file-status-item ${success ? 'file-success' : 'file-error'}`;
    item.innerHTML = `
        <span class="status-icon">${success ? '&#10003;' : '&#10007;'}</span>
        <span class="truncate">${filename}</span>
        <span class="ml-auto text-xs">${success ? 'Renamed' : 'Not Renamed'}</span>
    `;
    fileList.appendChild(item);
    fileList.scrollTop = fileList.scrollHeight;

    fileStatusCount++;
    const counter = document.getElementById('file-count');
    if (counter) counter.textContent = fileStatusCount + ' files';
}

// ─── Search Page ────────────────────────────────────────────────────────────

function initSearchPage() {
    const dirInput = document.getElementById('search-dir-input');
    if (dirInput) {
        dirInput.addEventListener('change', () => validateDir('search-dir-input'));
    }

    // Load existing search results on page load
    loadExistingResults();

    // Socket events for search
    socket.on('search_started', (data) => {
        document.getElementById('btn-search-start').disabled = true;
        document.getElementById('btn-search-stop').disabled = false;
        document.getElementById('btn-search-start').textContent = 'Searching... 0%';
        document.getElementById('search-summary').classList.remove('hidden');

        // Show spinner and start elapsed timer
        document.getElementById('search-spinner').classList.remove('hidden');
        document.getElementById('search-elapsed').classList.remove('hidden');
        startSearchTimer();
    });

    socket.on('search_result', (data) => {
        addSearchResult(data);
        // Update found count in real-time
        searchMatchCount++;
        document.getElementById('search-found').textContent = searchMatchCount;
    });

    socket.on('search_progress', (data) => {
        updateSearchProgress(data.percentage);
    });

    socket.on('search_file_processed', (data) => {
        // Update processed file count in real-time
        searchFileCount++;
        document.getElementById('search-processed').textContent = searchFileCount;
    });

    socket.on('search_complete', (data) => {
        document.getElementById('btn-search-start').disabled = false;
        document.getElementById('btn-search-stop').disabled = true;
        document.getElementById('btn-search-start').textContent = 'Start Search';
        updateSearchProgress(100);

        document.getElementById('search-found').textContent = data.found;
        document.getElementById('search-processed').textContent = data.processed;

        // Hide spinner and stop timer
        document.getElementById('search-spinner').classList.add('hidden');
        stopSearchTimer();

        if (data.found > 0) {
            const btnXlsx = document.getElementById('btn-export-xlsx');
            const btnDocx = document.getElementById('btn-export-docx');
            if (btnXlsx) btnXlsx.disabled = false;
            if (btnDocx) btnDocx.disabled = false;
        }

        // Show search complete modal
        showSearchCompleteModal(data);
    });
}

// Search timer variables
let searchStartTime = null;
let searchTimerInterval = null;
let searchMatchCount = 0;
let searchFileCount = 0;

function startSearchTimer() {
    searchStartTime = Date.now();
    searchMatchCount = 0;
    searchFileCount = 0;
    searchTimerInterval = setInterval(updateElapsedTime, 1000);
    updateElapsedTime();
}

function stopSearchTimer() {
    if (searchTimerInterval) {
        clearInterval(searchTimerInterval);
        searchTimerInterval = null;
    }
}

function updateElapsedTime() {
    if (!searchStartTime) return;
    const elapsed = Math.floor((Date.now() - searchStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const elapsedEl = document.getElementById('search-elapsed');
    if (elapsedEl) {
        elapsedEl.textContent = `${minutes}m ${seconds}s`;
    }
}

function loadExistingResults() {
    fetch('/api/get_search_results')
        .then(r => r.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                const tbody = document.getElementById('search-results-body');
                if (!tbody) return;

                // Clear empty row
                const emptyRow = document.getElementById('search-empty-row');
                if (emptyRow) emptyRow.remove();

                // Add each result
                data.results.forEach(row => {
                    const [doi, filename, page, keyword, prev_sentence, matched_sentence, next_sentence] = row;
                    addSearchResult({
                        doi: doi,
                        filename: filename,
                        page: page,
                        keyword: keyword,
                        prev_sentence: prev_sentence,
                        matched_sentence: matched_sentence,
                        next_sentence: next_sentence
                    });
                });

                // Update UI
                document.getElementById('search-found').textContent = data.count;
                document.getElementById('search-summary').classList.remove('hidden');
                document.getElementById('btn-export-xlsx').disabled = false;
                document.getElementById('btn-export-docx').disabled = false;
                updateSearchProgress(100);

                appendLog(`Loaded ${data.count} previous search results.`);
            }
        })
        .catch(err => {
            console.log('No existing results to load');
        });
}

function startSearch() {
    const directory = document.getElementById('search-dir-input').value;
    const keyword = document.getElementById('search-keyword').value.trim();

    if (!directory) {
        appendLog('Please select a directory first.');
        return;
    }
    if (!keyword) {
        appendLog('Please enter a keyword to search for.');
        return;
    }

    const searchParams = {
        directory: directory,
        keyword: keyword,
        exact_match: document.getElementById('search-exact').checked,
        case_sensitive: document.getElementById('search-case').checked,
        use_regex: document.getElementById('search-regex').checked,
    };

    // Check if there are existing results - show confirm modal
    const existingResults = document.getElementById('search-results-body');
    const hasResults = existingResults && !existingResults.querySelector('#search-empty-row');

    if (hasResults) {
        pendingSearchParams = searchParams;
        const confirmModal = document.getElementById('confirm-search-modal');
        if (confirmModal) {
            confirmModal.classList.remove('hidden');
        } else {
            // Fallback if modal not found
            clearSearchResults();
            socket.emit('start_search', searchParams);
        }
        return;
    }

    // No existing results, start directly
    clearSearchResults();
    socket.emit('start_search', searchParams);

    // Set default export filename
    const exportFilename = document.getElementById('export-filename');
    if (exportFilename) exportFilename.value = keyword.replace(/\s+/g, '_');
}

function stopSearch() {
    socket.emit('stop_search');
    document.getElementById('btn-search-start').textContent = 'Stopping...';
}

function updateSearchProgress(pct) {
    const bar = document.getElementById('search-progress-bar');
    const text = document.getElementById('search-progress-text');
    if (bar) bar.style.width = pct + '%';
    if (text) text.textContent = pct + '%';

    const btn = document.getElementById('btn-search-start');
    if (btn && btn.disabled && pct < 100) {
        btn.textContent = `Searching... ${pct}%`;
    }
}

function addSearchResult(data) {
    const tbody = document.getElementById('search-results-body');
    if (!tbody) return;

    // Remove empty row
    const emptyRow = document.getElementById('search-empty-row');
    if (emptyRow) emptyRow.remove();

    // Simplified row: PDF name, page, matched context with surrounding text
    const contextParts = [];
    if (data.prev_sentence) contextParts.push('<span class="text-gray-400">' + escapeHtml(truncate(data.prev_sentence, 60)) + '</span> ');
    contextParts.push('<mark class="search-highlight">' + escapeHtml(data.matched_sentence) + '</mark>');
    if (data.next_sentence) contextParts.push(' <span class="text-gray-400">' + escapeHtml(truncate(data.next_sentence, 60)) + '</span>');

    const row = document.createElement('tr');
    row.innerHTML = `
        <td class="text-xs font-medium" title="${escapeHtml(data.filename)}">${escapeHtml(truncate(data.filename, 40))}</td>
        <td class="text-center text-xs">${data.page}</td>
        <td class="text-xs leading-relaxed">${contextParts.join('')}</td>
    `;
    tbody.appendChild(row);
}

function clearSearchResults() {
    const tbody = document.getElementById('search-results-body');
    if (tbody) {
        tbody.innerHTML = '<tr id="search-empty-row"><td colspan="3" class="text-center text-gray-400 py-8">No results yet. Start a search to find matches.</td></tr>';
    }
    const bar = document.getElementById('search-progress-bar');
    const text = document.getElementById('search-progress-text');
    if (bar) bar.style.width = '0%';
    if (text) text.textContent = '0%';
    const btnXlsx = document.getElementById('btn-export-xlsx');
    const btnDocx = document.getElementById('btn-export-docx');
    if (btnXlsx) btnXlsx.disabled = true;
    if (btnDocx) btnDocx.disabled = true;
}

// ─── Search Complete Modal ───────────────────────────────────────────────────

function showSearchCompleteModal(data) {
    const modal = document.getElementById('search-complete-modal');
    if (!modal) return;

    const scmMatches = document.getElementById('scm-matches');
    const scmFiles = document.getElementById('scm-files');
    const scmTime = document.getElementById('scm-time');

    if (scmMatches) scmMatches.textContent = data.found || 0;
    if (scmFiles) scmFiles.textContent = data.processed || 0;

    // Calculate elapsed time
    if (scmTime && searchStartTime) {
        const elapsed = Math.floor((Date.now() - searchStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        scmTime.textContent = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
    }

    // Set export filename from keyword
    const keyword = document.getElementById('search-keyword');
    const exportFilename = document.getElementById('export-filename');
    if (keyword && exportFilename) {
        exportFilename.value = keyword.value.replace(/\s+/g, '_') || 'search_results';
    }

    // Enable export buttons if there are results
    const btnXlsx = document.getElementById('btn-export-xlsx');
    const btnDocx = document.getElementById('btn-export-docx');
    if (data.found > 0) {
        if (btnXlsx) btnXlsx.disabled = false;
        if (btnDocx) btnDocx.disabled = false;
    }

    modal.classList.remove('hidden');
}

function closeSearchCompleteModal() {
    const modal = document.getElementById('search-complete-modal');
    if (modal) modal.classList.add('hidden');
}

// ─── Confirm New Search Modal ────────────────────────────────────────────────

let pendingSearchParams = null;

function closeConfirmSearchModal() {
    const modal = document.getElementById('confirm-search-modal');
    if (modal) modal.classList.add('hidden');
    pendingSearchParams = null;
}

function confirmNewSearch() {
    closeConfirmSearchModal();
    if (pendingSearchParams) {
        clearSearchResults();
        socket.emit('start_search', pendingSearchParams);
        document.getElementById('export-filename').value = pendingSearchParams.keyword.replace(/\s+/g, '_');
        pendingSearchParams = null;
    }
}

function exportResults(format) {
    const filename = document.getElementById('export-filename').value || 'search_results';
    const formatName = format === 'xlsx' ? 'Excel' : 'Word';

    // Show export loading overlay
    showExportLoading(formatName);

    fetch('/api/download_search_results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: format, filename: filename })
    })
        .then(response => {
            if (!response.ok) throw new Error('Export failed');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            appendLog(`Exported results as ${format.toUpperCase()}: ${filename}.${format}`);
            hideExportLoading();
        })
        .catch(err => {
            appendLog('Export failed: ' + err.message);
            hideExportLoading();
        });
}

function showExportLoading(formatName) {
    // Create overlay if not exists
    let overlay = document.getElementById('export-loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'export-loading-overlay';
        overlay.className = 'fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="bg-white rounded-xl shadow-xl p-8 flex flex-col items-center gap-4 max-w-sm">
                <svg class="animate-spin w-12 h-12 text-blue-500" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div class="text-center">
                    <p id="export-loading-title" class="font-semibold text-navy text-lg">Exporting...</p>
                    <p id="export-loading-text" class="text-sm text-gray-500 mt-1">Preparing your document</p>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    // Update text
    document.getElementById('export-loading-title').textContent = `Exporting to ${formatName}...`;
    document.getElementById('export-loading-text').textContent = `Preparing your ${formatName} document with highlighted keywords`;
    overlay.classList.remove('hidden');
}

function hideExportLoading() {
    const overlay = document.getElementById('export-loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// ─── Utility Functions ──────────────────────────────────────────────────────

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function truncate(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
}

// ─── Citation Functions ─────────────────────────────────────────────────────

const citations = {
    bibtex: `@article{SAHIN2025102198,
    title = {LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews},
    journal = {SoftwareX},
    volume = {30},
    pages = {102198},
    year = {2025},
    issn = {2352-7110},
    doi = {10.1016/j.softx.2025.102198},
    url = {https://www.sciencedirect.com/science/article/pii/S2352711025001657},
    author = {Alperen Şahin and Burak Can Kara and Taşkın Dirsehan},
    keywords = {PDF management, DOI extraction, Academic literature, Scientific literature review, Research automation}
}`,
    apa: `Şahin, A., Kara, B. C., & Dirsehan, T. (2025). LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews. SoftwareX, 30, 102198. https://doi.org/10.1016/j.softx.2025.102198`,
    ris: `TY  - JOUR
TI  - LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews
AU  - Şahin, Alperen
AU  - Kara, Burak Can
AU  - Dirsehan, Taşkın
JO  - SoftwareX
VL  - 30
SP  - 102198
PY  - 2025
SN  - 2352-7110
DO  - 10.1016/j.softx.2025.102198
UR  - https://www.sciencedirect.com/science/article/pii/S2352711025001657
KW  - PDF management
KW  - DOI extraction
KW  - Academic literature
KW  - Scientific literature review
KW  - Research automation
ER  - `
};

function showCitation(format) {
    const modal = document.getElementById('citation-modal');
    const title = document.getElementById('citation-title');
    const content = document.getElementById('citation-content');

    if (modal && title && content) {
        const formatNames = { bibtex: 'BibTeX', apa: 'APA', ris: 'RIS' };
        title.textContent = `Citation (${formatNames[format] || format})`;
        content.textContent = citations[format] || '';
        modal.classList.remove('hidden');
    }
}

function closeCitationModal() {
    const modal = document.getElementById('citation-modal');
    if (modal) modal.classList.add('hidden');
}

function copyCitation() {
    const content = document.getElementById('citation-content');
    if (content) {
        navigator.clipboard.writeText(content.textContent).then(() => {
            const btn = document.querySelector('#citation-modal .btn-primary');
            if (btn) {
                const originalText = btn.innerHTML;
                btn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Copied!';
                setTimeout(() => { btn.innerHTML = originalText; }, 2000);
            }
        });
    }
}

// ─── Gemini AI Inline Panel ─────────────────────────────────────────────────

let geminiQueryCount = 0;

function resetGeminiPanel() {
    geminiQueryCount = 0;
    const results = document.getElementById('gemini-results');
    const counter = document.getElementById('gemini-counter');
    const badge = document.getElementById('gemini-status-badge');
    const emptyState = document.getElementById('gemini-empty-state');
    const activeQuery = document.getElementById('gemini-active-query');

    if (results) results.innerHTML = '';
    if (counter) counter.textContent = '0 queries';
    if (badge) { badge.classList.add('hidden'); }
    if (activeQuery) activeQuery.classList.add('hidden');
    
    // Re-add empty state
    if (results && emptyState) {
        // Clone won't work if removed, recreate
        results.innerHTML = `<div class="text-gray-400 text-center py-8 text-sm" id="gemini-empty-state">
            <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            Gemini AI results for PDFs<br>without DOI will appear here.
        </div>`;
    }
}

function updateGeminiCounter() {
    const counter = document.getElementById('gemini-counter');
    if (counter) counter.textContent = `${geminiQueryCount} queries`;
}

function setGeminiBadge(status, text) {
    const badge = document.getElementById('gemini-status-badge');
    if (!badge) return;
    badge.classList.remove('hidden', 'bg-indigo-100', 'text-indigo-700', 'bg-green-100', 'text-green-700', 'bg-orange-100', 'text-orange-700', 'bg-gray-100', 'text-gray-500');
    if (status === 'connecting') {
        badge.className = 'px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700';
        badge.textContent = text || 'Querying...';
    } else if (status === 'success') {
        badge.className = 'px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700';
        badge.textContent = text || 'Found';
    } else if (status === 'failed') {
        badge.className = 'px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700';
        badge.textContent = text || 'Not Found';
    }
}

function showGeminiActiveQuery(filename) {
    const el = document.getElementById('gemini-active-query');
    const nameEl = document.getElementById('gemini-active-filename');
    if (el) el.classList.remove('hidden');
    if (nameEl) nameEl.textContent = filename;
}

function hideGeminiActiveQuery() {
    const el = document.getElementById('gemini-active-query');
    if (el) el.classList.add('hidden');
}

function addGeminiResult(data) {
    const results = document.getElementById('gemini-results');
    if (!results) return;

    // Remove empty state on first result
    const emptyState = document.getElementById('gemini-empty-state');
    if (emptyState) emptyState.remove();

    const item = document.createElement('div');
    item.style.animation = 'fadeInScale 0.3s ease-out forwards';

    if (data.status === 'success') {
        const authors = (data.authors || []).join(', ') || 'Unknown';
        const year = data.year || '?';
        const titleText = data.title || 'Title not found';

        item.className = 'bg-green-50 border border-green-200 rounded-lg p-2.5';
        item.innerHTML = `
            <div class="flex items-start gap-2">
                <svg class="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                <div class="min-w-0 flex-1">
                    <div class="text-[11px] text-gray-400 truncate">${escapeHtml(data.filename)}</div>
                    <div class="text-xs font-semibold text-green-800 mt-0.5 leading-snug">${escapeHtml(titleText)}</div>
                    <div class="text-[11px] text-green-600 mt-0.5">${escapeHtml(authors)} (${escapeHtml(year)})</div>
                </div>
            </div>
        `;
    } else if (data.status === 'failed') {
        item.className = 'bg-orange-50 border border-orange-200 rounded-lg p-2.5';
        item.innerHTML = `
            <div class="flex items-start gap-2">
                <svg class="w-4 h-4 text-orange-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                <div class="min-w-0 flex-1">
                    <div class="text-[11px] text-gray-400 truncate">${escapeHtml(data.filename)}</div>
                    <div class="text-[11px] text-orange-700 mt-0.5">Metadata extraction failed</div>
                </div>
            </div>
        `;
    }

    results.appendChild(item);
    results.scrollTop = results.scrollHeight;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Socket listener for Gemini status events
socket.on('gemini_status', function(data) {
    const panel = document.getElementById('gemini-panel');
    if (!panel) return;

    if (data.status === 'connecting') {
        geminiQueryCount++;
        updateGeminiCounter();
        setGeminiBadge('connecting');
        showGeminiActiveQuery(data.filename);
    } else if (data.status === 'success') {
        setGeminiBadge('success');
        hideGeminiActiveQuery();
        addGeminiResult(data);
    } else if (data.status === 'failed') {
        setGeminiBadge('failed');
        hideGeminiActiveQuery();
        addGeminiResult(data);
    }
});
