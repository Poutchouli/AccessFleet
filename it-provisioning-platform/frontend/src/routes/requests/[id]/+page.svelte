<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { commandQueue } from '$lib/stores/commandQueue.js';

	let request = null;
	let templates = [];
	let selectedTemplateId = null;
	let checklistState = {};
	let availableTempAccounts = [];
	let allAccounts = [];
	let selectedTempAccountId = null;

	const requestId = $page.params.id;

	onMount(async () => {
		// Fetch request data first to get form_definition_id
		const reqRes = await fetch(`/api/requests/${requestId}`);
		request = await reqRes.json();

		// Fetch all necessary data in parallel
		const [tplRes, accRes, formDefRes] = await Promise.all([
			fetch('/api/admin/walkthrough-templates'),
			fetch('/api/admin/temp-accounts'),
			fetch(`/api/form-definitions/${request.form_definition_id}`)
		]);
		
		templates = await tplRes.json();
		allAccounts = await accRes.json();
		const formDef = await formDefRes.json();
		availableTempAccounts = allAccounts.filter(acc => !acc.is_in_use);

		// Set the suggested walkthrough by default
		if (formDef.suggested_walkthrough_id) {
			selectedTemplateId = formDef.suggested_walkthrough_id;
		}

		// Load saved checklist state if it exists, potentially overriding the suggestion
		if (request.walkthrough_state) {
			checklistState = request.walkthrough_state;
			// Find which template was saved
			selectedTemplateId = templates.find(t => t.id === checklistState.templateId)?.id || selectedTemplateId;
		}
	});

	// A "computed property" to get the selected template object
	$: selectedTemplate = templates.find(t => t.id === selectedTemplateId);

	// Computed property to get assigned account details
	$: assignedAccount = request?.assigned_temp_account_id 
		? allAccounts.find(a => a.id === request.assigned_temp_account_id) 
		: null;

	function handleTemplateSelect(event) {
		selectedTemplateId = parseInt(event.target.value);
		// Initialize state for the selected template
		const newChecklistState = {
			templateId: selectedTemplateId,
			completedSteps: []
		};
		updateChecklistState(newChecklistState);
	}

	function handleStepToggle(stepIndex) {
		const completed = checklistState.completedSteps.includes(stepIndex);
		if (completed) {
			checklistState.completedSteps = checklistState.completedSteps.filter(i => i !== stepIndex);
		} else {
			checklistState.completedSteps.push(stepIndex);
		}
		updateChecklistState(checklistState);
	}

	async function updateChecklistState(newState) {
		checklistState = newState; // Update local state immediately for responsiveness
		await fetch(`/api/requests/${requestId}/walkthrough-state`, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ state: checklistState })
		});
	}

	async function assignAccount() {
		if (!selectedTempAccountId) {
			alert('Please select an account to assign.');
			return;
		}
		try {
			const response = await fetch(`/api/requests/${requestId}/assign-temp-account`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ temp_account_id: selectedTempAccountId })
			});
			if (!response.ok) throw new Error('Failed to assign account.');

			// Update the UI
			request = await response.json();
			
			const assignedAccount = availableTempAccounts.find(a => a.id === selectedTempAccountId);
			
			// Generate and queue the PowerShell command
			const command = `Set-ADUser -Identity '${assignedAccount.user_principal_name}' -Enabled $false -Description 'In use for Request #${requestId}'`;
			commandQueue.update(q => [...q, command]);

			// Refresh available accounts list
			const updatedAccounts = await (await fetch('/api/admin/temp-accounts')).json();
			allAccounts = updatedAccounts;
			availableTempAccounts = updatedAccounts.filter(acc => !acc.is_in_use);

			alert('Account assigned successfully!');
			selectedTempAccountId = null;

		} catch (error) {
			alert(`Error: ${error.message}`);
		}
	}
</script>

{#if !request}
	<p>Loading request...</p>
{:else}
	<div class="page-header">
		<a href="/requests" class="back-link">← Back to Requests</a>
		<h2>Request Details (ID: {request.id})</h2>
	</div>
	
	<div class="container">
		<div class="details-pane">
			<h4>Request Information</h4>
			<div class="info-grid">
				<div class="info-item">
					<strong>Status:</strong>
					<span class="status status-{request.status}">{request.status}</span>
				</div>
				<div class="info-item">
					<strong>Submitted By:</strong> User ID {request.submitted_by_manager_id}
				</div>
				<div class="info-item">
					<strong>Form ID:</strong> {request.form_definition_id}
				</div>
			</div>

			<h4>Submitted Data</h4>
			<div class="form-data-grid">
				{#each Object.entries(request.form_data) as [key, value]}
					<div class="data-item">
						<strong>{key}:</strong>
						<span>{value}</span>
					</div>
				{/each}
			</div>

			<h4>TEMP Account Assignment</h4>
			<div class="temp-account-section">
				{#if request.assigned_temp_account_id}
					<div class="assigned-account">
						<div class="account-info">
							<strong>Account Assigned:</strong>
							{#if assignedAccount}
								<div class="account-details">
									<div><strong>Display Name:</strong> {assignedAccount.display_name}</div>
									<div><strong>UPN:</strong> {assignedAccount.user_principal_name}</div>
									<div class="status-badge assigned">✓ Assigned</div>
								</div>
							{:else}
								<span class="account-id">ID: {request.assigned_temp_account_id}</span>
							{/if}
						</div>
					</div>
				{:else}
					<div class="assignment-controls">
						<label for="account-select">Select Available TEMP Account:</label>
						<div class="assignment-row">
							<select id="account-select" bind:value={selectedTempAccountId}>
								<option value={null}>-- Select available account --</option>
								{#each availableTempAccounts as acc}
									<option value={acc.id}>{acc.display_name} ({acc.user_principal_name})</option>
								{/each}
							</select>
							<button 
								class="assign-btn" 
								on:click={assignAccount} 
								disabled={!selectedTempAccountId}
							>
								Assign Account
							</button>
						</div>
						{#if availableTempAccounts.length === 0}
							<p class="no-accounts">No available TEMP accounts found.</p>
						{/if}
					</div>
				{/if}
			</div>
		</div>

		<div class="walkthrough-pane">
			<h4>Admin Walkthrough</h4>
			<div class="template-selector">
				<label for="template-select">Select Walkthrough Template:</label>
				<select id="template-select" on:change={handleTemplateSelect} value={selectedTemplateId}>
					<option disabled selected={!selectedTemplateId} value={null}>-- Select a walkthrough --</option>
					{#each templates as template}
						<option value={template.id}>{template.name}</option>
					{/each}
				</select>
			</div>

			{#if selectedTemplate}
				<div class="template-info">
					<h5>{selectedTemplate.name}</h5>
					<p>{selectedTemplate.description}</p>
				</div>
				
				<div class="checklist">
					<h6>Checklist Steps:</h6>
					<ul class="steps-list">
						{#each selectedTemplate.steps as step, i}
							<li class="step-item">
								<label class="step-label">
									<input
										type="checkbox"
										checked={checklistState?.completedSteps?.includes(i) || false}
										on:change={() => handleStepToggle(i)}
									/>
									<span class="step-content">
										<span class="step-type">[{step.type}]</span>
										<span class="step-text">{step.content}</span>
									</span>
								</label>
							</li>
						{/each}
					</ul>
					
					{#if checklistState?.completedSteps}
						<div class="progress">
							Progress: {checklistState.completedSteps.length} of {selectedTemplate.steps.length} steps completed
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.page-header {
		margin-bottom: 2rem;
	}

	.back-link {
		display: inline-block;
		color: #007bff;
		text-decoration: none;
		margin-bottom: 1rem;
		font-weight: 500;
	}

	.back-link:hover {
		text-decoration: underline;
	}

	.container {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		max-width: 1200px;
		margin: 0 auto;
	}

	.details-pane,
	.walkthrough-pane {
		background: white;
		border-radius: 8px;
		padding: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.info-grid {
		display: grid;
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.info-item {
		padding: 0.75rem;
		background: #f8f9fa;
		border-radius: 4px;
	}

	.status {
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.875rem;
		font-weight: 500;
		text-transform: uppercase;
	}

	.status-pending {
		background-color: #fff3cd;
		color: #856404;
	}

	.status-in_progress {
		background-color: #cce5ff;
		color: #004085;
	}

	.status-completed {
		background-color: #d4edda;
		color: #155724;
	}

	.status-rejected {
		background-color: #f8d7da;
		color: #721c24;
	}

	.form-data-grid {
		display: grid;
		gap: 0.75rem;
	}

	.data-item {
		padding: 0.75rem;
		background: #f8f9fa;
		border-radius: 4px;
		border-left: 3px solid #007bff;
	}

	.template-selector {
		margin-bottom: 1.5rem;
	}

	.template-selector label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
	}

	.template-selector select {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	.template-info {
		margin-bottom: 1.5rem;
		padding: 1rem;
		background: #e7f3ff;
		border-radius: 4px;
		border-left: 3px solid #007bff;
	}

	.template-info h5 {
		margin: 0 0 0.5rem 0;
		color: #007bff;
	}

	.template-info p {
		margin: 0;
		color: #666;
	}

	.checklist h6 {
		margin-bottom: 1rem;
		color: #333;
	}

	.steps-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.step-item {
		margin-bottom: 0.75rem;
	}

	.step-label {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		cursor: pointer;
		padding: 0.75rem;
		border-radius: 4px;
		transition: background-color 0.2s;
	}

	.step-label:hover {
		background-color: #f8f9fa;
	}

	.step-label input[type="checkbox"] {
		margin-top: 0.25rem;
		width: 1.1rem;
		height: 1.1rem;
	}

	.step-content {
		flex: 1;
	}

	.step-type {
		display: inline-block;
		background: #007bff;
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 3px;
		font-size: 0.75rem;
		font-weight: 500;
		margin-right: 0.75rem;
		text-transform: uppercase;
	}

	.step-text {
		font-size: 0.95rem;
		line-height: 1.4;
	}

	.progress {
		margin-top: 1.5rem;
		padding: 1rem;
		background: #d4edda;
		border-radius: 4px;
		text-align: center;
		font-weight: 500;
		color: #155724;
	}

	/* TEMP Account Assignment Styles */
	.temp-account-section {
		margin-top: 1.5rem;
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 4px;
		border-left: 3px solid #28a745;
	}

	.assigned-account {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.account-details {
		margin-top: 0.5rem;
		padding: 0.75rem;
		background: white;
		border-radius: 4px;
		border: 1px solid #dee2e6;
	}

	.account-details div {
		margin-bottom: 0.5rem;
	}

	.account-details div:last-child {
		margin-bottom: 0;
	}

	.status-badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.status-badge.assigned {
		background-color: #d4edda;
		color: #155724;
	}

	.assignment-controls label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
	}

	.assignment-row {
		display: flex;
		gap: 0.75rem;
		align-items: center;
	}

	.assignment-row select {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	.assign-btn {
		padding: 0.75rem 1.5rem;
		background: #28a745;
		color: white;
		border: none;
		border-radius: 4px;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.assign-btn:hover:not(:disabled) {
		background: #218838;
	}

	.assign-btn:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.no-accounts {
		margin-top: 0.75rem;
		color: #856404;
		font-style: italic;
	}

	.account-id {
		font-family: monospace;
		background: #e9ecef;
		padding: 0.25rem 0.5rem;
		border-radius: 3px;
	}

	@media (max-width: 768px) {
		.container {
			grid-template-columns: 1fr;
			gap: 1rem;
		}

		.assignment-row {
			flex-direction: column;
			align-items: stretch;
		}

		.assign-btn {
			margin-top: 0.5rem;
		}
	}
</style>
