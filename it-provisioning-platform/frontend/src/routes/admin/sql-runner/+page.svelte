<script>
    let query = 'SELECT * FROM users LIMIT 10;';
    let results = [];
    let headers = [];
    let error = '';
    let isLoading = false;
    let queryHistory = [];

    // Pre-defined useful queries
    const sampleQueries = [
        {
            name: "All Users",
            query: "SELECT id, full_name, email, role, service FROM users ORDER BY full_name;"
        },
        {
            name: "Recent Requests",
            query: "SELECT id, status, timestamp FROM requests ORDER BY timestamp DESC LIMIT 20;"
        },
        {
            name: "Audit Log Summary",
            query: "SELECT event_type, COUNT(*) as count FROM audit_logs GROUP BY event_type ORDER BY count DESC;"
        },
        {
            name: "TEMP Accounts Status",
            query: "SELECT display_name, user_principal_name, is_in_use FROM temp_accounts ORDER BY display_name;"
        },
        {
            name: "Request Status Breakdown",
            query: "SELECT status, COUNT(*) as count FROM requests GROUP BY status;"
        }
    ];

    async function runQuery() {
        if (!query.trim()) {
            error = 'Please enter a query';
            return;
        }

        error = '';
        isLoading = true;
        
        try {
            const response = await fetch('/api/admin/sql-query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Query failed');
            }

            results = data;
            headers = data.length > 0 ? Object.keys(data[0]) : [];
            
            // Add to query history (keep last 10)
            queryHistory = [query, ...queryHistory.filter(q => q !== query)].slice(0, 10);
        } catch (e) {
            error = e.message;
            results = [];
            headers = [];
        } finally {
            isLoading = false;
        }
    }

    function loadSampleQuery(sampleQuery) {
        query = sampleQuery.query;
    }

    function loadFromHistory(historicalQuery) {
        query = historicalQuery;
    }

    function exportToCSV() {
        if (results.length === 0) return;

        const csvContent = [
            headers.join(','),
            ...results.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'query_results.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }
</script>

<div class="page-container">
    <div class="page-header">
        <h2>🗃️ SQL Query Runner</h2>
        <p class="subtitle">Execute SELECT queries against the database for advanced reporting and analysis</p>
    </div>

    <div class="layout">
        <!-- Left Panel: Query Input -->
        <div class="query-panel">
            <div class="section">
                <h3>Query Editor</h3>
                <textarea 
                    bind:value={query} 
                    rows="8" 
                    placeholder="Enter your SELECT query here..."
                    class="query-editor"
                ></textarea>
                
                <div class="query-actions">
                    <button on:click={runQuery} disabled={isLoading} class="run-btn">
                        {isLoading ? '⏳ Running...' : '▶️ Run Query'}
                    </button>
                    
                    {#if results.length > 0}
                        <button on:click={exportToCSV} class="export-btn">
                            📊 Export CSV
                        </button>
                    {/if}
                </div>
            </div>

            <!-- Sample Queries -->
            <div class="section">
                <h3>📋 Sample Queries</h3>
                <div class="samples-grid">
                    {#each sampleQueries as sample}
                        <button 
                            on:click={() => loadSampleQuery(sample)} 
                            class="sample-btn"
                            title={sample.query}
                        >
                            {sample.name}
                        </button>
                    {/each}
                </div>
            </div>

            <!-- Query History -->
            {#if queryHistory.length > 0}
                <div class="section">
                    <h3>🕒 Recent Queries</h3>
                    <div class="history-list">
                        {#each queryHistory as historicalQuery}
                            <button 
                                on:click={() => loadFromHistory(historicalQuery)} 
                                class="history-btn"
                                title={historicalQuery}
                            >
                                {historicalQuery.length > 50 ? historicalQuery.substring(0, 50) + '...' : historicalQuery}
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>

        <!-- Right Panel: Results -->
        <div class="results-panel">
            <div class="section">
                <h3>Query Results</h3>
                
                {#if error}
                    <div class="error-message">
                        <strong>❌ Error:</strong> {error}
                    </div>
                {:else if isLoading}
                    <div class="loading-message">
                        ⏳ Executing query...
                    </div>
                {:else if results.length > 0}
                    <div class="results-info">
                        <span class="result-count">📊 {results.length} row{results.length === 1 ? '' : 's'} returned</span>
                    </div>
                    
                    <div class="table-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    {#each headers as header}
                                        <th>{header}</th>
                                    {/each}
                                </tr>
                            </thead>
                            <tbody>
                                {#each results as row}
                                    <tr>
                                        {#each headers as header}
                                            <td>{row[header] || ''}</td>
                                        {/each}
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {:else}
                    <div class="empty-message">
                        <p>💡 Enter a SELECT query and click "Run Query" to see results here.</p>
                        <p class="hint">Try one of the sample queries to get started!</p>
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>

<style>
    .page-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }

    .page-header {
        margin-bottom: 2rem;
        text-align: center;
    }

    .page-header h2 {
        margin: 0 0 0.5rem 0;
        color: #2d3436;
    }

    .subtitle {
        color: #636e72;
        margin: 0;
        font-size: 1rem;
    }

    .layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        align-items: start;
    }

    .query-panel, .results-panel {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }

    .section {
        padding: 1.5rem;
        border-bottom: 1px solid #e1e8ed;
    }

    .section:last-child {
        border-bottom: none;
    }

    .section h3 {
        margin: 0 0 1rem 0;
        color: #2d3436;
        font-size: 1.1rem;
    }

    .query-editor {
        width: 100%;
        padding: 1rem;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        resize: vertical;
        transition: border-color 0.2s;
    }

    .query-editor:focus {
        outline: none;
        border-color: #0984e3;
    }

    .query-actions {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }

    .run-btn {
        background: #00b894;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .run-btn:hover:not(:disabled) {
        background: #00a085;
    }

    .run-btn:disabled {
        background: #95a5a6;
        cursor: not-allowed;
    }

    .export-btn {
        background: #0984e3;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .export-btn:hover {
        background: #0770d4;
    }

    .samples-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.5rem;
    }

    .sample-btn {
        background: #74b9ff;
        color: white;
        border: none;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: background-color 0.2s;
        text-align: left;
    }

    .sample-btn:hover {
        background: #5fa3f7;
    }

    .history-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .history-btn {
        background: #f8f9fa;
        color: #2d3436;
        border: 1px solid #ddd;
        padding: 0.5rem;
        border-radius: 6px;
        font-size: 0.85rem;
        cursor: pointer;
        text-align: left;
        font-family: 'Courier New', monospace;
        transition: background-color 0.2s;
    }

    .history-btn:hover {
        background: #e9ecef;
    }

    .error-message {
        background: #ffe0e0;
        color: #d63031;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #d63031;
    }

    .loading-message {
        background: #e3f2fd;
        color: #1976d2;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    .empty-message {
        background: #f8f9fa;
        color: #636e72;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
    }

    .hint {
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    .results-info {
        margin-bottom: 1rem;
    }

    .result-count {
        background: #00b894;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .table-container {
        max-height: 400px;
        overflow: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
    }

    .results-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }

    .results-table th {
        background: #f8f9fa;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #2d3436;
        border-bottom: 2px solid #ddd;
        position: sticky;
        top: 0;
    }

    .results-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .results-table tr:hover {
        background: #f8f9fa;
    }

    @media (max-width: 1024px) {
        .layout {
            grid-template-columns: 1fr;
            gap: 1rem;
        }

        .samples-grid {
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        }
    }
</style>
