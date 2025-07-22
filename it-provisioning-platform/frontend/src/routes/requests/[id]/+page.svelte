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
		// Fetch request data first to get form_definition
		const reqRes = await fetch(`/api/requests/${requestId}`);
		request = await reqRes.json();

		// Fetch all necessary data in parallel
		const [tplRes, accRes] = await Promise.all([
			fetch('/api/admin/walkthrough-templates'),
			fetch('/api/admin/temp-accounts')
		]);
		
		templates = await tplRes.json();
		allAccounts = await accRes.json();
		availableTempAccounts = allAccounts.filter(acc => !acc.is_in_use);

		// Set the suggested walkthrough by default from the form definition
		if (request.form_definition?.suggested_walkthrough_id) {
			selectedTemplateId = request.form_definition.suggested_walkthrough_id;
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
	$: assignedAccount = request?.assigned_temp_account || null;

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

	async function approveMailboxRequest(modification) {
		try {
			const response = await fetch('/api/admin/generate-mailbox-commands', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(modification)
			});
			
			if (!response.ok) {
				throw new Error('Failed to generate mailbox commands');
			}
			
			const result = await response.json();
			
			// Add all commands to the queue
			commandQueue.update(q => [...q, ...result.commands]);
			
			alert(`✅ ${result.total_commands} mailbox command${result.total_commands === 1 ? '' : 's'} added to queue for ${result.mailbox_name}!`);
		} catch (error) {
			alert(`❌ Error: ${error.message}`);
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
					<strong>Submitted By:</strong>
					{#if request.submitted_by}
						<div class="user-info">
							<div class="user-name">{request.submitted_by.full_name}</div>
							<div class="user-details">{request.submitted_by.email}</div>
							{#if request.submitted_by.service}
								<div class="user-service">📍 {request.submitted_by.service}</div>
							{/if}
						</div>
					{:else}
						<span class="unknown">Unknown User</span>
					{/if}
				</div>
				<div class="info-item">
					<strong>Using Form:</strong>
					{#if request.form_definition}
						<div class="form-info">
							<div class="form-name">{request.form_definition.name}</div>
							{#if request.form_definition.description}
								<div class="form-description">{request.form_definition.description}</div>
							{/if}
						</div>
					{:else}
						<span class="unknown">Unknown Form</span>
					{/if}
				</div>
			</div>

			<h4>Submitted Data</h4>
			{#if request.form_data.type === 'mailbox_modifications'}
				<div class="mailbox-modifications">
					<h5>📧 SharedMailbox Request</h5>
					{#each request.form_data.modifications.modifications as mod}
						<div class="modification-card">
							<div class="mailbox-header">
								<h6>📮 {mod.mailbox_name}</h6>
							</div>
							
							<div class="modification-content">
								{#if mod.add_users.length > 0}
									<div class="user-changes add-users">
										<strong>➕ Add Users:</strong>
										<ul>
											{#each mod.add_users as user}
												<li class="user-item add">{user}</li>
											{/each}
										</ul>
									</div>
								{/if}
								
								{#if mod.remove_users.length > 0}
									<div class="user-changes remove-users">
										<strong>➖ Remove Users:</strong>
										<ul>
											{#each mod.remove_users as user}
												<li class="user-item remove">{user}</li>
											{/each}
										</ul>
									</div>
								{/if}
							</div>
							
							<div class="modification-actions">
								<button 
									class="approve-btn" 
									on:click={() => approveMailboxRequest(mod)}
								>
									🚀 Queue PowerShell Commands
								</button>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="form-data-grid">
					{#each Object.entries(request.form_data) as [key, value]}
						<div class="data-item">
							<strong>{key}:</strong>
							<span>{value}</span>
						</div>
					{/each}
				</div>
			{/if}

			{#if selectedTemplate?.tools?.includes('temp_account_assignment')}
				<h4>TEMP Account Assignment</h4>
				<div class="temp-account-section">
					{#if request.assigned_temp_account}
						<div class="assigned-account">
							<div class="account-info">
								<strong>Account Assigned:</strong>
								<div class="account-details">
									<div><strong>Display Name:</strong> {assignedAccount.display_name}</div>
									<div><strong>UPN:</strong> {assignedAccount.user_principal_name}</div>
									<div class="status-badge assigned">✓ Assigned</div>
								</div>
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
			{/if}
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

	.user-info, .form-info {
		margin-top: 0.5rem;
	}

	.user-name, .form-name {
		font-weight: 600;
		color: #2d3436;
		margin-bottom: 0.25rem;
	}

	.user-details, .user-service, .form-description {
		font-size: 0.9em;
		color: #636e72;
		margin-bottom: 0.25rem;
	}

	.user-service {
		font-style: italic;
	}

	.unknown {
		color: #e74c3c;
		font-style: italic;
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

	/* Mailbox Modification Styles */
	.mailbox-modifications {
		margin-top: 1rem;
	}

	.mailbox-modifications h5 {
		color: #0984e3;
		margin-bottom: 1rem;
		font-size: 1.2rem;
	}

	.modification-card {
		border: 1px solid #e1e8ed;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 1rem;
		background: white;
		box-shadow: 0 2px 4px rgba(0,0,0,0.05);
	}

	.mailbox-header h6 {
		margin: 0 0 1rem 0;
		color: #2d3436;
		font-size: 1.1rem;
		padding-bottom: 0.5rem;
		border-bottom: 2px solid #e1e8ed;
	}

	.modification-content {
		margin: 1rem 0;
	}

	.user-changes {
		margin-bottom: 1rem;
	}

	.user-changes strong {
		display: block;
		margin-bottom: 0.5rem;
		color: #2d3436;
	}

	.user-changes ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.user-item {
		padding: 0.5rem 0.75rem;
		margin-bottom: 0.25rem;
		border-radius: 6px;
		font-weight: 500;
	}

	.user-item.add {
		background: #d1fae5;
		color: #065f46;
		border-left: 4px solid #10b981;
	}

	.user-item.remove {
		background: #fee2e2;
		color: #991b1b;
		border-left: 4px solid #ef4444;
	}

	.modification-actions {
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid #e1e8ed;
	}

	.approve-btn {
		background: #0984e3;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: background-color 0.2s;
		font-size: 0.95rem;
	}

	.approve-btn:hover {
		background: #0770d4;
	}
</style>
