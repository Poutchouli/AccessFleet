<script>
	import { onMount, onDestroy } from 'svelte';
	let requests = [];
	let ws;
	let isPolling = false;
	let pollInterval;
	let connectionStatus = 'Connecting...';

	onMount(async () => {
		// Load initial data
		await loadRequests();

		// Try to establish WebSocket connection with fallback to polling
		connectWebSocket();
	});

	async function loadRequests() {
		try {
			const response = await fetch('/api/requests/');
			requests = await response.json();
		} catch (error) {
			console.error('Failed to load requests:', error);
		}
	}

	function connectWebSocket() {
		try {
			const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			ws = new WebSocket(`${wsProtocol}//localhost:8000/ws/admin-dashboard`);

			ws.onopen = () => {
				connectionStatus = 'Connected (Live)';
				isPolling = false;
				if (pollInterval) {
					clearInterval(pollInterval);
					pollInterval = null;
				}
			};

			ws.onmessage = (event) => {
				const message = JSON.parse(event.data);

				if (message.type === 'new_request') {
					requests = [message.data, ...requests];
				} else if (message.type === 'status_update') {
					requests = requests.map((req) =>
						req.id === message.data.id ? { ...req, status: message.data.status } : req
					);
				}
			};

			ws.onerror = (error) => {
				console.warn('WebSocket error, falling back to polling:', error);
				fallbackToPolling();
			};

			ws.onclose = () => {
				console.warn('WebSocket closed, falling back to polling');
				fallbackToPolling();
			};

		} catch (error) {
			console.warn('WebSocket connection failed, using polling:', error);
			fallbackToPolling();
		}
	}

	function fallbackToPolling() {
		connectionStatus = 'Connected (Polling)';
		isPolling = true;
		
		if (ws) {
			ws.close();
			ws = null;
		}

		// Poll for updates every 5 seconds
		if (!pollInterval) {
			pollInterval = setInterval(loadRequests, 5000);
		}
	}

	onDestroy(() => {
		if (ws) {
			ws.close();
		}
		if (pollInterval) {
			clearInterval(pollInterval);
		}
	});

	async function changeStatus(requestId, newStatus) {
		try {
			await fetch(`/api/requests/${requestId}/status?status=${newStatus}`, {
				method: 'PUT'
			});
			
			// If using polling, refresh immediately
			if (isPolling) {
				await loadRequests();
			}
			// Otherwise, the UI will update via the WebSocket broadcast
		} catch (error) {
			console.error('Failed to update status:', error);
			alert('Failed to update request status');
		}
	}
</script>

<h2>Admin Dashboard</h2>

<div class="connection-status">
	<span class="status-indicator" class:polling={isPolling} class:connected={!isPolling}>
		{connectionStatus}
	</span>
</div>

<table border="1" style="width: 100%; margin-top: 1rem;">
	<thead>
		<tr>
			<th>ID</th>
			<th>Status</th>
			<th>Submitted By</th>
			<th>Form</th>
			<th>Assigned Account</th>
			<th>Change Status</th>
		</tr>
	</thead>
	<tbody>
		{#each requests as req (req.id)}
			<tr>
				<td>{req.id}</td>
				<td>
					<span class="status-badge status-{req.status}">
						{req.status}
					</span>
				</td>
				<td>
					{#if req.submitted_by}
						<div class="user-compact">
							<strong>{req.submitted_by.full_name}</strong>
							<br><small>{req.submitted_by.service || 'No service'}</small>
						</div>
					{:else}
						<em>Unknown</em>
					{/if}
				</td>
				<td>
					{#if req.form_definition}
						<strong>{req.form_definition.name}</strong>
					{:else}
						<em>Unknown Form</em>
					{/if}
				</td>
				<td>
					{#if req.assigned_temp_account}
						<div class="account-compact">
							<strong>{req.assigned_temp_account.display_name}</strong>
							<br><small class="status-badge {req.assigned_temp_account.is_in_use ? 'status-in-use' : 'status-available'}">
								{req.assigned_temp_account.is_in_use ? 'In Use' : 'Available'}
							</small>
						</div>
					{:else}
						<em>Not Assigned</em>
					{/if}
				</td>
				<td>
					<select on:change={(e) => changeStatus(req.id, e.target.value)} value={req.status}>
						<option value="pending">Pending</option>
						<option value="in_progress">In Progress</option>
						<option value="completed">Completed</option>
						<option value="rejected">Rejected</option>
					</select>
				</td>
			</tr>
		{/each}
	</tbody>
</table>

<style>
	table {
		border-collapse: collapse;
		font-family: Arial, sans-serif;
	}
	
	th, td {
		padding: 0.5rem;
		text-align: left;
		border: 1px solid #ddd;
	}
	
	th {
		background-color: #f2f2f2;
		font-weight: bold;
	}
	
	.status-badge {
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
		font-size: 0.8rem;
		font-weight: bold;
		text-transform: uppercase;
	}
	
	.status-pending {
		background-color: #fef3c7;
		color: #92400e;
	}
	
	.status-in_progress {
		background-color: #dbeafe;
		color: #1e40af;
	}
	
	.status-completed {
		background-color: #d1fae5;
		color: #065f46;
	}
	
	.status-rejected {
		background-color: #fee2e2;
		color: #991b1b;
	}
	
	select {
		padding: 0.25rem;
		border: 1px solid #ccc;
		border-radius: 0.25rem;
	}

	.user-compact, .account-compact {
		line-height: 1.3;
	}

	.user-compact strong, .account-compact strong {
		font-size: 0.9em;
		color: #2d3436;
	}

	.user-compact small, .account-compact small {
		color: #636e72;
		font-size: 0.75em;
	}

	.status-in-use {
		background-color: #fee2e2;
		color: #991b1b;
	}

	.status-available {
		background-color: #d1fae5;
		color: #065f46;
	}

	.connection-status {
		margin-bottom: 1rem;
		padding: 0.5rem;
		background-color: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 0.375rem;
		text-align: center;
	}

	.status-indicator {
		padding: 0.375rem 0.75rem;
		border-radius: 0.375rem;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.status-indicator.connected {
		background-color: #d1fae5;
		color: #065f46;
	}

	.status-indicator.polling {
		background-color: #fef3c7;
		color: #92400e;
	}
</style>
