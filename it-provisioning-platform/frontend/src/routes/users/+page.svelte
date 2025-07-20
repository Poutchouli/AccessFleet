<script>
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	let users = [];
	let isLoading = true;

	onMount(async () => {
		try {
			const response = await fetch('/api/users');
			if (!response.ok) throw new Error('Failed to fetch users');
			users = await response.json();
		} catch (error) {
			console.error(error);
		} finally {
			isLoading = false;
		}
	});
</script>

<h2>Users</h2>

{#if isLoading}
	<p>Loading users...</p>
{:else if users.length === 0}
	<p>No users found. Create one via the API docs.</p>
{:else}
	<table>
		<thead>
			<tr>
				<th>ID</th>
				<th>Name</th>
				<th>Email</th>
				<th>Role</th>
			</tr>
		</thead>
		<tbody>
			{#each users as user}
				<tr>
					<td>{user.id}</td>
					<td>{user.full_name}</td>
					<td>{user.email}</td>
					<td>{user.role}</td>
				</tr>
			{/each}
		</tbody>
	</table>
{/if}

<style>
	table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
	}
	th,
	td {
		border: 1px solid #ddd;
		padding: 8px;
		text-align: left;
	}
	th {
		background-color: #f2f2f2;
	}
</style>
