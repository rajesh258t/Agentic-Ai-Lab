document.addEventListener('DOMContentLoaded', () => {
  // State Management
  const state = {
    activeDatabase: 'ecommerce',
    activeTab: 'playground',
    tools: [],
    selectedTool: null,
    chartInstance: null
  };

  // Preset Questions Mapping
  const PRESET_QUESTIONS = {
    ecommerce: [
      "Which customer has spent the highest total amount on orders?",
      "List all products along with their category name and price sorted from most expensive to least expensive.",
      "How many total orders have been placed in the system?"
    ],
    hr: [
      "Which employee has the highest salary and in which department do they work?",
      "What is the average employee salary per department?",
      "List all projects currently 'In Progress' along with their department location."
    ],
    university: [
      "List all students enrolled in Computer Science courses with an 'A' grade.",
      "Which instructor teaches the course with the highest credits?",
      "How many total students are enrolled in each department?"
    ]
  };

  // DOM Selectors
  const dbSelect = document.getElementById('db-select');
  const navTabs = document.querySelectorAll('.nav-tab');
  const tabPages = document.querySelectorAll('.tab-page');

  // Playground Elements
  const questionInput = document.getElementById('question-input');
  const btnRunAgent = document.getElementById('btn-run-agent');
  const presetButtonsContainer = document.getElementById('preset-buttons');
  const traceContainer = document.getElementById('trace-container');
  const agentLoader = document.getElementById('agent-loader');
  const finalAnswerCard = document.getElementById('final-answer-card');
  const finalAnswerText = document.getElementById('final-answer-text');
  const metricSteps = document.getElementById('metric-steps');
  const metricStatus = document.getElementById('metric-status');

  // Tool Explorer Elements
  const toolList = document.getElementById('tool-list');
  const activeToolTitle = document.getElementById('active-tool-title');
  const activeToolDesc = document.getElementById('active-tool-desc');
  const toolInputsForm = document.getElementById('tool-inputs-form');
  const btnExecTool = document.getElementById('btn-exec-tool');
  const toolOutputJson = document.getElementById('tool-output-json');

  // Schema Elements
  const schemaErdGrid = document.getElementById('schema-erd-grid');
  const btnRefreshSchema = document.getElementById('btn-refresh-schema');

  // Benchmark Elements
  const btnRunBenchmark = document.getElementById('btn-run-benchmark');
  const bmAcc = document.getElementById('bm-acc');
  const bmSteps = document.getElementById('bm-steps');
  const bmTotal = document.getElementById('bm-total');
  const benchmarkList = document.getElementById('benchmark-list');

  // SQL Console Elements
  const sqlConsoleInput = document.getElementById('sql-console-input');
  const btnRunSql = document.getElementById('btn-run-sql');
  const sqlTimer = document.getElementById('sql-timer');
  const sqlResultsTable = document.getElementById('sql-results-table');

  // --- INITIALIZATION ---
  init();

  function init() {
    setupEventListeners();
    renderPresets();
    fetchToolRegistry();
    fetchSchema();
  }

  function setupEventListeners() {
    // DB Switch
    dbSelect.addEventListener('change', (e) => {
      state.activeDatabase = e.target.value;
      renderPresets();
      fetchSchema();
    });

    // Tab Navigation
    navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        navTabs.forEach(t => t.classList.remove('active'));
        tabPages.forEach(p => p.classList.remove('active'));

        tab.classList.add('active');
        document.getElementById(`tab-${targetTab}`).classList.add('active');
        state.activeTab = targetTab;
      });
    });

    // Run Agent
    btnRunAgent.addEventListener('click', runReActAgent);

    // Refresh Schema
    btnRefreshSchema.addEventListener('click', fetchSchema);

    // Run Tool Action
    btnExecTool.addEventListener('click', executeSelectedTool);

    // Run Benchmark
    btnRunBenchmark.addEventListener('click', runBenchmarkSuite);

    // Run Direct SQL
    btnRunSql.addEventListener('click', runDirectSQL);
  }

  // --- PRESETS ---
  function renderPresets() {
    presetButtonsContainer.innerHTML = '';
    const presets = PRESET_QUESTIONS[state.activeDatabase] || [];
    presets.forEach(q => {
      const btn = document.createElement('button');
      btn.className = 'preset-btn';
      btn.innerHTML = `<i class="fa-solid fa-arrow-right-long"></i> ${q}`;
      btn.addEventListener('click', () => {
        questionInput.value = q;
        runReActAgent();
      });
      presetButtonsContainer.appendChild(btn);
    });
  }

  // --- REACT AGENT EXECUTION ---
  async function runReActAgent() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Reset UI
    traceContainer.innerHTML = '';
    finalAnswerCard.classList.add('hidden');
    agentLoader.classList.remove('hidden');
    metricSteps.textContent = '0 Steps';
    metricStatus.textContent = 'Reasoning...';

    if (state.chartInstance) {
      state.chartInstance.destroy();
      state.chartInstance = null;
    }

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          database: state.activeDatabase
        })
      });
      const data = await res.json();
      agentLoader.classList.add('hidden');

      if (data.success && data.agent_result) {
        renderReActTrajectory(data.agent_result);
      } else {
        traceContainer.innerHTML = `<div class="empty-state"><p>Error executing ReAct agent query.</p></div>`;
      }
    } catch (err) {
      agentLoader.classList.add('hidden');
      traceContainer.innerHTML = `<div class="empty-state"><p>API Connection Exception: ${err.message}</p></div>`;
    }
  }

  function renderReActTrajectory(result) {
    const steps = result.trajectory || [];
    metricSteps.textContent = `${result.total_steps} Steps`;
    metricStatus.textContent = result.solved ? 'Solved' : 'Max Steps Reached';

    if (steps.length === 0) {
      traceContainer.innerHTML = `<div class="empty-state"><p>No steps generated by agent.</p></div>`;
      return;
    }

    traceContainer.innerHTML = '';
    let chartDataCandidate = null;

    steps.forEach((step) => {
      if (step.is_final) return; // Handled separately below

      const stepCard = document.createElement('div');
      stepCard.className = 'react-step-card';

      const obsJson = typeof step.observation === 'object' 
        ? JSON.stringify(step.observation, null, 2) 
        : String(step.observation);

      let actionContent = '';
      if (step.action_name) {
        const inputStr = typeof step.action_input === 'object'
          ? JSON.stringify(step.action_input)
          : String(step.action_input);
        actionContent = `<div class="action-box"><span>Action:</span> ${step.action_name} <span>Input:</span> ${inputStr}</div>`;
      }

      // Check if observation contains rows to plot a chart later
      if (step.observation && step.observation.result && step.observation.result.rows) {
        chartDataCandidate = step.observation.result;
      }

      stepCard.innerHTML = `
        <div class="step-header-row">
          <span class="step-num-badge">STEP ${step.step_number}</span>
          ${step.action_name ? `<span class="step-tool-badge"><i class="fa-solid fa-wrench"></i> ${step.action_name}</span>` : ''}
        </div>
        <div class="thought-text"><strong>Thought:</strong> ${step.thought}</div>
        ${actionContent}
        <div class="observation-box">
          <strong style="color: var(--text-muted); display: block; margin-bottom: 4px;">Observation:</strong>
          <pre style="margin: 0;">${obsJson}</pre>
        </div>
      `;

      traceContainer.appendChild(stepCard);
    });

    // Final Answer
    if (result.final_answer) {
      finalAnswerText.innerHTML = result.final_answer;
      finalAnswerCard.classList.remove('hidden');

      if (chartDataCandidate && chartDataCandidate.rows && chartDataCandidate.rows.length > 1) {
        renderPlaygroundChart(chartDataCandidate);
      }
    }
  }

  // --- CHART RENDERING ---
  function renderPlaygroundChart(data) {
    const canvas = document.getElementById('playground-chart');
    if (!canvas) return;

    const rows = data.rows;
    const cols = data.columns;

    if (!rows || rows.length < 2 || !cols || cols.length < 2) return;

    const labelCol = cols[0];
    const valueCol = cols[1];

    const labels = rows.map(r => r[labelCol]);
    const values = rows.map(r => typeof r[valueCol] === 'number' ? r[valueCol] : parseFloat(r[valueCol]) || 0);

    if (state.chartInstance) {
      state.chartInstance.destroy();
    }

    state.chartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: valueCol,
          data: values,
          backgroundColor: 'rgba(0, 242, 254, 0.5)',
          borderColor: '#00F2FE',
          borderWidth: 1.5,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#F1F5F9', font: { family: 'Inter' } } }
        },
        scales: {
          x: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }

  // --- TOOL SANDBOX ---
  async function fetchToolRegistry() {
    try {
      const res = await fetch('/api/tools');
      const data = await res.json();
      if (data.success) {
        state.tools = data.tools;
        renderToolList();
      }
    } catch (err) {
      console.error('Failed to fetch tool registry:', err);
    }
  }

  function renderToolList() {
    toolList.innerHTML = '';
    state.tools.forEach(tool => {
      const card = document.createElement('div');
      card.className = 'tool-card-item';
      card.innerHTML = `
        <h4><i class="fa-solid fa-code-branch"></i> ${tool.name}</h4>
        <p>${tool.description}</p>
      `;
      card.addEventListener('click', () => selectTool(tool, card));
      toolList.appendChild(card);
    });

    if (state.tools.length > 0) {
      selectTool(state.tools[0], toolList.children[0]);
    }
  }

  function selectTool(tool, cardEl) {
    state.selectedTool = tool;
    document.querySelectorAll('.tool-card-item').forEach(c => c.classList.remove('active'));
    if (cardEl) cardEl.classList.add('active');

    activeToolTitle.textContent = tool.name;
    activeToolDesc.textContent = tool.description;
    btnExecTool.disabled = false;

    // Render Input Fields
    toolInputsForm.innerHTML = '';
    const props = tool.parameters.properties || {};
    
    if (Object.keys(props).length === 0) {
      toolInputsForm.innerHTML = `<p style="font-size: 0.85rem; color: var(--text-muted);">This tool requires no input parameters.</p>`;
    } else {
      for (const [key, schema] of Object.entries(props)) {
        const field = document.createElement('div');
        field.style.marginBottom = '0.75rem';
        field.innerHTML = `
          <label style="display: block; font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.25rem;">${key} (${schema.type})</label>
          <input type="text" id="param-${key}" placeholder="${schema.description || ''}" class="styled-select" style="width: 100%; padding-left: 0.85rem;">
        `;
        toolInputsForm.appendChild(field);
      }
    }
  }

  async function executeSelectedTool() {
    if (!state.selectedTool) return;

    const toolName = state.selectedTool.name;
    const props = state.selectedTool.parameters.properties || {};
    const params = {};

    for (const key of Object.keys(props)) {
      const val = document.getElementById(`param-${key}`).value.trim();
      if (val) params[key] = val;
    }

    toolOutputJson.textContent = 'Executing tool...';

    try {
      const res = await fetch('/api/tool/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: toolName,
          database: state.activeDatabase,
          params: params
        })
      });
      const data = await res.json();
      toolOutputJson.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      toolOutputJson.textContent = `Error executing tool: ${err.message}`;
    }
  }

  // --- SCHEMA ERD BROWSER ---
  async function fetchSchema() {
    schemaErdGrid.innerHTML = '<p style="color: var(--text-muted);">Loading database schema...</p>';
    try {
      const res = await fetch(`/api/schema?db=${state.activeDatabase}`);
      const data = await res.json();
      if (data.success && data.result) {
        renderSchemaGrid(data.result.tables || []);
      }
    } catch (err) {
      schemaErdGrid.innerHTML = `<p style="color: red;">Error fetching schema: ${err.message}</p>`;
    }
  }

  function renderSchemaGrid(tables) {
    schemaErdGrid.innerHTML = '';
    tables.forEach(t => {
      const card = document.createElement('div');
      card.className = 'erd-card';

      const cols = t.columns || [];
      const colItems = cols.map(c => `
        <div class="erd-col-item">
          <span class="erd-col-name">${c.pk ? '<span class="pk-badge">PK</span>' : ''}${c.name}</span>
          <span class="erd-col-type">${c.type}</span>
        </div>
      `).join('');

      card.innerHTML = `
        <div class="erd-card-header">
          <h3><i class="fa-solid fa-table"></i> ${t.table_name}</h3>
          <span class="badge badge-purple">${cols.length} Cols</span>
        </div>
        <div class="erd-col-list">
          ${colItems}
        </div>
      `;
      schemaErdGrid.appendChild(card);
    });
  }

  // --- BENCHMARK RUNNER ---
  async function runBenchmarkSuite() {
    btnRunBenchmark.disabled = true;
    benchmarkList.innerHTML = '<p style="color: var(--accent-cyan);">Executing 5 benchmark test cases against E-Commerce, HR, and University databases...</p>';

    try {
      const res = await fetch('/api/benchmark');
      const data = await res.json();
      btnRunBenchmark.disabled = false;

      if (data.success && data.benchmark) {
        const bm = data.benchmark;
        bmAcc.textContent = `${bm.execution_accuracy_rate}%`;
        bmSteps.textContent = `${bm.average_steps_per_query}`;
        bmTotal.textContent = `${bm.total_cases} Cases`;

        renderBenchmarkList(bm.results || []);
      }
    } catch (err) {
      btnRunBenchmark.disabled = false;
      benchmarkList.innerHTML = `<p style="color: red;">Benchmark execution failed: ${err.message}</p>`;
    }
  }

  function renderBenchmarkList(results) {
    benchmarkList.innerHTML = '';
    results.forEach(r => {
      const card = document.createElement('div');
      card.className = 'bm-item-card';
      card.innerHTML = `
        <div class="bm-header">
          <strong>[${r.id}] ${r.question}</strong>
          <span class="badge ${r.solved ? 'badge-emerald' : 'badge-purple'}">${r.solved ? 'PASSED' : 'FAILED'}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">
          Database: <span style="color: var(--accent-cyan);">${r.database}</span> | Steps: ${r.steps_taken}
        </div>
      `;
      benchmarkList.appendChild(card);
    });
  }

  // --- DIRECT SQL CONSOLE ---
  async function runDirectSQL() {
    const query = sqlConsoleInput.value.trim();
    if (!query) return;

    sqlResultsTable.innerHTML = '<p style="color: var(--text-muted);">Executing query...</p>';
    const startTime = performance.now();

    try {
      const res = await fetch('/api/custom_sql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sql_query: query,
          database: state.activeDatabase
        })
      });
      const data = await res.json();
      const duration = (performance.now() - startTime).toFixed(2);
      sqlTimer.textContent = `${duration} ms`;

      if (data.success && data.result) {
        renderSQLTable(data.result);
      } else {
        sqlResultsTable.innerHTML = `<p style="color: #FF007F;">${data.error || 'Execution failed'}</p>`;
      }
    } catch (err) {
      sqlResultsTable.innerHTML = `<p style="color: #FF007F;">Exception: ${err.message}</p>`;
    }
  }

  function renderSQLTable(result) {
    const rows = result.rows || [];
    const cols = result.columns || [];

    if (rows.length === 0) {
      sqlResultsTable.innerHTML = '<p style="color: var(--text-muted);">Query executed successfully. 0 rows returned.</p>';
      return;
    }

    let html = '<table class="data-table"><thead><tr>';
    cols.forEach(c => { html += `<th>${c}</th>`; });
    html += '</tr></thead><tbody>';

    rows.forEach(r => {
      html += '<tr>';
      cols.forEach(c => { html += `<td>${r[c] !== null ? r[c] : 'null'}</td>`; });
      html += '</tr>';
    });

    html += '</tbody></table>';
    sqlResultsTable.innerHTML = html;
  }
});
