<script>
	import { onMount } from 'svelte';
	
	let mailboxes = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/shared-mailboxes');
			if (!response.ok) {
				throw new Error('Failed to fetch shared mailboxes');
			}
			mailboxes = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="container">
	<h2>📮 Shared Mailboxes</h2>
	<p>View all imported shared mailboxes and their access permissions.</p>

	{#if loading}
		<div class="loading">
			<p>Loading mailboxes...</p>
		</div>
	{:else if error}
		<div class="error">
			<p>Error: {error}</p>
		</div>
	{:else if mailboxes.length > 0}
		<div class="mailboxes-grid">
			{#each mailboxes as mailbox}
				<div class="mailbox-card">
					<div class="mailbox-header">
						<h3>{mailbox.display_name}</h3>
						<span class="email">{mailbox.primary_smtp_address}</span>
					</div>
					<div class="access-section">
						<h4>Full Access Users:</h4>
						{#if mailbox.full_access_users}
							<div class="users-list">
								{#each mailbox.full_access_users.split(';').filter(u => u.trim()) as user}
									<span class="user-tag">{user.trim()}</span>
								{/each}
							</div>
						{:else}
							<span class="no-users">No full access users defined</span>
						{/if}
					</div>
				</div>
			{/each}
		</div>
		<div class="summary">
			<p><strong>Total Shared Mailboxes:</strong> {mailboxes.length}</p>
		</div>
	{:else}
		<div class="empty-state">
			<p>No shared mailboxes found. Use the <a href="/admin/initialize">Data Initialization</a> page to import mailboxes from your Exchange environment.</p>
		</div>
	{/if}
</div>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	h2 {
		color: #1f2937;
		margin-bottom: 0.5rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	p {
		color: #6b7280;
		margin-bottom: 2rem;
	}

	.loading, .error, .empty-state {
		text-align: center;
		padding: 3rem;
		background: #f9fafb;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
	}

	.error {
		background: #fef2f2;
		border-color: #fecaca;
		color: #991b1b;
	}

	.mailboxes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.mailbox-card {
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1.5rem;
		box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
		transition: box-shadow 0.2s;
	}

	.mailbox-card:hover {
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	.mailbox-header {
		margin-bottom: 1rem;
		border-bottom: 1px solid #f3f4f6;
		padding-bottom: 1rem;
	}

	.mailbox-header h3 {
		margin: 0 0 0.5rem 0;
		color: #374151;
		font-size: 1.25rem;
	}

	.email {
		color: #6b7280;
		font-size: 0.9rem;
		font-family: 'Courier New', monospace;
		background: #f3f4f6;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
	}

	.access-section h4 {
		margin: 0 0 0.75rem 0;
		color: #374151;
		font-size: 1rem;
	}

	.users-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.user-tag {
		background: #dbeafe;
		color: #1e40af;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.875rem;
		border: 1px solid #93c5fd;
	}

	.no-users {
		color: #9ca3af;
		font-style: italic;
	}

	.summary {
		background: #f0f9ff;
		border: 1px solid #bae6fd;
		border-radius: 8px;
		padding: 1rem;
		text-align: center;
	}

	.summary p {
		margin: 0;
		color: #0c4a6e;
	}

	.empty-state a {
		color: #4f46e5;
		text-decoration: underline;
	}

	@media (max-width: 768px) {
		.mailboxes-grid {
			grid-template-columns: 1fr;
		}
		
		.container {
			padding: 1rem;
		}
	}
</style>
