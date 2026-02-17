const API_BASE = "";

const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const connectBtn = document.getElementById('connect-btn');
const dbPathInput = document.getElementById('db-path');
const statusBadge = document.getElementById('connection-status');
const explainToggle = document.getElementById('explain-toggle');
const graphToggle = document.getElementById('graph-toggle');
const dashboardToggle = document.getElementById('dashboard-toggle');

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

function scrollToBottom() {
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

function addUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'msg-row user';
    row.innerHTML = `<div class="bubble">${text}</div>`;
    messagesContainer.appendChild(row);
    scrollToBottom();
}

function createBotSkeleton() {
    const row = document.createElement('div');
    row.className = 'msg-row bot';
    row.innerHTML = `
        <div class="bubble">
            <div class="typing-vibe">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(row);
    scrollToBottom();
    return row;
}

// Check Backend Status
async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        if (data.status === "online") {
            statusBadge.style.display = "flex";
            if (!dbPathInput.value) dbPathInput.value = data.database_path;
        }
    } catch (e) {
        statusBadge.style.display = "none";
    }
}

// Connect to DB
connectBtn.addEventListener('click', async () => {
    const path = dbPathInput.value;
    if (!path) return;

    connectBtn.disabled = true;
    connectBtn.innerHTML = '<i data-lucide="loader-2" class="spin" size="16"></i> Indexing...';
    lucide.createIcons();

    try {
        const res = await fetch(`${API_BASE}/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ db_path: path })
        });
        const data = await res.json();

        const row = document.createElement('div');
        row.className = 'msg-row bot';

        if (res.ok) {
            row.innerHTML = `
                <div class="bubble">
                    <div style="color: var(--success); font-weight: 700; display:flex; align-items:center; gap:8px;">
                        <i data-lucide="check-circle" size="18"></i> 
                        Schema Synchronized
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
                        Successfully indexed <strong>${data.tables_indexed} tables</strong>. I am now schema-aware and ready for your queries.
                    </div>
                </div>`;
        } else {
            row.innerHTML = `<div class="bubble" style="border-color: var(--error);">❌ <strong>Connection Failed</strong><br>${data.detail || 'Generic error'}</div>`;
        }
        messagesContainer.appendChild(row);
        lucide.createIcons();
        scrollToBottom();
    } catch (e) {
        addUserMessage("System Error: Failed to reach internal intelligence service.");
    } finally {
        connectBtn.disabled = false;
        connectBtn.innerHTML = '<i data-lucide="refresh-cw" size="16"></i> Connect & Index';
        lucide.createIcons();
    }
});

// Send Query
sendBtn.addEventListener('click', async () => {
    const question = userInput.value.trim();
    if (!question) return;

    addUserMessage(question);
    userInput.value = '';
    userInput.style.height = 'auto';

    const loadingRow = createBotSkeleton();

    try {
        const isDashboard = dashboardToggle.checked;
        const endpoint = isDashboard ? '/generate-dashboard' : '/ask';

        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                explain: explainToggle.checked,
                generate_graph: graphToggle.checked
            })
        });
        const data = await res.json();

        const bubble = loadingRow.querySelector('.bubble');
        bubble.innerHTML = '';

        if (isDashboard) {
            renderDashboardPlan(bubble, data);
            return;
        }

        if (data.error) {
            bubble.innerHTML = `
                <div style="color: var(--error); font-weight: 600; margin-bottom: 0.5rem; display:flex; align-items:center; gap:8px;">
                    <i data-lucide="alert-circle" size="16"></i> Intelligence Error
                </div>
                <div style="font-size: 0.9rem;">${data.error}</div>
            `;
            if (data.sql) {
                const sqlSec = document.createElement('div');
                sqlSec.className = 'sql-container';
                sqlSec.innerHTML = `
                    <div class="sql-header">GENERATED SQL</div>
                    <div class="sql-code" style="color: var(--error)">${data.sql}</div>
                `;
                bubble.appendChild(sqlSec);
            }
            lucide.createIcons();
            return;
        }

        // 1. Explanation if exists
        if (data.explanation) {
            const ins = document.createElement('div');
            ins.className = 'insight-box';
            ins.innerHTML = `<strong>Quick Analysis:</strong><br>${data.explanation}`;
            bubble.appendChild(ins);
        }

        // 1.5. Graph if exists
        if (data.graph_image) {
            const graphContainer = document.createElement('div');
            graphContainer.style.position = 'relative';
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${data.graph_image}`;
            img.style.maxWidth = "100%";
            img.style.borderRadius = "12px";
            img.style.marginTop = "1rem";
            img.style.border = "1px solid var(--border-color)";

            const dlBtn = document.createElement('button');
            dlBtn.innerHTML = '<i data-lucide="download" size="14" color="white"></i>';
            dlBtn.style = 'position: absolute; top: 1.5rem; right: 0.5rem; padding: 6px 10px; border-radius: 6px; background: rgba(0, 0, 0, 0.75); border: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(4px); cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; transition: all 0.2s ease;';
            dlBtn.onmouseover = () => dlBtn.style.background = 'rgba(0, 0, 0, 0.9)';
            dlBtn.onmouseout = () => dlBtn.style.background = 'rgba(0, 0, 0, 0.75)';
            dlBtn.onclick = () => downloadImage(img.src, 'ChatSQL_Graph.png');

            graphContainer.appendChild(img);
            graphContainer.appendChild(dlBtn);
            bubble.appendChild(graphContainer);
        }

        // 2. Query Details (Foldable?)
        const sqlSec = document.createElement('div');
        sqlSec.className = 'sql-container';
        sqlSec.innerHTML = `
            <div class="sql-header">
                <span>SQL PIPELINE</span>
                <span class="admin-badge" style="background: var(--primary)">AUTO</span>
            </div>
            <div class="sql-code">${data.sql}</div>
        `;
        bubble.appendChild(sqlSec);

        // 3. Results Table
        if (data.rows && data.rows.length > 0) {
            const tblWrap = document.createElement('div');
            tblWrap.className = 'table-wrapper';
            const table = document.createElement('table');

            const thead = document.createElement('thead');
            const hRow = document.createElement('tr');
            data.columns.forEach(col => {
                const th = document.createElement('th');
                th.innerText = col;
                hRow.appendChild(th);
            });
            thead.appendChild(hRow);
            table.appendChild(thead);

            const tbody = document.createElement('tbody');
            data.rows.forEach(row => {
                const tr = document.createElement('tr');
                row.forEach(cell => {
                    const td = document.createElement('td');
                    td.innerText = cell === null ? 'NULL' : cell;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            tblWrap.appendChild(table);
            bubble.appendChild(tblWrap);

            const count = document.createElement('div');
            count.style = "font-size: 0.7rem; color: var(--text-muted); margin-top: 0.75rem; text-align: right; font-weight: 500;";
            count.innerText = `Retrieved ${data.row_count} records from internal DB`;
            bubble.appendChild(count);
        } else {
            bubble.innerHTML += `<div style="color: var(--text-muted); font-size: 0.9rem; margin-top: 1rem; font-style: italic;">The query executed successfully but returned zero matches.</div>`;
        }

        lucide.createIcons();
        scrollToBottom();

    } catch (e) {
        const bubble = loadingRow.querySelector('.bubble');
        bubble.innerHTML = `<div style="color: var(--error)">Critical: Communication with local LLM failed. Ensure Ollama is running.</div>`;
    }
    scrollToBottom();
});

function renderDashboardPlan(container, plan) {
    if (plan.error) {
        container.innerHTML = `<div style="color: var(--error)">${plan.error}</div>`;
        return;
    }

    container.innerHTML = `
        <h3 style="color: var(--primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="layout-dashboard"></i> ${plan.dashboard_title}
        </h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.5rem;">Intelligence-driven analytical overview generated locally.</p>
        <div class="dashboard-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;"></div>
    `;

    const grid = container.querySelector('.dashboard-grid');

    plan.components.forEach(comp => {
        const card = document.createElement('div');
        card.className = 'card';
        card.style.background = 'rgba(255, 255, 255, 0.02)';
        card.style.padding = '1rem';

        let visualHtml = '';
        if (comp.error) {
            visualHtml = `<div style="color: var(--error); font-size: 0.75rem;">Error: ${comp.error}</div>`;
        } else if (comp.chart_type === 'metric' && comp.data && comp.data.rows.length > 0) {
            const val = comp.data.rows[0][0];
            visualHtml = `<div style="font-size: 1.5rem; font-weight: 800; color: var(--success); margin: 0.5rem 0;">${val}</div>`;
        } else if (comp.image) {
            const imgId = `img-${Math.random().toString(36).substr(2, 9)}`;
            visualHtml = `
                <div style="position: relative;">
                    <img id="${imgId}" src="data:image/png;base64,${comp.image}" style="width: 100%; border-radius: 6px; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.05);">
                    <button onclick="downloadImage(document.getElementById('${imgId}').src, '${comp.title.replace(/\s+/g, '_')}.png')" 
                            style="position: absolute; top: 1rem; right: 0.5rem; padding: 5px 8px; border-radius: 6px; background: rgba(0, 0, 0, 0.75); border: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(4px); cursor: pointer; color: white; display: flex; align-items: center; justify-content: center;">
                        <i data-lucide="download" size="12"></i>
                    </button>
                </div>`;
        } else {
            visualHtml = `<div style="height: 100px; background: rgba(0,0,0,0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: var(--text-dim);">
                <i data-lucide="${getIcon(comp.chart_type)}" size="16"></i>
                <span style="margin-left: 8px;">${comp.chart_type.toUpperCase()} Visual Ready</span>
            </div>`;
        }

        card.innerHTML = `
            <div style="font-size: 0.8rem; font-weight: 700; margin-bottom: 0.25rem;">${comp.title}</div>
            <div style="font-size: 0.7rem; color: var(--text-dim); margin-bottom: 0.75rem;">${comp.description}</div>
            ${visualHtml}
            <div style="margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; opacity: 0.4; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">${comp.sql}</div>
        `;
        grid.appendChild(card);
    });

    lucide.createIcons();
}

function getIcon(type) {
    switch (type) {
        case 'line': return 'trending-up';
        case 'bar': return 'bar-chart-3';
        case 'pie': return 'pie-chart';
        case 'metric': return 'target';
        default: return 'help-circle';
    }
}

// Key bindings
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

checkStatus();
setInterval(checkStatus, 10000);

function downloadImage(dataUrl, filename) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
