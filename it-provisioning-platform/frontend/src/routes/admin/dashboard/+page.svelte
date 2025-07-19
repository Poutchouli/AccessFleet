<script>
	import { onMount, onDestroy } from 'svelte';
	let requests = [];
	let ws;

	onMount(async () => {
		const response = await fetch('http://localhost:8000/requests/');
		requests = await response.json();

		// Establish WebSocket connection
		const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		ws = new WebSocket(`${wsProtocol}//localhost:8000/ws/admin-dashboard`);

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
	});

	onDestroy(() => {
		if (ws) {
			ws.close();
		}
	});

	async function changeStatus(requestId, newStatus) {
		await fetch(`http://localhost:8000/requests/${requestId}/status?status=${newStatus}`, {
			method: 'PUT'
		});
		// The UI will update via the WebSocket broadcast, not here.
	}
</script>

<h2>Admin Dashboard (Live)</h2>

<table border="1" style="width: 100%; margin-top: 1rem;">
	<thead>
		<tr>
			<th>ID</th>
			<th>Status</th>
			<th>Submitted By (ID)</th>
			<th>Form Definition ID</th>
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
				<td>{req.submitted_by_manager_id}</td>
				<td>{req.form_definition_id}</td>
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
</style>
