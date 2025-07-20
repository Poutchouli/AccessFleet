<script>
	import { commandQueue } from '$lib/stores/commandQueue.js';

	let userData = {
		first_name: '',
		last_name: '',
		sam_account_name: '',
		department: '',
		password: ''
	};

	let isLoading = false;

	async function generateCommand() {
		if (!userData.password) {
			alert('A temporary password is required.');
			return;
		}

		if (!userData.sam_account_name) {
			alert('Login name (SAM Account Name) is required.');
			return;
		}

		isLoading = true;
		try {
			const response = await fetch('/api/admin/generate-new-user-command', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(userData)
			});

			if (!response.ok) throw new Error('Failed to generate command.');

			const result = await response.json();
			commandQueue.update(q => [...q, result.powershell_command]);
			alert('New User command has been added to the queue!');
			
			// Clear the form
			userData = { 
				first_name: '', 
				last_name: '', 
				sam_account_name: '', 
				department: '', 
				password: '' 
			};

		} catch (error) {
			alert(`Error: ${error.message}`);
		} finally {
			isLoading = false;
		}
	}

	function generateSamAccountName() {
		if (userData.first_name && userData.last_name) {
			userData.sam_account_name = `${userData.first_name.toLowerCase()}.${userData.last_name.toLowerCase()}`.replace(/\s/g, '');
		}
	}
</script>

<h2>Create New Active Directory User</h2>
<p>Fill out the details below to generate and queue the PowerShell command for creating a new user.</p>

<div class="form-container">
	<form on:submit|preventDefault={generateCommand}>
		<div class="form-grid">
			<div class="form-group">
				<label for="first_name">First Name:</label>
				<input 
					id="first_name" 
					type="text" 
					bind:value={userData.first_name} 
					on:input={generateSamAccountName}
					required 
					disabled={isLoading}
				/>
			</div>

			<div class="form-group">
				<label for="last_name">Last Name:</label>
				<input 
					id="last_name" 
					type="text" 
					bind:value={userData.last_name} 
					on:input={generateSamAccountName}
					required 
					disabled={isLoading}
				/>
			</div>

			<div class="form-group">
				<label for="sam_account_name">Login Name (SAM Account Name):</label>
				<input 
					id="sam_account_name" 
					type="text" 
					bind:value={userData.sam_account_name} 
					required 
					disabled={isLoading}
					placeholder="e.g., john.doe"
				/>
				<small>This will be auto-generated from first and last name</small>
			</div>

			<div class="form-group">
				<label for="department">Department:</label>
				<input 
					id="department" 
					type="text" 
					bind:value={userData.department} 
					required 
					disabled={isLoading}
					placeholder="e.g., IT, HR, Finance"
				/>
			</div>

			<div class="form-group">
				<label for="password">Temporary Password:</label>
				<input 
					id="password" 
					type="password" 
					bind:value={userData.password} 
					required 
					disabled={isLoading}
					placeholder="User must change on first login"
				/>
				<small>User will be required to change this password on first login</small>
			</div>
		</div>

		<div class="form-actions">
			<button type="submit" disabled={isLoading} class="primary-button">
				{#if isLoading}
					Generating Command...
				{:else}
					Generate & Queue Command
				{/if}
			</button>
		</div>
	</form>

	<div class="info-section">
		<h3>📝 What This Does</h3>
		<ul>
			<li>Creates a new Active Directory user account</li>
			<li>Sets the user's basic information (name, department, login)</li>
			<li>Assigns a temporary password that must be changed on first login</li>
			<li>Enables the account immediately</li>
			<li>Places the user in the default Users OU</li>
		</ul>
	</div>
</div>

<style>
	.form-container {
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 2rem;
		margin-top: 1rem;
	}

	.form-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.form-group:nth-child(3),
	.form-group:nth-child(4),
	.form-group:nth-child(5) {
		grid-column: 1 / -1;
	}

	label {
		font-weight: bold;
		color: #2d3748;
		font-size: 0.9rem;
	}

	input {
		padding: 0.75rem;
		border: 2px solid #e2e8f0;
		border-radius: 6px;
		font-size: 1rem;
		transition: border-color 0.2s;
	}

	input:focus {
		outline: none;
		border-color: #4299e1;
		box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
	}

	input:disabled {
		background-color: #f7fafc;
		cursor: not-allowed;
	}

	input::placeholder {
		color: #a0aec0;
	}

	small {
		color: #718096;
		font-size: 0.8rem;
		margin-top: 0.25rem;
	}

	.form-actions {
		grid-column: 1 / -1;
		margin-top: 1rem;
	}

	.primary-button {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		padding: 1rem 2rem;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: bold;
		cursor: pointer;
		transition: transform 0.2s, box-shadow 0.2s;
		width: 100%;
	}

	.primary-button:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
	}

	.primary-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	.info-section {
		background: #f7fafc;
		border-left: 4px solid #667eea;
		border-radius: 8px;
		padding: 1.5rem;
		height: fit-content;
	}

	.info-section h3 {
		margin: 0 0 1rem 0;
		color: #2d3748;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.info-section ul {
		margin: 0;
		padding-left: 1.2rem;
		color: #4a5568;
	}

	.info-section li {
		margin-bottom: 0.5rem;
	}

	h2 {
		color: #2d3748;
		margin-bottom: 0.5rem;
	}

	p {
		color: #718096;
		margin-bottom: 2rem;
	}

	@media (max-width: 768px) {
		.form-container {
			grid-template-columns: 1fr;
		}
		
		.form-grid {
			grid-template-columns: 1fr;
		}
		
		.form-group:nth-child(3),
		.form-group:nth-child(4),
		.form-group:nth-child(5) {
			grid-column: 1;
		}
	}
</style>
