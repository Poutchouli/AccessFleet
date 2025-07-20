<script>
	let userMessage = '';
	let mailboxMessage = '';
	let isUserLoading = false;
	let isMailboxLoading = false;

	const userExportCommand = `Get-ADUser -Filter {Enabled -eq $true} -Properties DisplayName, EmailAddress | Select-Object DisplayName, EmailAddress | Export-Csv -Path "C:\\temp\\ad_users_export.csv" -NoTypeInformation`;
	const mailboxExportCommand = `Get-EXOMailbox -RecipientTypeDetails SharedMailbox -ResultSize Unlimited | Select-Object DisplayName, PrimarySmtpAddress, @{Name="FullAccess";Expression={(Get-EXOMailboxPermission -Identity $_.Identity | Where-Object { $_.AccessRights -eq 'FullAccess' -and !$_.IsInherited } | ForEach-Object { $_.User.ToString() }) -join ';'}} | Export-Csv -Path "C:\\temp\\shared_mailboxes_export.csv" -NoTypeInformation`;

	async function handleUpload(event, type) {
		const file = event.target.files[0];
		if (!file) return;

		if (type === 'users') {
			isUserLoading = true;
			userMessage = 'Uploading...';
		} else {
			isMailboxLoading = true;
			mailboxMessage = 'Uploading...';
		}
		
		const formData = new FormData();
		formData.append('file', file);
		
		const endpoint = type === 'users' ? '/api/admin/upload-ad-users-csv' : '/api/admin/upload-shared-mailboxes-csv';

		try {
			const response = await fetch(endpoint, { method: 'POST', body: formData });
			const result = await response.json();
			if (!response.ok) throw new Error(result.detail || 'Upload failed');
			
			if (type === 'users') userMessage = result.message;
			else mailboxMessage = result.message;

		} catch (error) {
			if (type === 'users') userMessage = `Error: ${error.message}`;
			else mailboxMessage = `Error: ${error.message}`;
		} finally {
			if (type === 'users') isUserLoading = false;
			else isMailboxLoading = false;
		}
	}

	function copyToClipboard(text) {
		navigator.clipboard.writeText(text).then(() => {
			alert('Command copied to clipboard!');
		}).catch(() => {
			alert('Failed to copy to clipboard. Please copy manually.');
		});
	}
</script>

<div class="container">
	<h2>🚀 Initialize Application Data</h2>
	<p class="intro">Use the PowerShell commands below to export data from your environment, then upload the resulting CSV files to populate the application's database with realistic baseline data.</p>

	<div class="workflow-section">
		<div class="workflow-box">
			<h3>📋 Step 1: Import Active Directory Users</h3>
			<p>This will populate the 'Users' list for realistic testing. The application will skip any users whose email address already exists in the database.</p>
			
			<div class="command-section">
				<label>PowerShell Command to Export AD Users:</label>
				<div class="command-wrapper">
					<textarea readonly rows="3" class="command-text">{userExportCommand}</textarea>
					<button class="copy-btn" on:click={() => copyToClipboard(userExportCommand)}>📋 Copy</button>
				</div>
			</div>

			<div class="upload-section">
				<label for="users-upload">Upload ad_users_export.csv:</label>
				<input 
					id="users-upload"
					type="file" 
					accept=".csv" 
					on:change={(e) => handleUpload(e, 'users')} 
					disabled={isUserLoading} 
					class="file-input"
				/>
				{#if userMessage}
					<div class="message" class:success={userMessage.includes('Added')} class:error={userMessage.includes('Error')}>
						{userMessage}
					</div>
				{/if}
			</div>
		</div>

		<div class="workflow-box">
			<h3>📮 Step 2: Import Shared Mailboxes</h3>
			<p>This will populate a new list of all shared mailboxes and their access permissions for comprehensive mailbox management.</p>
			
			<div class="command-section">
				<label>PowerShell Command to Export Shared Mailboxes:</label>
				<div class="command-wrapper">
					<textarea readonly rows="4" class="command-text">{mailboxExportCommand}</textarea>
					<button class="copy-btn" on:click={() => copyToClipboard(mailboxExportCommand)}>📋 Copy</button>
				</div>
			</div>

			<div class="upload-section">
				<label for="mailboxes-upload">Upload shared_mailboxes_export.csv:</label>
				<input 
					id="mailboxes-upload"
					type="file" 
					accept=".csv" 
					on:change={(e) => handleUpload(e, 'mailboxes')} 
					disabled={isMailboxLoading} 
					class="file-input"
				/>
				{#if mailboxMessage}
					<div class="message" class:success={mailboxMessage.includes('Added')} class:error={mailboxMessage.includes('Error')}>
						{mailboxMessage}
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="info-panel">
		<h3>ℹ️ Important Notes</h3>
		<ul>
			<li><strong>Prerequisites:</strong> Ensure you have appropriate permissions and PowerShell modules installed (ActiveDirectory and ExchangeOnlineManagement)</li>
			<li><strong>File Location:</strong> Commands export to C:\temp\ - ensure this directory exists</li>
			<li><strong>Data Safety:</strong> Existing records with matching email addresses will be skipped</li>
			<li><strong>Default Role:</strong> All imported AD users will be assigned the 'manager' role by default</li>
			<li><strong>Processing:</strong> Large CSV files may take a moment to process</li>
		</ul>
	</div>
</div>

<style>
	.container {
		max-width: 1000px;
		margin: 0 auto;
		padding: 2rem;
	}

	.intro {
		color: #6b7280;
		font-size: 1.1rem;
		margin-bottom: 2rem;
		line-height: 1.6;
	}

	.workflow-section {
		display: grid;
		gap: 2rem;
		margin-bottom: 2rem;
	}

	.workflow-box {
		border: 2px solid #e5e7eb;
		border-radius: 12px;
		padding: 2rem;
		background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	.workflow-box h3 {
		color: #374151;
		margin: 0 0 1rem 0;
		font-size: 1.25rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.workflow-box p {
		color: #6b7280;
		margin-bottom: 1.5rem;
		line-height: 1.5;
	}

	.command-section {
		margin-bottom: 1.5rem;
	}

	.command-section label {
		display: block;
		font-weight: 600;
		color: #374151;
		margin-bottom: 0.5rem;
	}

	.command-wrapper {
		position: relative;
		display: flex;
		gap: 0.5rem;
	}

	.command-text {
		flex: 1;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		padding: 1rem;
		border: 2px solid #d1d5db;
		border-radius: 8px;
		background-color: #f9fafb;
		color: #374151;
		resize: none;
		overflow-x: auto;
		white-space: nowrap;
	}

	.copy-btn {
		background: #4f46e5;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		height: fit-content;
		align-self: flex-start;
		transition: background-color 0.2s;
	}

	.copy-btn:hover {
		background: #4338ca;
	}

	.upload-section label {
		display: block;
		font-weight: 600;
		color: #374151;
		margin-bottom: 0.5rem;
	}

	.file-input {
		display: block;
		width: 100%;
		padding: 0.75rem;
		border: 2px dashed #d1d5db;
		border-radius: 8px;
		background: #ffffff;
		cursor: pointer;
		transition: border-color 0.2s;
	}

	.file-input:hover {
		border-color: #9ca3af;
	}

	.file-input:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.message {
		margin-top: 1rem;
		padding: 0.75rem;
		border-radius: 6px;
		font-weight: 500;
	}

	.message.success {
		background-color: #d1fae5;
		color: #065f46;
		border: 1px solid #a7f3d0;
	}

	.message.error {
		background-color: #fef2f2;
		color: #991b1b;
		border: 1px solid #fecaca;
	}

	.info-panel {
		background: #eff6ff;
		border: 1px solid #dbeafe;
		border-radius: 12px;
		padding: 1.5rem;
	}

	.info-panel h3 {
		color: #1e40af;
		margin: 0 0 1rem 0;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.info-panel ul {
		margin: 0;
		padding-left: 1.5rem;
		color: #1e40af;
	}

	.info-panel li {
		margin-bottom: 0.5rem;
		line-height: 1.5;
	}

	h2 {
		color: #1f2937;
		margin-bottom: 1rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	@media (max-width: 768px) {
		.container {
			padding: 1rem;
		}
		
		.command-wrapper {
			flex-direction: column;
		}
		
		.copy-btn {
			align-self: stretch;
		}
	}
</style>
