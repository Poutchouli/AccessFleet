<script>
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/session.js';

	let tables = [];
	let selectedTable = null;
	let tableContent = [];
	let tableHeaders = [];
	let isLoading = false;
	let error = null;

	onMount(async () => {
		if (!$user || $user.role !== 'admin') {
			error = 'Access denied. Admin privileges required.';
			return;
		}
		
		try {
			const response = await fetch('/api/admin/db/tables', {
				headers: { 'user-id': $user.id.toString() }
			});
			
			if (!response.ok) {
				throw new Error('Failed to fetch table list');
			}
			
			tables = await response.json();
		} catch (err) {
			error = `Error loading tables: ${err.message}`;
		}
	});

	async function fetchTableContent(tableName) {
		isLoading = true;
		error = null;
		selectedTable = tableName;
		
		try {
			const response = await fetch(`/api/admin/db/tables/${tableName}`, {
				headers: { 'user-id': $user.id.toString() }
			});
			
			if (!response.ok) {
				throw new Error(`Failed to fetch table content: ${response.statusText}`);
			}
			
			tableContent = await response.json();
			
			if (tableContent.length > 0) {
				tableHeaders = Object.keys(tableContent[0]);
			} else {
				tableHeaders = [];
			}
		} catch (err) {
			error = `Error loading table content: ${err.message}`;
			tableContent = [];
			tableHeaders = [];
		} finally {
			isLoading = false;
		}
	}

	function formatValue(value) {
		if (value === null || value === undefined) {
			return 'NULL';
		}
		if (typeof value === 'object') {
			return JSON.stringify(value, null, 2);
		}
		return String(value);
	}
</script>

<svelte:head>
	<title>Database Explorer - AccessFleet Admin</title>
</svelte:head>

{#if $user?.role === 'admin'}
	<div class="page-header">
		<h2>Database Explorer</h2>
		<p class="subtitle">View and explore database tables (Admin only)</p>
	</div>

	{#if error}
		<div class="error-message">
			<strong>Error:</strong> {error}
		</div>
	{/if}

	<div class="container">
		<div class="sidebar">
			<h4>Database Tables ({tables.length})</h4>
			<ul class="table-list">
				{#each tables as table}
					<li class:active={table === selectedTable}>
						<button on:click={() => fetchTableContent(table)} class="table-btn">
							{table}
						</button>
					</li>
				{/each}
			</ul>
		</div>

		<div class="content">
			{#if selectedTable}
				<div class="table-header">
					<h4>Table: <strong>{selectedTable}</strong></h4>
					<p class="table-info">Showing up to 100 rows</p>
				</div>
				
				{#if isLoading}
					<div class="loading">
						<p>Loading table content...</p>
					</div>
				{:else if tableContent.length === 0}
					<div class="empty-state">
						<p>No data found in this table.</p>
					</div>
				{:else}
					<div class="table-stats">
						<p><strong>Rows:</strong> {tableContent.length} | <strong>Columns:</strong> {tableHeaders.length}</p>
					</div>
					
					<div class="table-wrapper">
						<table class="data-table">
							<thead>
								<tr>
									{#each tableHeaders as header}
										<th>{header}</th>
									{/each}
								</tr>
							</thead>
							<tbody>
								{#each tableContent as row}
									<tr>
										{#each tableHeaders as header}
											<td>
												<div class="cell-content">
													{formatValue(row[header])}
												</div>
											</td>
										{/each}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			{:else}
				<div class="welcome-state">
					<h4>Welcome to Database Explorer</h4>
					<p>Select a table from the sidebar to view its content and structure.</p>
					<div class="features">
						<h5>Features:</h5>
						<ul>
							<li>View all database tables</li>
							<li>Explore table content (up to 100 rows)</li>
							<li>Inspect data structure and values</li>
							<li>JSON formatting for complex data</li>
						</ul>
					</div>
				</div>
			{/if}
		</div>
	</div>
{:else}
	<div class="access-denied">
		<h2>Access Denied</h2>
		<p>You need admin privileges to access the database explorer.</p>
		<a href="/admin/dashboard" class="back-link">← Back to Admin Dashboard</a>
	</div>
{/if}

<style>
	.page-header {
		margin-bottom: 2rem;
	}

	.subtitle {
		color: #6b7280;
		margin-top: 0.5rem;
	}

	.error-message {
		background-color: #fef2f2;
		border: 1px solid #fecaca;
		color: #dc2626;
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1rem;
	}

	.container {
		display: grid;
		grid-template-columns: 250px 1fr;
		gap: 2rem;
		height: calc(100vh - 200px);
	}

	.sidebar {
		background-color: #f9fafb;
		padding: 1.5rem;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
		overflow-y: auto;
	}

	.sidebar h4 {
		margin-top: 0;
		color: #374151;
		border-bottom: 1px solid #e5e7eb;
		padding-bottom: 0.5rem;
	}

	.table-list {
		list-style: none;
		padding: 0;
		margin: 1rem 0 0 0;
	}

	.table-btn {
		width: 100%;
		text-align: left;
		background: none;
		border: none;
		padding: 0.75rem;
		cursor: pointer;
		border-radius: 6px;
		transition: background-color 0.2s;
		font-family: monospace;
		font-size: 0.9rem;
	}

	.table-btn:hover {
		background-color: #e5e7eb;
	}

	.table-list li.active .table-btn {
		background-color: #3b82f6;
		color: white;
		font-weight: bold;
	}

	.content {
		background-color: white;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.table-header {
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
		background-color: #f9fafb;
	}

	.table-header h4 {
		margin: 0;
		color: #374151;
	}

	.table-info {
		margin: 0.5rem 0 0 0;
		color: #6b7280;
		font-size: 0.9rem;
	}

	.table-stats {
		padding: 1rem 1.5rem;
		background-color: #f3f4f6;
		border-bottom: 1px solid #e5e7eb;
		font-size: 0.9rem;
	}

	.table-stats p {
		margin: 0;
		color: #374151;
	}

	.loading, .empty-state {
		padding: 3rem;
		text-align: center;
		color: #6b7280;
	}

	.welcome-state {
		padding: 3rem;
		text-align: center;
	}

	.welcome-state h4 {
		color: #374151;
		margin-bottom: 1rem;
	}

	.features {
		background-color: #f9fafb;
		padding: 1.5rem;
		border-radius: 8px;
		margin-top: 2rem;
		text-align: left;
		max-width: 400px;
		margin-left: auto;
		margin-right: auto;
	}

	.features h5 {
		margin-top: 0;
		color: #374151;
	}

	.features ul {
		margin: 0.5rem 0 0 0;
		color: #6b7280;
	}

	.table-wrapper {
		flex: 1;
		overflow: auto;
		padding: 0;
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.875rem;
	}

	.data-table th {
		background-color: #f9fafb;
		border: 1px solid #e5e7eb;
		padding: 0.75rem;
		text-align: left;
		font-weight: 600;
		color: #374151;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.data-table td {
		border: 1px solid #e5e7eb;
		padding: 0;
		vertical-align: top;
		max-width: 300px;
	}

	.cell-content {
		padding: 0.75rem;
		white-space: pre-wrap;
		word-break: break-word;
		overflow-wrap: break-word;
		max-height: 200px;
		overflow-y: auto;
		font-family: monospace;
		font-size: 0.8rem;
		line-height: 1.4;
	}

	.access-denied {
		text-align: center;
		padding: 3rem;
	}

	.access-denied h2 {
		color: #dc2626;
		margin-bottom: 1rem;
	}

	.back-link {
		color: #3b82f6;
		text-decoration: none;
		font-weight: 500;
	}

	.back-link:hover {
		text-decoration: underline;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.container {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
		
		.sidebar {
			height: auto;
			max-height: 200px;
		}
	}
</style>
