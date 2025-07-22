<script>
	import { onMount } from 'svelte';
	import { commandQueue } from '$lib/stores/commandQueue.js';
	let accounts = [];
	let isLoading = false;

	async function fetchAccounts() {
		const res = await fetch('/api/admin/temp-accounts');
		accounts = await res.json();
	}

	async function toggleInUseStatus(account) {
		const newStatus = !account.is_in_use;
		try {
			const response = await fetch(`/api/admin/temp-accounts/${account.id}/status?is_in_use=${newStatus}`, {
				method: 'PUT'
			});
			const result = await response.json();
			if (!response.ok) throw new Error(result.detail);

			// Update the UI with the data from the backend response
			accounts = accounts.map(a => a.id === account.id ? result.updated_account : a);
			
			// Add the command to our queue instead of showing a modal
			commandQueue.update(queue => [...queue, result.powershell_command]);

		} catch (error) {
			alert(`Error: ${error.message}`);
		}
	}

	onMount(fetchAccounts);
</script>

<h2>Temporary Accounts Management</h2>

<div class="info-box">
	<h3>TEMP Account Status Control</h3>
	<p>Manage the availability status of temporary accounts. When you toggle an account's status, the corresponding PowerShell command will be added to your command queue.</p>
</div>

<h3>Cached TEMP Accounts</h3>
<table>
	<thead>
		<tr>
			<th>ID</th>
			<th>Display Name</th>
			<th>User Principal Name</th>
			<th>In Use?</th>
			<th>Action</th>
		</tr>
	</thead>
	<tbody>
		{#each accounts as acc (acc.id)}
			<tr>
				<td>{acc.id}</td>
				<td>{acc.display_name}</td>
				<td>{acc.user_principal_name}</td>
				<td>{acc.is_in_use ? 'Yes' : 'No'}</td>
				<td>
					<button on:click={() => toggleInUseStatus(acc)}>
						{acc.is_in_use ? 'Mark as Available' : 'Mark as In Use'}
					</button>
				</td>
			</tr>
		{/each}
	</tbody>
</table>

<style>
	.info-box {
		border: 1px solid #ddd;
		padding: 1.5rem;
		margin-bottom: 2rem;
		background-color: #f8f9fa;
		border-radius: 8px;
		border-left: 4px solid #0984e3;
	}
	
	.info-box h3 {
		margin-top: 0;
		color: #2d3436;
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
		color: #2d3436;
	}
	
	tr:hover {
		background-color: #f5f5f5;
	}
	
	button {
		background-color: #0984e3;
		color: white;
		border: none;
		padding: 0.75rem 1rem;
		cursor: pointer;
		border-radius: 6px;
		font-weight: 500;
		transition: background-color 0.2s;
	}
	
	button:hover {
		background-color: #0770d4;
	}
</style>
