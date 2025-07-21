<script>
	import { onMount } from 'svelte';

	let formName = '';
	let formDescription = '';
	let selectedWalkthroughId = null;
	let walkthroughTemplates = [];
	let elements = [
		{
			type: 'text',
			name: 'example',
			title: 'Example Field',
			isRequired: false
		}
	];
	
	let saving = false;
	let saveSuccess = false;
	let saveError = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/admin/walkthrough-templates');
			walkthroughTemplates = await response.json();
		} catch (error) {
			console.error('Failed to load walkthrough templates:', error);
		}
	});

	function addElement() {
		elements = [...elements, {
			type: 'text',
			name: `field_${Date.now()}`,
			title: 'New Field',
			isRequired: false
		}];
	}

	function removeElement(index) {
		elements = elements.filter((_, i) => i !== index);
	}

	async function saveForm() {
		if (!formName.trim()) {
			alert('Please enter a form name');
			return;
		}

		saving = true;
		saveError = null;
		saveSuccess = false;

		try {
			const formSchema = {
				title: formName,
				description: formDescription,
				elements: elements.map(el => ({
					type: el.type,
					name: el.name,
					title: el.title,
					isRequired: el.isRequired,
					...(el.choices ? { choices: el.choices.split(',').map(c => c.trim()) } : {})
				}))
			};

			const response = await fetch('/api/form-definitions/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: formName,
					description: formDescription,
					schema: formSchema,
					suggested_walkthrough_id: selectedWalkthroughId
				})
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to save the form');
			}

			saveSuccess = true;
			// Redirect to forms list after a brief delay
			setTimeout(() => {
				window.location.href = '/admin/forms';
			}, 2000);
		} catch (error) {
			console.error('Save error:', error);
			saveError = error.message;
		} finally {
			saving = false;
		}
	}
</script>

<style>
	.container {
		max-width: 1000px;
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

	.form-section {
		background: white;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 20px;
		margin-bottom: 20px;
	}

	.form-group {
		margin-bottom: 15px;
	}

	.form-group label {
		display: block;
		margin-bottom: 5px;
		font-weight: bold;
		color: #333;
	}

	.form-group input,
	.form-group textarea,
	.form-group select {
		width: 100%;
		padding: 8px 12px;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 14px;
	}

	.form-group textarea {
		resize: vertical;
		min-height: 60px;
	}

	.help-text {
		display: block;
		margin-top: 5px;
		font-size: 12px;
		color: #666;
		font-style: italic;
	}

	.element-item {
		border: 1px solid #e0e0e0;
		border-radius: 6px;
		padding: 15px;
		margin-bottom: 10px;
		background: #f9f9f9;
	}

	.element-header {
		display: flex;
		justify-content: between;
		align-items: center;
		margin-bottom: 10px;
	}

	.element-title {
		font-weight: bold;
		color: #333;
		flex: 1;
	}

	.remove-btn {
		background: #f44336;
		color: white;
		border: none;
		padding: 5px 10px;
		border-radius: 4px;
		cursor: pointer;
		font-size: 12px;
	}

	.remove-btn:hover {
		background: #d32f2f;
	}

	.add-btn {
		background: #4CAF50;
		color: white;
		border: none;
		padding: 10px 20px;
		border-radius: 5px;
		cursor: pointer;
		font-weight: bold;
		margin-bottom: 20px;
	}

	.add-btn:hover {
		background: #45a049;
	}

	.save-btn {
		background: #2196F3;
		color: white;
		border: none;
		padding: 12px 30px;
		border-radius: 5px;
		cursor: pointer;
		font-weight: bold;
		font-size: 16px;
	}

	.save-btn:hover {
		background: #1976D2;
	}

	.save-btn:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.element-row {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr auto;
		gap: 10px;
		align-items: end;
	}

	.checkbox-group {
		display: flex;
		align-items: center;
		gap: 5px;
	}

	.success-message {
		background: #e8f5e8;
		color: #2e7d32;
		padding: 15px;
		border-radius: 5px;
		margin-bottom: 20px;
	}

	.error-message {
		background: #ffebee;
		color: #c62828;
		padding: 15px;
		border-radius: 5px;
		margin-bottom: 20px;
	}
</style>

<div class="container">
	<div class="header">
		<h1>Form Builder</h1>
		<a href="/admin/forms" class="back-link">← Back to Forms</a>
	</div>

	{#if saveSuccess}
		<div class="success-message">
			Form template saved successfully! Redirecting to forms list...
		</div>
	{/if}

	{#if saveError}
		<div class="error-message">
			Error: {saveError}
		</div>
	{/if}

	<div class="form-section">
		<h3>Form Information</h3>
		<div class="form-group">
			<label for="form-name">Form Name</label>
			<input id="form-name" type="text" bind:value={formName} placeholder="e.g., Server Access Request">
		</div>
		<div class="form-group">
			<label for="form-description">Description</label>
			<textarea id="form-description" bind:value={formDescription} placeholder="Brief description of this form"></textarea>
		</div>
		<div class="form-group">
			<label for="walkthrough-select">Suggested Walkthrough (Optional)</label>
			<select id="walkthrough-select" bind:value={selectedWalkthroughId}>
				<option value={null}>-- None --</option>
				{#each walkthroughTemplates as template}
					<option value={template.id}>{template.name}</option>
				{/each}
			</select>
			<small class="help-text">Select a walkthrough that administrators should follow when processing requests from this form</small>
		</div>
	</div>

	<div class="form-section">
		<h3>Form Elements</h3>
		
		{#each elements as element, index}
			<div class="element-item">
				<div class="element-header">
					<div class="element-title">Field {index + 1}</div>
					<button class="remove-btn" on:click={() => removeElement(index)}>Remove</button>
				</div>
				<div class="element-row">
					<div class="form-group">
						<label>Field Type</label>
						<select bind:value={element.type}>
							<option value="text">Text</option>
							<option value="email">Email</option>
							<option value="number">Number</option>
							<option value="textarea">Textarea</option>
							<option value="dropdown">Dropdown</option>
							<option value="checkbox">Checkbox</option>
						</select>
					</div>
					<div class="form-group">
						<label>Field Name</label>
						<input type="text" bind:value={element.name} placeholder="field_name">
					</div>
					<div class="form-group">
						<label>Field Title</label>
						<input type="text" bind:value={element.title} placeholder="Display Title">
					</div>
					<div class="form-group">
						<div class="checkbox-group">
							<input type="checkbox" bind:checked={element.isRequired} id="required-{index}">
							<label for="required-{index}">Required</label>
						</div>
					</div>
				</div>
				{#if element.type === 'dropdown'}
					<div class="form-group">
						<label>Choices (comma separated)</label>
						<input type="text" bind:value={element.choices} placeholder="option1, option2, option3">
					</div>
				{/if}
			</div>
		{/each}

		<button class="add-btn" on:click={addElement}>+ Add Field</button>
	</div>

	<button class="save-btn" on:click={saveForm} disabled={saving}>
		{saving ? 'Saving...' : 'Save Form Template'}
	</button>
</div>
