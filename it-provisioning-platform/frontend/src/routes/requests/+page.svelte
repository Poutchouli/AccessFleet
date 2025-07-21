<script>
	import { onMount } from 'svelte';
	let requests = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/requests');
			if (!response.ok) {
				throw new Error('Failed to fetch requests');
			}
			requests = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="container">
	<h2>Submitted Requests</h2>

	<div class="actions">
		<a href="/requests/new" class="btn btn-primary">Submit a New Request</a>
	</div>

	{#if loading}
		<p>Loading requests...</p>
	{:else if error}
		<p class="error">Error: {error}</p>
	{:else if requests.length > 0}
		<div class="table-container">
			<table>
				<thead>
					<tr>
						<th>ID</th>
						<th>Status</th>
						<th>Submitted By</th>
						<th>Form</th>
						<th>Assigned Account</th>
						<th>Submitted Data</th>
					</tr>
				</thead>
				<tbody>
					{#each requests as req}
						<tr>
							<td><a href="/requests/{req.id}" class="request-link">{req.id}</a></td>
							<td>
								<span class="status status-{req.status}">{req.status}</span>
							</td>
							<td>
								{#if req.submitted_by}
									<div class="user-info">
										<strong>{req.submitted_by.full_name}</strong>
										<br><small>{req.submitted_by.email}</small>
										{#if req.submitted_by.service}
											<br><small>📍 {req.submitted_by.service}</small>
										{/if}
									</div>
								{:else}
									<em>Unknown User</em>
								{/if}
							</td>
							<td>
								{#if req.form_definition}
									<div class="form-info">
										<strong>{req.form_definition.name}</strong>
										{#if req.form_definition.description}
											<br><small>{req.form_definition.description}</small>
										{/if}
									</div>
								{:else}
									<em>Unknown Form</em>
								{/if}
							</td>
							<td>
								{#if req.assigned_temp_account}
									<div class="account-info">
										<strong>{req.assigned_temp_account.display_name}</strong>
										<br><small>{req.assigned_temp_account.user_principal_name}</small>
										<span class="status {req.assigned_temp_account.is_in_use ? 'status-in-use' : 'status-available'}">
											{req.assigned_temp_account.is_in_use ? 'In Use' : 'Available'}
										</span>
									</div>
								{:else}
									<em>No Account Assigned</em>
								{/if}
							</td>
							<td>
								<details>
									<summary>View Data</summary>
									<pre class="form-data">{JSON.stringify(req.form_data, null, 2)}</pre>
								</details>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{:else}
		<p>No requests found. <a href="/requests/new">Submit your first request</a>.</p>
	{/if}
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
	}

	.actions {
		margin-bottom: 20px;
	}

	.btn {
		display: inline-block;
		padding: 10px 20px;
		background-color: #007bff;
		color: white;
		text-decoration: none;
		border-radius: 4px;
		border: none;
		cursor: pointer;
	}

	.btn:hover {
		background-color: #0056b3;
	}

	.btn-primary {
		background-color: #007bff;
	}

	.table-container {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
		background: white;
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	th, td {
		padding: 12px;
		text-align: left;
		border-bottom: 1px solid #ddd;
	}

	th {
		background-color: #f8f9fa;
		font-weight: 600;
	}

	tr:hover {
		background-color: #f5f5f5;
	}

	.status {
		padding: 4px 8px;
		border-radius: 4px;
		font-size: 0.85em;
		font-weight: 500;
		text-transform: capitalize;
	}

	.status-pending {
		background-color: #ffeaa7;
		color: #d63031;
	}

	.status-in_progress {
		background-color: #81ecec;
		color: #00b894;
	}

	.status-completed {
		background-color: #a8e6cf;
		color: #00b894;
	}

	.status-rejected {
		background-color: #ff7675;
		color: white;
	}

	.status-in-use {
		background-color: #ff7675;
		color: white;
	}

	.status-available {
		background-color: #a8e6cf;
		color: #00b894;
	}

	.user-info, .form-info, .account-info {
		line-height: 1.4;
	}

	.user-info strong, .form-info strong, .account-info strong {
		color: #2d3436;
	}

	.user-info small, .form-info small, .account-info small {
		color: #636e72;
		font-size: 0.85em;
	}

	.request-link {
		color: #0984e3;
		text-decoration: none;
		font-weight: 600;
	}

	.request-link:hover {
		text-decoration: underline;
	}

	.form-data {
		background-color: #f8f9fa;
		padding: 10px;
		border-radius: 4px;
		font-size: 0.85em;
		max-width: 300px;
		overflow-x: auto;
	}

	.error {
		color: #d63031;
		background-color: #ffeaa7;
		padding: 10px;
		border-radius: 4px;
	}

	details {
		cursor: pointer;
	}

	summary {
		font-weight: 500;
		color: #007bff;
	}

	.request-link {
		color: #007bff;
		text-decoration: none;
		font-weight: 500;
	}

	.request-link:hover {
		text-decoration: underline;
	}
</style>
