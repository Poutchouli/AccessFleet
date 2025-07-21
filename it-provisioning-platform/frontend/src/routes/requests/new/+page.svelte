<script>
	import { onMount } from 'svelte';
	import { invalidateAll } from '$app/navigation'; // Import invalidateAll for data refresh
	import { goto } from '$app/navigation'; // Import goto for SvelteKit navigation

	let formTemplates = [];
	let selectedForm = null;
	let formData = {};
	let loading = true;
	let submitting = false;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/form-definitions');
			if (!response.ok) {
				throw new Error('Failed to fetch form templates');
			}
			formTemplates = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	});

	function selectForm(form) {
		selectedForm = form;
		formData = {};
		// Initialize form data based on form schema
		if (form.schema && form.schema.elements) {
			form.schema.elements.forEach(element => {
				if (element.type === 'checkbox' && element.choices) {
					formData[element.name] = [];
				} else if (element.type === 'boolean') {
					formData[element.name] = false;
				} else {
					formData[element.name] = '';
				}
			});
		} else if (form.schema && form.schema.pages) {
			form.schema.pages.forEach(page => {
				if (page.elements) {
					page.elements.forEach(element => {
						if (element.type === 'checkbox' && element.choices) {
							formData[element.name] = [];
						} else if (element.type === 'boolean') {
							formData[element.name] = false;
						} else {
							formData[element.name] = '';
						}
					});
				}
			});
		}
	}

	function goBack() {
		selectedForm = null;
		formData = {};
	}

	async function handleFormSubmit() {
		if (!selectedForm) return;
		
		submitting = true;
		try {
			const response = await fetch('/api/requests/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					form_definition_id: selectedForm.id,
					form_data: formData
				})
			});

			if (!response.ok) {
				throw new Error('Failed to submit request');
			}

			// Invalidate all data before navigating to ensure fresh data load
			await invalidateAll();
			
			// Navigate back to requests page using SvelteKit's goto
			await goto('/requests');
			
			alert('Request submitted successfully!');
		} catch (err) {
			error = err.message;
		} finally {
			submitting = false;
		}
	}

	function getFormElements(form) {
		if (!form || !form.schema) return [];
		
		if (form.schema.elements) {
			return form.schema.elements;
		} else if (form.schema.pages) {
			let allElements = [];
			form.schema.pages.forEach(page => {
				if (page.elements) {
					allElements = [...allElements, ...page.elements];
				}
			});
			return allElements;
		}
		return [];
	}
</script>

<div class="container">
	<h2>Submit a New Request</h2>

	{#if loading}
		<p>Loading form templates...</p>
	{:else if error}
		<p class="error">Error: {error}</p>
	{:else if !selectedForm}
		<div class="step">
			<h3>Step 1: Choose a Template</h3>
			<div class="form-grid">
				{#each formTemplates as form}
					<div class="form-card">
						<h4>{form.name}</h4>
						<p>{form.description || 'No description available'}</p>
						<button class="btn btn-primary" on:click={() => selectForm(form)}>
							Select Template
						</button>
					</div>
				{/each}
			</div>
		</div>
	{:else}
		<div class="step">
			<div class="step-header">
				<button class="btn btn-secondary" on:click={goBack}>← Back to Templates</button>
				<h3>Step 2: Fill Out "{selectedForm.name}"</h3>
			</div>
			
			<form on:submit|preventDefault={handleFormSubmit}>
				<div class="form-fields">
					{#each getFormElements(selectedForm) as element}
						<div class="field-group">
							<label for={element.name}>
								{element.title || element.name}
								{#if element.isRequired}<span class="required">*</span>{/if}
							</label>
							
							{#if element.type === 'text' || element.type === 'comment'}
								<input
									type="text"
									id={element.name}
									bind:value={formData[element.name]}
									placeholder={element.placeholder || ''}
									required={element.isRequired}
									disabled={submitting}
								/>
							{:else if element.type === 'email'}
								<input
									type="email"
									id={element.name}
									bind:value={formData[element.name]}
									placeholder={element.placeholder || ''}
									required={element.isRequired}
									disabled={submitting}
								/>
							{:else if element.type === 'number'}
								<input
									type="number"
									id={element.name}
									bind:value={formData[element.name]}
									placeholder={element.placeholder || ''}
									required={element.isRequired}
									disabled={submitting}
								/>
							{:else if element.type === 'textarea'}
								<textarea 
									id={element.name}
									bind:value={formData[element.name]}
									placeholder={element.placeholder || ''}
									required={element.isRequired}
									disabled={submitting}
									rows="4"
								></textarea>
							{:else if element.type === 'dropdown'}
								<select 
									id={element.name} 
									bind:value={formData[element.name]} 
									required={element.isRequired}
									disabled={submitting}
								>
									<option value="">Please select...</option>
									{#each element.choices || [] as choice}
										<option value={choice.value || choice}>{choice.text || choice}</option>
									{/each}
								</select>
							{:else if element.type === 'radiogroup'}
								<div class="radio-group">
									{#each element.choices || [] as choice}
										<label class="radio-label">
											<input 
												type="radio" 
												name={element.name}
												value={choice.value || choice}
												bind:group={formData[element.name]}
												required={element.isRequired}
												disabled={submitting}
											/>
											{choice.text || choice}
										</label>
									{/each}
								</div>
							{:else if element.type === 'checkbox'}
								<div>
									{#each element.choices || [] as choice}
										<label class="checkbox-label">
											<input
												type="checkbox"
												value={choice.value || choice}
												bind:group={formData[element.name]}
												disabled={submitting}
											/>
											{choice.text || choice}
										</label>
									{/each}
								</div>
							{:else if element.type === 'boolean'}
								<label class="checkbox-label">
									<input 
										type="checkbox" 
										id={element.name}
										bind:checked={formData[element.name]}
										disabled={submitting}
									/>
									{element.title || element.name}
								</label>
							{:else}
								<p>Unsupported field type: {element.type}</p>
							{/if}
						</div>
					{/each}
				</div>

				<div class="form-actions">
					<button 
						type="submit" 
						class="btn btn-primary" 
						disabled={submitting}
					>
						{submitting ? 'Submitting...' : 'Submit Request'}
					</button>
				</div>
			</form>
		</div>
	{/if}
</div>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
	}

	.step {
		background: white;
		padding: 20px;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.step-header {
		display: flex;
		align-items: center;
		gap: 20px;
		margin-bottom: 20px;
	}

	.form-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 20px;
		margin-top: 20px;
	}

	.form-card {
		padding: 20px;
		border: 1px solid #ddd;
		border-radius: 8px;
		background: #f8f9fa;
	}

	.form-card h4 {
		margin: 0 0 10px 0;
		color: #333;
	}

	.form-card p {
		margin: 0 0 15px 0;
		color: #666;
		font-size: 0.9em;
	}

	.btn {
		display: inline-block;
		padding: 10px 20px;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		text-decoration: none;
		font-size: 14px;
		font-weight: 500;
		transition: background-color 0.2s;
	}

	.btn-primary {
		background-color: #007bff;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #0056b3;
	}

	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background-color: #545b62;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.form-fields {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.field-group {
		display: flex;
		flex-direction: column;
		gap: 5px;
		margin-bottom: 1rem;
	}

	label {
		font-weight: 500;
		color: #333;
	}

	.required {
		color: #d63031;
	}

	input, select, textarea {
		padding: 10px;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 14px;
	}

	input:focus, select:focus, textarea:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
	}

	.radio-group {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-top: 5px;
	}

	.radio-label, .checkbox-label {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: normal;
		cursor: pointer;
		margin-bottom: 5px;
	}

	.form-actions {
		margin-top: 30px;
		padding-top: 20px;
		border-top: 1px solid #ddd;
	}

	.error {
		color: #d63031;
		background-color: #ffeaa7;
		padding: 10px;
		border-radius: 4px;
		margin-bottom: 20px;
	}
</style>
