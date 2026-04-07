const userToken = localStorage.getItem('user_token') || localStorage.getItem('admin_token');

function handleResponseStatus(res) {
    if (res.status === 401 || res.status === 403) {
        logout();
        throw new Error("Session expired. Please login again.");
    }
    return res;
}

// --- User Info & History ---
function initializeUser() {
    try {
        const payload = JSON.parse(atob(userToken.split('.')[1]));
        const username = payload.sub;
        document.getElementById('display-username').innerText = username;
        document.getElementById('user-avatar').innerText = username[0].toUpperCase();
        loadHistory();
    } catch (e) { console.error("Init fail", e); }
}

async function loadHistory() {
    if (!userToken) return;
    try {
        const res = await fetch('/history', {
            headers: { 'Authorization': `Bearer ${userToken}` }
        });
        handleResponseStatus(res);
        const data = await res.json();
        renderHistory(data.history);
    } catch (e) { console.error("History fail", e); }
}

async function clearHistory() {
    if (!confirm("Are you sure you want to delete all chat history?")) return;
    try {
        const res = await fetch('/history/clear', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${userToken}` }
        });
        handleResponseStatus(res);
        loadHistory();
    } catch (e) { console.error("Clear fail", e); }
}

async function deleteChatItem(chatId) {
    if (!confirm("Delete this conversation?")) return;
    try {
        const res = await fetch(`/history/${chatId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${userToken}` }
        });
        handleResponseStatus(res);
        loadHistory();
    } catch (e) { console.error("Delete fail", e); }
}

function renderHistory(history) {
    const container = document.getElementById('history-list');
    if (!history || history.length === 0) {
        container.innerHTML = `<div style="padding: 2rem; text-align: center; color: var(--text-dim); font-size: 0.8rem;">No past conversations</div>`;
        return;
    }
    container.innerHTML = '';
    history.forEach(item => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.style = "display: flex; align-items: center; justify-content: space-between; position: relative;";
        
        const content = document.createElement('div');
        content.style = "flex: 1; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 8px;";
        content.innerHTML = `<i data-lucide="message-square" size="14" style="min-width: 14px"></i><span>${item.prompt}</span>`;
        content.onclick = () => showHistoryItem(item);
        
        const delBtn = document.createElement('button');
        delBtn.style = "background: none; border: none; color: var(--error); cursor: pointer; padding: 4px; opacity: 0; transition: opacity 0.2s; display: flex; align-items: center; justify-content: center;";
        delBtn.innerHTML = '<i data-lucide="trash-2" size="14"></i>';
        delBtn.onclick = (e) => {
            e.stopPropagation();
            deleteChatItem(item.id);
        };
        
        div.appendChild(content);
        div.appendChild(delBtn);
        
        // Show delete button on hover
        div.onmouseenter = () => delBtn.style.opacity = '1';
        div.onmouseleave = () => delBtn.style.opacity = '0';
        
        container.appendChild(div);
    });
    lucide.createIcons();
}

function showHistoryItem(item) {
    messagesContainer.innerHTML = '';
    addUserMessage(item.prompt);
    addBotMessage(JSON.parse(item.response_json));
}

function addBotMessage(data) {
    const row = document.createElement('div');
    row.className = 'msg-row bot';
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    row.appendChild(bubble);
    messagesContainer.appendChild(row);

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
    } else {
        // 1. Explanation
        if (data.explanation) {
            const ins = document.createElement('div');
            ins.className = 'insight-box';
            ins.innerHTML = `<strong>Quick Analysis:</strong><br>${data.explanation}`;
            bubble.appendChild(ins);
        }

        // 2. Graph
        if (data.graph_image) {
            const graphContainer = document.createElement('div');
            graphContainer.style.position = 'relative';
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${data.graph_image}`;
            img.style.maxWidth = "100%";
            img.style.borderRadius = "12px";
            img.style.marginTop = "1rem";
            img.style.border = "1px solid var(--border-color)";
            graphContainer.appendChild(img);

            // Add download button
            const dlBtn = document.createElement('button');
            dlBtn.className = "graph-download-btn";
            dlBtn.innerHTML = '<i data-lucide="download"></i> <span>Save</span>';
            dlBtn.onclick = (e) => {
                e.stopPropagation();
                downloadImage(img.src, `charts_export_${Date.now()}.png`);
            };
            graphContainer.appendChild(dlBtn);

            bubble.appendChild(graphContainer);
        }

        // 3. SQL
        if (data.sql) {
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
        }

        // 4. Table
        if (data.rows && data.rows.length > 0) {
            const exportToolbar = document.createElement('div');
            exportToolbar.className = 'export-toolbar';
            const csvBtn = document.createElement('button');
            csvBtn.className = 'btn-export';
            csvBtn.innerHTML = '<i data-lucide="download"></i> Export CSV';
            csvBtn.onclick = () => downloadCSV(data.columns, data.rows, `query_export_${Date.now()}.csv`);
            exportToolbar.appendChild(csvBtn);
            bubble.appendChild(exportToolbar);

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
            data.rows.forEach(r => {
                const tr = document.createElement('tr');
                r.forEach(cell => {
                    const td = document.createElement('td');
                    td.innerText = cell === null ? 'NULL' : cell;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            tblWrap.appendChild(table);
            bubble.appendChild(tblWrap);
        } else if (data.sql) {
            const emptyHint = document.createElement('div');
            emptyHint.style = "color: var(--text-muted); font-size: 0.85rem; margin-top: 1rem; font-style: italic;";
            emptyHint.innerText = "The query executed successfully but returned zero matches.";
            bubble.appendChild(emptyHint);
        }
    }

    lucide.createIcons();
    scrollToBottom();
}

if (userToken) {
    window.addEventListener('DOMContentLoaded', initializeUser);
}

function logout() {
    localStorage.removeItem('user_token');
    localStorage.removeItem('admin_token');
    window.location.href = '/login';
}

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
        const res = await fetch('/status');
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
    connectBtn.innerHTML = '<i data-lucide="refresh-cw" class="spin" size="16"></i> Indexing...';
    lucide.createIcons();

    try {
        const res = await fetch('/connect', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userToken}`
            },
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

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userToken}`
            },
            body: JSON.stringify({
                question,
                explain: explainToggle.checked,
                generate_graph: graphToggle.checked
            })
        });
        const data = await res.json();
        loadHistory(); 

        loadingRow.remove(); // Remove skeleton
        addBotMessage(data); // Use common renderer

    } catch (e) {
        const bubble = loadingRow.querySelector('.bubble');
        if (bubble) {
            bubble.innerHTML = `<div style="color: var(--error)">Critical: Communication with local LLM failed. Ensure Ollama is running.</div>`;
        }
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

function downloadCSV(columns, rows, filename) {
    const csvContent = [
        columns.join(','),
        ...rows.map(r => r.join(','))
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

function downloadImage(dataUrl, filename) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
