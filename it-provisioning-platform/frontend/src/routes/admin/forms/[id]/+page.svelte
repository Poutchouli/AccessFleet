<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	
	let form = null;
	let loading = true;
	let error = null;
	
	$: formId = $page.params.id;

	onMount(async () => {
		try {
			const response = await fetch(`/api/form-definitions/${formId}`);
			if (!response.ok) {
				throw new Error('Failed to load form');
			}
			form = await response.json();
		} catch (err) {
			console.error('Error loading form:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	});

	function renderPreview(schema) {
		if (!schema || !schema.elements) return 'No form elements defined';
		
		return schema.elements.map(element => {
			switch (element.type) {
				case 'text':
				case 'email':
				case 'number':
					return `${element.title}${element.isRequired ? ' *' : ''} (${element.type})`;
				case 'textarea':
					return `${element.title}${element.isRequired ? ' *' : ''} (multi-line text)`;
				case 'dropdown':
					const choices = element.choices ? element.choices.join(', ') : 'No options';
					return `${element.title}${element.isRequired ? ' *' : ''} (dropdown: ${choices})`;
				case 'checkbox':
					return `${element.title}${element.isRequired ? ' *' : ''} (checkbox)`;
				default:
					return `${element.title}${element.isRequired ? ' *' : ''} (${element.type})`;
			}
		}).join('\n');
	}
</script>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
	}

	.back-link {
		color: #666;
		text-decoration: none;
	}

	.back-link:hover {
		color: #333;
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

	.form-details {
		background: white;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 20px;
		margin-bottom: 20px;
	}

	.form-title {
		font-size: 1.8em;
		font-weight: bold;
		margin-bottom: 10px;
		color: #333;
	}

	.form-description {
		color: #666;
		margin-bottom: 20px;
		font-size: 1.1em;
	}

	.form-meta {
		background: #f5f5f5;
		padding: 15px;
		border-radius: 5px;
		margin-bottom: 20px;
	}

	.meta-item {
		margin-bottom: 8px;
	}

	.meta-label {
		font-weight: bold;
		color: #555;
	}

	.schema-preview {
		background: white;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 20px;
	}

	.schema-title {
		font-size: 1.2em;
		font-weight: bold;
		margin-bottom: 15px;
		color: #333;
	}

	.form-elements {
		white-space: pre-line;
		font-family: monospace;
		background: #f9f9f9;
		padding: 15px;
		border-radius: 5px;
		border: 1px solid #e0e0e0;
	}

	.json-view {
		background: #f5f5f5;
		padding: 15px;
		border-radius: 5px;
		font-family: monospace;
		font-size: 0.9em;
		white-space: pre-wrap;
		overflow-x: auto;
		max-height: 400px;
		overflow-y: auto;
	}
</style>

<div class="container">
	<div class="header">
		<h1>Form Template Details</h1>
		<a href="/admin/forms" class="back-link">← Back to Forms</a>
	</div>

	{#if loading}
		<div class="loading">Loading form details...</div>
	{:else if error}
		<div class="error">Error: {error}</div>
	{:else if form}
		<div class="form-details">
			<div class="form-title">{form.name}</div>
			{#if form.description}
				<div class="form-description">{form.description}</div>
			{/if}
			
			<div class="form-meta">
				<div class="meta-item">
					<span class="meta-label">Form ID:</span> {form.id}
				</div>
				<div class="meta-item">
					<span class="meta-label">Created by Admin ID:</span> {form.created_by_admin_id}
				</div>
			</div>
		</div>

		<div class="schema-preview">
			<div class="schema-title">Form Elements Preview</div>
			<div class="form-elements">
				{renderPreview(form.schema)}
			</div>
			
			<details style="margin-top: 20px;">
				<summary style="cursor: pointer; font-weight: bold;">View Raw JSON Schema</summary>
				<div class="json-view">
					{JSON.stringify(form.schema, null, 2)}
				</div>
			</details>
		</div>
	{/if}
</div>
