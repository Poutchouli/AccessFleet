<script>
	import { onMount } from 'svelte';

	let allUsers = [];
	let filteredUsers = [];
	let searchTerm = '';
	let expandedCardId = null;
	let isLoading = true;

	onMount(async () => {
		try {
			const response = await fetch('/api/users');
			if (!response.ok) throw new Error('Failed to fetch users');
			allUsers = await response.json();
			filteredUsers = allUsers;
		} catch (error) {
			console.error(error);
		} finally {
			isLoading = false;
		}
	});

	function toggleCard(userId) {
		expandedCardId = expandedCardId === userId ? null : userId;
	}

	$: {
		if (searchTerm) {
			const lowerTerm = searchTerm.toLowerCase();
			filteredUsers = allUsers.filter(user =>
				user.full_name.toLowerCase().includes(lowerTerm) ||
				user.email.toLowerCase().includes(lowerTerm) ||
				user.service?.toLowerCase().includes(lowerTerm) ||
				user.role.toLowerCase().includes(lowerTerm)
			);
		} else {
			filteredUsers = allUsers;
		}
	}
</script>

<div class="page-container">
	<div class="page-header">
		<h2>Users Directory</h2>
		<p class="subtitle">{filteredUsers.length} user{filteredUsers.length === 1 ? '' : 's'} found</p>
	</div>

	{#if isLoading}
		<div class="loading">
			<p>Loading users...</p>
		</div>
	{:else if allUsers.length === 0}
		<div class="empty-state">
			<h3>No Users Found</h3>
			<p>No users have been created yet. Create one via the API docs.</p>
		</div>
	{:else}
		<div class="search-section">
			<input 
				type="search" 
				bind:value={searchTerm} 
				placeholder="Search by name, email, service, or role..." 
				class="search-input"
			/>
		</div>

		{#if filteredUsers.length === 0}
			<div class="empty-state">
				<h3>No Matches Found</h3>
				<p>No users match your search criteria. Try adjusting your search term.</p>
			</div>
		{:else}
			<div class="user-grid">
				{#each filteredUsers as user (user.id)}
					<div 
						class="user-card" 
						class:expanded={expandedCardId === user.id} 
						on:click={() => toggleCard(user.id)}
						on:keydown={(e) => e.key === 'Enter' && toggleCard(user.id)}
						role="button"
						tabindex="0"
					>
						<div class="card-header">
							<div class="user-avatar">
								{user.full_name.charAt(0).toUpperCase()}
							</div>
							<div class="user-basic">
								<div class="name">{user.full_name}</div>
								<div class="role-badge role-{user.role}">{user.role}</div>
							</div>
							<div class="expand-icon">
								{expandedCardId === user.id ? '▼' : '▶'}
							</div>
						</div>
						
						{#if expandedCardId === user.id}
							<div class="card-body">
								<div class="info-row">
									<strong>📧 Email:</strong> 
									<a href="mailto:{user.email}" class="email-link">{user.email}</a>
								</div>
								<div class="info-row">
									<strong>🏢 Service:</strong> 
									<span>{user.service || 'Not specified'}</span>
								</div>
								<div class="info-row">
									<strong>🆔 User ID:</strong> 
									<span class="user-id">{user.id}</span>
								</div>
								{#if user.title}
									<div class="info-row">
										<strong>💼 Title:</strong> 
										<span>{user.title}</span>
									</div>
								{/if}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.page-container {
		max-width: 1200px;
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

	.loading, .empty-state {
		text-align: center;
		padding: 3rem;
		color: #636e72;
	}

	.empty-state h3 {
		color: #2d3436;
		margin-bottom: 1rem;
	}

	.search-section {
		margin-bottom: 2rem;
	}

	.search-input {
		width: 100%;
		padding: 1rem;
		font-size: 1rem;
		border: 2px solid #ddd;
		border-radius: 8px;
		transition: border-color 0.2s;
	}

	.search-input:focus {
		outline: none;
		border-color: #0984e3;
	}

	.user-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 1.5rem;
	}

	.user-card {
		border: 1px solid #e1e8ed;
		border-radius: 12px;
		padding: 1.5rem;
		cursor: pointer;
		transition: all 0.2s ease-in-out;
		background: white;
		box-shadow: 0 2px 4px rgba(0,0,0,0.05);
	}

	.user-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		border-color: #74b9ff;
	}

	.user-card.expanded {
		border-color: #0984e3;
		box-shadow: 0 6px 20px rgba(9, 132, 227, 0.15);
	}

	.card-header {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.user-avatar {
		width: 50px;
		height: 50px;
		border-radius: 50%;
		background: linear-gradient(135deg, #74b9ff, #0984e3);
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-weight: bold;
		font-size: 1.2rem;
		flex-shrink: 0;
	}

	.user-basic {
		flex: 1;
	}

	.name {
		font-weight: 600;
		font-size: 1.1rem;
		color: #2d3436;
		margin-bottom: 0.25rem;
	}

	.role-badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.8rem;
		font-weight: 500;
		text-transform: capitalize;
	}

	.role-admin {
		background-color: #ff7675;
		color: white;
	}

	.role-manager {
		background-color: #74b9ff;
		color: white;
	}

	.role-user {
		background-color: #00b894;
		color: white;
	}

	.expand-icon {
		color: #636e72;
		font-size: 1.2rem;
		transition: transform 0.2s;
	}

	.user-card.expanded .expand-icon {
		transform: rotate(90deg);
	}

	.card-body {
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid #e1e8ed;
	}

	.info-row {
		display: flex;
		align-items: center;
		margin-bottom: 0.75rem;
		gap: 0.5rem;
	}

	.info-row:last-child {
		margin-bottom: 0;
	}

	.info-row strong {
		min-width: 120px;
		color: #2d3436;
		font-size: 0.9rem;
	}

	.email-link {
		color: #0984e3;
		text-decoration: none;
	}

	.email-link:hover {
		text-decoration: underline;
	}

	.user-id {
		font-family: monospace;
		background: #f8f9fa;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	@media (max-width: 768px) {
		.page-container {
			padding: 1rem;
		}

		.user-grid {
			grid-template-columns: 1fr;
			gap: 1rem;
		}

		.user-card {
			padding: 1rem;
		}

		.user-avatar {
			width: 40px;
			height: 40px;
			font-size: 1rem;
		}

		.info-row {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.25rem;
		}

		.info-row strong {
			min-width: auto;
		}
	}
</style>
