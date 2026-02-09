const API_BASE = "";

const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const connectBtn = document.getElementById('connect-btn');
const dbPathInput = document.getElementById('db-path');
const statusBadge = document.getElementById('connection-status');
const explainToggle = document.getElementById('explain-toggle');
const graphToggle = document.getElementById('graph-toggle');

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Helper to create bot message skeleton
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

function scrollToBottom() {
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// Add user message to UI
function addUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'msg-row user';
    row.innerHTML = `<div class="bubble">${text}</div>`;
    messagesContainer.appendChild(row);
    scrollToBottom();
}

// Check Backend Status
async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        if (data.status === "online") {
            statusBadge.innerHTML = '<div class="status-dot"></div> Systems Online';
            statusBadge.style.color = "var(--success)";
            if (!dbPathInput.value) dbPathInput.value = data.database_path;
        }
    } catch (e) {
        statusBadge.innerHTML = '<div class="status-dot" style="background: var(--error); box-shadow: 0 0 10px var(--error);"></div> Offline';
        statusBadge.style.color = "var(--error)";
    }
}

// Connect to DB
connectBtn.addEventListener('click', async () => {
    const path = dbPathInput.value;
    if (!path) return;

    connectBtn.disabled = true;
    connectBtn.innerText = "Indexing...";

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
            row.innerHTML = `<div class="bubble">✅ <strong>Schema Synchronized</strong><br>Successfully indexed ${data.tables_indexed} tables from your database. I'm ready for your queries.</div>`;
        } else {
            row.innerHTML = `<div class="bubble" style="border-color: var(--error);">❌ <strong>Connection Failed</strong><br>${data.detail || 'Generic error'}</div>`;
        }
        messagesContainer.appendChild(row);
        scrollToBottom();
    } catch (e) {
        addUserMessage("System Error: Failed to reach backend.");
    } finally {
        connectBtn.disabled = false;
        connectBtn.innerText = "Connect & Index";
    }
});

// Send Query
sendBtn.addEventListener('click', async () => {
    const question = userInput.value.trim();
    if (!question) return;

    addUserMessage(question);
    userInput.value = '';
    userInput.style.height = 'auto'; // Reset height

    const loadingRow = createBotSkeleton();

    try {
        const res = await fetch(`${API_BASE}/ask`, {
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
        bubble.innerHTML = ''; // Clear skeleton

        if (data.error) {
            bubble.innerHTML = `
                <div style="color: var(--error); font-weight: 600; margin-bottom: 0.5rem;">Intelligence Error</div>
                <div style="font-size: 0.9rem;">${data.error}</div>
            `;
            if (data.sql) {
                const sqlSec = document.createElement('div');
                sqlSec.className = 'sql-container';
                sqlSec.innerHTML = `
                    <div class="sql-header">GENERATED SQL</div>
                    <div class="sql-code">${data.sql}</div>
                `;
                bubble.appendChild(sqlSec);
            }
            return;
        }

        // 1. Explanation if exists
        if (data.explanation) {
            const ins = document.createElement('div');
            ins.className = 'insight-box';
            ins.innerHTML = `<strong>Quick Summary:</strong><br>${data.explanation}`;
            bubble.appendChild(ins);
        }

        // 1.5. Graph if exists
        if (data.graph_image) {
            const graphDiv = document.createElement('div');
            graphDiv.className = 'graph-wrapper';
            graphDiv.style.marginTop = "1rem";
            graphDiv.innerHTML = `<img src="data:image/png;base64,${data.graph_image}" alt="Data Visualization" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">`;
            bubble.appendChild(graphDiv);
        }

        // 2. SQL Query
        const sqlSec = document.createElement('div');
        sqlSec.className = 'sql-container';
        sqlSec.innerHTML = `
            <div class="sql-header">
                <span>SQL QUERY</span>
                <span style="font-size: 0.6rem; letter-spacing: 0;">AUTO-GENERATED</span>
            </div>
            <div class="sql-code">${data.sql}</div>
        `;
        bubble.appendChild(sqlSec);

        // 3. Results Table
        if (data.rows && data.rows.length > 0) {
            const tblWrap = document.createElement('div');
            tblWrap.className = 'table-wrapper';
            const table = document.createElement('table');

            // Header
            const thead = document.createElement('thead');
            const hRow = document.createElement('tr');
            data.columns.forEach(col => {
                const th = document.createElement('th');
                th.innerText = col;
                hRow.appendChild(th);
            });
            thead.appendChild(hRow);
            table.appendChild(thead);

            // Body
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
            count.style = "font-size: 0.75rem; color: var(--text-muted); margin-top: 0.75rem; text-align: right;";
            count.innerText = `Retrieved ${data.row_count} records`;
            bubble.appendChild(count);
        } else {
            const empty = document.createElement('div');
            empty.style = "color: var(--text-muted); font-size: 0.9rem; margin-top: 1rem; font-style: italic;";
            empty.innerText = "The query returned no results.";
            bubble.appendChild(empty);
        }

        scrollToBottom();

    } catch (e) {
        const bubble = loadingRow.querySelector('.bubble');
        bubble.innerHTML = "System Error: Failed to process request.";
        console.error(e);
    }
});

// Allow Enter to send, Shift+Enter for new line
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// Initial load
checkStatus();
setInterval(checkStatus, 10000); // Heartbeat
