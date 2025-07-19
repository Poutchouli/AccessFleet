<script>
	import { onMount } from 'svelte';
	let logs = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/admin/audit-log');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			logs = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	});

	function formatTimestamp(ts) {
		return new Date(ts).toLocaleString();
	}

	function formatEventType(eventType) {
		return eventType.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
	}
</script>

<h2>Audit Log</h2>
<p>Immutable record of all significant actions performed within the system.</p>

{#if loading}
	<p>Loading audit logs...</p>
{:else if error}
	<p class="error">Error loading audit logs: {error}</p>
{:else if logs.length === 0}
	<p>No audit logs found.</p>
{:else}
	<div class="table-container">
		<table>
			<thead>
				<tr>
					<th>Timestamp</th>
					<th>Actor ID</th>
					<th>Event Type</th>
					<th>Details</th>
				</tr>
			</thead>
			<tbody>
				{#each logs as log (log.id)}
					<tr>
						<td class="timestamp">{formatTimestamp(log.timestamp)}</td>
						<td class="actor">{log.actor_id}</td>
						<td class="event-type">{formatEventType(log.event_type)}</td>
						<td class="details">
							<details>
								<summary>View Details</summary>
								<pre>{JSON.stringify(log.details, null, 2)}</pre>
							</details>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<style>
	.table-container {
		overflow-x: auto;
		border: 1px solid #e2e8f0;
		border-radius: 5px;
	}
	
	table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
		background-color: white;
	}
	
	th, td {
		border: 1px solid #e2e8f0;
		padding: 0.75rem;
		text-align: left;
		vertical-align: top;
	}
	
	th {
		background-color: #f7fafc;
		font-weight: bold;
		position: sticky;
		top: 0;
	}
	
	.timestamp {
		white-space: nowrap;
		font-family: monospace;
		font-size: 0.9em;
	}
	
	.actor {
		text-align: center;
		font-weight: bold;
		color: #2d3748;
	}
	
	.event-type {
		font-weight: 500;
		color: #2b6cb0;
		white-space: nowrap;
	}
	
	.details {
		max-width: 400px;
	}
	
	details {
		cursor: pointer;
	}
	
	summary {
		color: #2b6cb0;
		font-weight: 500;
		padding: 0.25rem;
		border-radius: 3px;
	}
	
	summary:hover {
		background-color: #ebf8ff;
	}
	
	pre {
		margin: 0.5rem 0 0 0;
		white-space: pre-wrap;
		word-break: break-all;
		background-color: #f7fafc;
		padding: 0.5rem;
		border-radius: 3px;
		font-size: 0.85em;
		max-height: 200px;
		overflow-y: auto;
	}
	
	.error {
		color: #e53e3e;
		background-color: #fed7d7;
		padding: 1rem;
		border-radius: 5px;
		border: 1px solid #feb2b2;
	}
	
	tbody tr:nth-child(even) {
		background-color: #f9fafb;
	}
	
	tbody tr:hover {
		background-color: #edf2f7;
	}
</style>
