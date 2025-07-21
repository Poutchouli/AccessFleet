<script>
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/session.js';
	import { invalidateAll } from '$app/navigation';
	import { goto } from '$app/navigation';

	let managers = [];
	let mailboxes = [];
	let currentPermissions = [];
	let selectedManagerId = null;
	let selectedMailboxId = null;
	let message = '';
	let messageType = ''; // 'success' or 'error'
	let isLoading = false;
	let isAssigning = false;

	onMount(async () => {
		if (!$user || $user.role !== 'admin') {
			message = 'Access denied. Admin privileges required.';
			messageType = 'error';
			return;
		}
		
		await loadData();
	});

	async function loadData() {
		isLoading = true;
		try {
			// Fetch all users and filter managers
			const usersRes = await fetch('/api/users', {
				headers: { 'user-id': $user.id.toString() }
			});
			if (!usersRes.ok) throw new Error('Failed to fetch users');
			const allUsers = await usersRes.json();
			managers = allUsers.filter(u => u.role === 'manager');

			// Fetch all shared mailboxes
			const mailboxesRes = await fetch('/api/shared-mailboxes', {
				headers: { 'user-id': $user.id.toString() }
			});
			if (!mailboxesRes.ok) throw new Error('Failed to fetch mailboxes');
			mailboxes = await mailboxesRes.json();

			// Fetch current permissions
			const permissionsRes = await fetch('/api/admin/permissions/manager-mailboxes', {
				headers: { 'user-id': $user.id.toString() }
			});
			if (!permissionsRes.ok) throw new Error('Failed to fetch permissions');
			currentPermissions = await permissionsRes.json();

		} catch (error) {
			message = `Error loading data: ${error.message}`;
			messageType = 'error';
		} finally {
			isLoading = false;
		}
	}

	async function assignPermission() {
		if (!selectedManagerId || !selectedMailboxId) {
			message = 'Please select both a manager and a mailbox.';
			messageType = 'error';
			return;
		}

		isAssigning = true;
		message = 'Assigning permission...';
		messageType = '';

		try {
			const response = await fetch(`/api/admin/permissions/mailbox-to-manager?manager_id=${selectedManagerId}&mailbox_id=${selectedMailboxId}`, {
				method: 'POST',
				headers: { 'user-id': $user.id.toString() }
			});
			
			const result = await response.json();
			if (!response.ok) throw new Error(result.detail);
			
			message = result.message;
			messageType = 'success';
			
			// Reset form
			selectedManagerId = null;
			selectedMailboxId = null;
			
			// Reload permissions to show the new assignment
			await loadData();
			
		} catch (error) {
			message = `Error: ${error.message}`;
			messageType = 'error';
		} finally {
			isAssigning = false;
		}
	}

	async function revokePermission(managerId, mailboxId) {
		if (!confirm('Are you sure you want to revoke this permission?')) {
			return;
		}

		try {
			const response = await fetch(`/api/admin/permissions/mailbox-to-manager?manager_id=${managerId}&mailbox_id=${mailboxId}`, {
				method: 'DELETE',
				headers: { 'user-id': $user.id.toString() }
			});
			
			const result = await response.json();
			if (!response.ok) throw new Error(result.detail);
			
			message = result.message;
			messageType = 'success';
			
			// Reload permissions to show the removal
			await loadData();
			
		} catch (error) {
			message = `Error: ${error.message}`;
			messageType = 'error';
		}
	}

	function getManagerName(managerId) {
		const manager = managers.find(m => m.id === managerId);
		return manager ? manager.full_name : 'Unknown Manager';
	}

	function getMailboxName(mailboxId) {
		const mailbox = mailboxes.find(m => m.id === mailboxId);
		return mailbox ? mailbox.display_name : 'Unknown Mailbox';
	}
</script>

<svelte:head>
	<title>Mailbox Permissions - AccessFleet Admin</title>
</svelte:head>

{#if $user?.role === 'admin'}
	<div class="page-header">
		<h2>Mailbox Permissions Management</h2>
		<p class="subtitle">Assign managers to shared mailboxes they can manage</p>
	</div>

	{#if message}
		<div class="message {messageType}">
			{message}
		</div>
	{/if}

	{#if isLoading}
		<div class="loading">
			<p>Loading data...</p>
		</div>
	{:else}
		<div class="content-grid">
			<!-- Assignment Form -->
			<div class="assignment-section">
				<h3>Assign New Permission</h3>
				<div class="form-container">
					<div class="form-group">
						<label for="manager-select">Manager:</label>
						<select id="manager-select" bind:value={selectedManagerId} disabled={isAssigning}>
							<option value={null}>-- Select a Manager --</option>
							{#each managers as manager}
								<option value={manager.id}>{manager.full_name} ({manager.service || 'No service'})</option>
							{/each}
						</select>
					</div>

					<div class="form-group">
						<label for="mailbox-select">Shared Mailbox:</label>
						<select id="mailbox-select" bind:value={selectedMailboxId} disabled={isAssigning}>
							<option value={null}>-- Select a Mailbox --</option>
							{#each mailboxes as mailbox}
								<option value={mailbox.id}>{mailbox.display_name} ({mailbox.primary_smtp_address})</option>
							{/each}
						</select>
					</div>

					<button 
						on:click={assignPermission} 
						disabled={!selectedManagerId || !selectedMailboxId || isAssigning}
						class="assign-btn"
					>
						{isAssigning ? 'Assigning...' : 'Assign Permission'}
					</button>
				</div>

				<div class="stats">
					<p><strong>Available Managers:</strong> {managers.length}</p>
					<p><strong>Available Mailboxes:</strong> {mailboxes.length}</p>
				</div>
			</div>

			<!-- Current Permissions -->
			<div class="permissions-section">
				<h3>Current Permissions ({currentPermissions.length} managers)</h3>
				<div class="permissions-list">
					{#each currentPermissions as permission}
						<div class="permission-card">
							<div class="permission-header">
								<h4>{permission.manager_name}</h4>
								<span class="mailbox-count">{permission.visible_mailboxes.length} mailbox(es)</span>
							</div>
							<div class="mailboxes">
								{#each permission.visible_mailboxes as mailbox}
									<div class="mailbox-item">
										<div class="mailbox-info">
											<strong>{mailbox.display_name}</strong>
											<span class="email">{mailbox.primary_smtp_address}</span>
										</div>
										<button 
											class="revoke-btn"
											on:click={() => revokePermission(permission.manager_id, mailbox.id)}
											title="Revoke permission"
										>
											×
										</button>
									</div>
								{/each}
							</div>
						</div>
					{:else}
						<div class="empty-state">
							<p>No permissions assigned yet.</p>
							<p>Use the form on the left to assign managers to mailboxes.</p>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
{:else}
	<div class="access-denied">
		<h2>Access Denied</h2>
		<p>You need admin privileges to manage mailbox permissions.</p>
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

	.message {
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1.5rem;
		font-weight: 500;
	}

	.message.success {
		background-color: #f0fdf4;
		border: 1px solid #bbf7d0;
		color: #166534;
	}

	.message.error {
		background-color: #fef2f2;
		border: 1px solid #fecaca;
		color: #dc2626;
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: #6b7280;
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		align-items: start;
	}

	.assignment-section,
	.permissions-section {
		background-color: white;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1.5rem;
	}

	.assignment-section h3,
	.permissions-section h3 {
		margin-top: 0;
		margin-bottom: 1.5rem;
		color: #374151;
		border-bottom: 1px solid #e5e7eb;
		padding-bottom: 0.5rem;
	}

	.form-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-weight: 500;
		color: #374151;
	}

	.form-group select {
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		background-color: white;
		font-size: 0.875rem;
	}

	.form-group select:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.assign-btn {
		background-color: #3b82f6;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
		margin-top: 0.5rem;
	}

	.assign-btn:hover:not(:disabled) {
		background-color: #2563eb;
	}

	.assign-btn:disabled {
		background-color: #9ca3af;
		cursor: not-allowed;
	}

	.stats {
		margin-top: 1.5rem;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
		font-size: 0.875rem;
		color: #6b7280;
	}

	.stats p {
		margin: 0.25rem 0;
	}

	.permissions-list {
		max-height: 600px;
		overflow-y: auto;
	}

	.permission-card {
		background-color: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.permission-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
	}

	.permission-header h4 {
		margin: 0;
		color: #374151;
		font-size: 1rem;
	}

	.mailbox-count {
		background-color: #3b82f6;
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.mailboxes {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.mailbox-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		background-color: white;
		padding: 0.75rem;
		border-radius: 4px;
		border: 1px solid #e5e7eb;
	}

	.mailbox-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.email {
		font-size: 0.75rem;
		color: #6b7280;
		font-family: monospace;
	}

	.revoke-btn {
		background-color: #dc2626;
		color: white;
		border: none;
		width: 24px;
		height: 24px;
		border-radius: 50%;
		cursor: pointer;
		font-weight: bold;
		font-size: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: background-color 0.2s;
	}

	.revoke-btn:hover {
		background-color: #b91c1c;
	}

	.empty-state {
		text-align: center;
		padding: 3rem;
		color: #6b7280;
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
		.content-grid {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
	}
</style>
