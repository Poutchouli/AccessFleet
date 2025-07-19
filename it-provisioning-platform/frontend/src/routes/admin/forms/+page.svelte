<script>
	import { onMount } from 'svelte';
	
	let forms = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/form-definitions');
			if (!response.ok) {
				throw new Error('Failed to fetch forms');
			}
			forms = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	});
</script>

<style>
	.container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
	}

	.create-btn {
		background: #4CAF50;
		color: white;
		padding: 10px 20px;
		text-decoration: none;
		border-radius: 5px;
		font-weight: bold;
	}

	.create-btn:hover {
		background: #45a049;
	}

	.forms-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 20px;
	}

	.form-card {
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 20px;
		background: white;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		transition: box-shadow 0.2s;
	}

	.form-card:hover {
		box-shadow: 0 4px 8px rgba(0,0,0,0.15);
	}

	.form-title {
		font-size: 1.2em;
		font-weight: bold;
		margin-bottom: 10px;
		color: #333;
	}

	.form-description {
		color: #666;
		margin-bottom: 15px;
	}

	.form-meta {
		font-size: 0.9em;
		color: #888;
		border-top: 1px solid #eee;
		padding-top: 10px;
	}

	.loading {
		text-align: center;
		padding: 40px;
		color: #666;
	}

	.error {
		background: #ffebee;
		color: #c62828;
		padding: 15px;
		border-radius: 5px;
		margin-bottom: 20px;
	}

	.empty-state {
		text-align: center;
		padding: 60px 20px;
		color: #666;
	}

	.empty-state h3 {
		margin-bottom: 10px;
		color: #333;
	}

	.form-actions {
		margin-top: 15px;
		text-align: center;
	}

	.view-btn {
		background: #2196F3;
		color: white;
		text-decoration: none;
		padding: 8px 16px;
		border-radius: 4px;
		font-size: 0.9em;
		display: inline-block;
		transition: background 0.2s;
	}

	.view-btn:hover {
		background: #1976D2;
	}
</style>

<div class="container">
	<div class="header">
		<h1>Form Templates</h1>
		<a href="/admin/forms/builder" class="create-btn">Create New Form</a>
	</div>

	{#if loading}
		<div class="loading">Loading forms...</div>
	{:else if error}
		<div class="error">Error: {error}</div>
	{:else if forms.length === 0}
		<div class="empty-state">
			<h3>No Form Templates Yet</h3>
			<p>Create your first form template to get started with dynamic access requests.</p>
		</div>
	{:else}
		<div class="forms-grid">
			{#each forms as form}
				<div class="form-card">
					<div class="form-title">{form.name}</div>
					{#if form.description}
						<div class="form-description">{form.description}</div>
					{/if}
					<div class="form-meta">
						<div>ID: {form.id}</div>
						<div>Created by Admin ID: {form.created_by_admin_id}</div>
					</div>
					<div class="form-actions">
						<a href="/admin/forms/{form.id}" class="view-btn">View Details</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
