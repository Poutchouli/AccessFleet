<script>
	import { onMount } from 'svelte';

	let formTemplates = [];
	let selectedForm = null;
	let formData = {};
	let loading = true;
	let submitting = false;
	let error = null;

	onMount(async () => {
		try {
			const response = await fetch('http://localhost:8000/form-definitions');
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
				formData[element.name] = '';
			});
		} else if (form.schema && form.schema.pages) {
			form.schema.pages.forEach(page => {
				if (page.elements) {
					page.elements.forEach(element => {
						formData[element.name] = '';
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
			const response = await fetch('http://localhost:8000/requests/', {
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

			alert('Request submitted successfully!');
			window.location.href = '/requests';
		} catch (err) {
			error = err.message;
		} finally {
			submitting = false;
		}
	}

	function renderFormField(element) {
		const commonProps = {
			required: element.isRequired,
			disabled: submitting
		};

		switch (element.type) {
			case 'text':
				return { type: 'text', ...commonProps };
			case 'email':
				return { type: 'email', ...commonProps };
			case 'number':
				return { type: 'number', ...commonProps };
			case 'dropdown':
				return { type: 'select', options: element.choices || [], ...commonProps };
			case 'radiogroup':
				return { type: 'radio', options: element.choices || [], ...commonProps };
			case 'checkbox':
				return { type: 'checkbox', ...commonProps };
			case 'boolean':
				return { type: 'checkbox', ...commonProps };
			case 'comment':
			case 'textarea':
				return { type: 'textarea', ...commonProps };
			default:
				return { type: 'text', ...commonProps };
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
						{@const fieldProps = renderFormField(element)}
						<div class="field-group">
							<label for={element.name}>
								{element.title}
								{#if element.isRequired}<span class="required">*</span>{/if}
							</label>
							
							{#if fieldProps.type === 'select'}
								<select 
									id={element.name} 
									bind:value={formData[element.name]} 
									required={fieldProps.required}
									disabled={fieldProps.disabled}
								>
									<option value="">Please select...</option>
									{#each fieldProps.options as option}
										<option value={option}>{option}</option>
									{/each}
								</select>
							{:else if fieldProps.type === 'radio'}
								<div class="radio-group">
									{#each fieldProps.options as option}
										<label class="radio-label">
											<input 
												type="radio" 
												name={element.name}
												value={option}
												bind:group={formData[element.name]}
												required={fieldProps.required}
												disabled={fieldProps.disabled}
											/>
											{option}
										</label>
									{/each}
								</div>
							{:else if fieldProps.type === 'checkbox'}
								<label class="checkbox-label">
									<input 
										type="checkbox" 
										id={element.name}
										bind:checked={formData[element.name]}
										disabled={fieldProps.disabled}
									/>
									{element.title}
								</label>
							{:else if fieldProps.type === 'textarea'}
								<textarea 
									id={element.name}
									bind:value={formData[element.name]}
									required={fieldProps.required}
									disabled={fieldProps.disabled}
									rows="4"
								></textarea>
							{:else}
								<input 
									type={fieldProps.type}
									id={element.name}
									bind:value={formData[element.name]}
									required={fieldProps.required}
									disabled={fieldProps.disabled}
								/>
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
	}

	.radio-label, .checkbox-label {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: normal;
		cursor: pointer;
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
