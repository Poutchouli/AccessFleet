<script>
	import { locale, _ } from 'svelte-i18n';
	import { commandQueue } from '$lib/stores/commandQueue.js'; // Import our queue store
	import { user, login, logout } from '$lib/stores/session.js'; // Import session store
	import '../lib/i18n.js'; // Import to initialize
	import { onMount } from 'svelte';

	let showQueueModal = false;
	let showViewsDropdown = false;
	let showToolsDropdown = false;

	// Set default locale immediately
	locale.set('en');

	// When the app loads, try to set the locale from localStorage
	onMount(() => {
		const savedLocale = localStorage.getItem('lang');
		if (savedLocale) {
			locale.set(savedLocale);
		}

		// When locale changes, save it to localStorage
		locale.subscribe((value) => {
			if (value) {
				localStorage.setItem('lang', value);
			}
		});
	});

	function clearQueue() {
		commandQueue.set([]);
		showQueueModal = false;
	}

	// Handle login selection
	function handleLoginChange(event) {
		const userId = event.target.value;
		if (userId) {
			login(userId);
		}
		// Reset the select to show placeholder
		event.target.selectedIndex = 0;
	}

	function toggleViewsDropdown() {
		showViewsDropdown = !showViewsDropdown;
		showToolsDropdown = false; // Close other dropdown
	}

	function toggleToolsDropdown() {
		showToolsDropdown = !showToolsDropdown;
		showViewsDropdown = false; // Close other dropdown
	}

	// Close dropdowns when clicking outside
	function handleOutsideClick(event) {
		if (!event.target.closest('.dropdown')) {
			showViewsDropdown = false;
			showToolsDropdown = false;
		}
	}
</script>

<header>
	<h1>{$_('app.title')}</h1>
	<nav>
		{#if !$user}
			<a href="/">Home</a>
		{/if}

		{#if $user}
			<div class="dropdown">
				<button class="dropbtn" class:active={showViewsDropdown} on:click={toggleViewsDropdown}>
					📊 Views {showViewsDropdown ? '▲' : '▼'}
				</button>
				{#if showViewsDropdown}
					<div class="dropdown-content">
						{#if $user.role === 'admin'}
							<a href="/admin/dashboard">🏠 Dashboard</a>
							<a href="/admin/analytics">📈 Analytics</a>
							<a href="/users">👥 Users Directory</a>
							<a href="/requests">📋 All Requests</a>
							<a href="/admin/audit">📜 Audit Log</a>
							<a href="/admin/db-explorer">🗃️ Database Explorer</a>
						{/if}
						{#if $user.role === 'manager'}
							<a href="/requests">📋 Service Requests</a>
							<a href="/users">👥 Users Directory</a>
						{/if}
					</div>
				{/if}
			</div>

			<div class="dropdown">
				<button class="dropbtn" class:active={showToolsDropdown} on:click={toggleToolsDropdown}>
					🛠️ Tools {showToolsDropdown ? '▲' : '▼'}
				</button>
				{#if showToolsDropdown}
					<div class="dropdown-content">
						{#if $user.role === 'admin'}
							<a href="/admin/forms">📝 Form Builder</a>
							<a href="/admin/walkthroughs">📋 Walkthrough Creator</a>
							<a href="/admin/permissions">📧 Mailbox Permissions</a>
							<a href="/admin/temp-accounts">👤 TEMP Accounts</a>
							<a href="/admin/new-user">➕ New AD User</a>
							<a href="/admin/sql-runner">🗃️ SQL Runner</a>
							<a href="/admin/initialize">⚙️ Initialize Data</a>
						{/if}
						{#if $user.role === 'manager'}
							<a href="/requests/new">➕ Submit New Request</a>
							<a href="/mailboxes">📧 Manage Mailboxes</a>
						{/if}
					</div>
				{/if}
			</div>
		{/if}
	</nav>

	<div class="controls">
		{#if $commandQueue.length > 0}
			<button class="queue-button" on:click={() => showQueueModal = true}>
				💻 Command Queue ({$commandQueue.length})
			</button>
		{/if}
		{#if $user}
			<span class="welcome-text">Welcome, {$user.full_name}</span>
			<button class="logout-btn" on:click={logout}>Logout</button>
		{:else}
			<select class="login-select" on:change={handleLoginChange}>
				<option value="">Login As...</option>
				<option value="1">Admin User (ID 1)</option>
				<option value="2">Manager User (ID 2)</option>
				<option value="3">Manager User (ID 3)</option>
			</select>
		{/if}
	</div>
</header>

<!-- Click outside handler -->
<svelte:window on:click={handleOutsideClick} />

<main>
	<slot />
</main>

<!-- Command Queue Modal -->
{#if showQueueModal}
	<div class="modal-overlay" on:click={() => showQueueModal = false}>
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h3>💻 PowerShell Command Queue</h3>
				<button class="close-btn" on:click={() => showQueueModal = false}>✖</button>
			</div>
			<div class="modal-body">
				{#if $commandQueue.length > 0}
					<p class="queue-info">📋 {$commandQueue.length} command{$commandQueue.length === 1 ? '' : 's'} ready to execute</p>
					<textarea readonly rows="12" class="command-display">{$commandQueue.join('\n\n')}</textarea>
					<div class="modal-actions">
						<button class="clear-btn" on:click={clearQueue}>🗑️ Clear Queue</button>
						<button class="copy-btn" on:click={() => navigator.clipboard.writeText($commandQueue.join('\n\n'))}>
							📋 Copy to Clipboard
						</button>
					</div>
				{:else}
					<p class="empty-queue">Queue is empty. Commands will appear here when you perform admin actions.</p>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 1.5rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		height: 60px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	h1 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 600;
	}

	nav {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	nav a {
		text-decoration: none;
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		transition: background-color 0.2s;
	}

	nav a:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}

	.controls {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.welcome-text {
		color: rgba(255, 255, 255, 0.9);
		font-size: 0.9rem;
	}

	.logout-btn, .queue-button {
		background: rgba(255, 255, 255, 0.2);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.3);
		padding: 0.5rem 1rem;
		border-radius: 6px;
		cursor: pointer;
		transition: background-color 0.2s;
		font-size: 0.9rem;
		font-weight: bold;
	}

	.logout-btn:hover, .queue-button:hover {
		background: rgba(255, 255, 255, 0.3);
	}

	.login-select {
		background: rgba(255, 255, 255, 0.9);
		color: #333;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
	}

	/* --- Dropdown Styles --- */
	.dropdown {
		position: relative;
		display: inline-block;
	}

	.dropbtn {
		background-color: transparent;
		color: white;
		padding: 0.75rem 1rem;
		font-size: 0.95rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s ease-in-out;
		font-weight: 500;
	}

	.dropbtn:hover, .dropbtn.active {
		background-color: rgba(255, 255, 255, 0.1);
		border-color: rgba(255, 255, 255, 0.3);
	}

	.dropdown-content {
		/* Start hidden and out of the way */
		opacity: 0;
		transform: translateY(-10px);
		
		/* Positioning */
		position: absolute;
		top: 100%; /* Position directly below the button */
		left: 0;
		background-color: white;
		min-width: 220px;
		box-shadow: 0 8px 24px rgba(0,0,0,0.15);
		z-index: 1000;
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		overflow: hidden;
		margin-top: 0.5rem;
		
		/* Animation will be triggered by conditional rendering */
		animation: liquidDrop 0.4s ease-out forwards;
	}

	.dropdown-content a {
		color: #2d3436 !important;
		padding: 0.75rem 1rem !important;
		text-decoration: none;
		display: block;
		font-size: 0.9rem;
		transition: background-color 0.2s;
		border-bottom: 1px solid #f1f3f4;
	}

	.dropdown-content a:last-child {
		border-bottom: none;
	}

	.dropdown-content a:hover {
		background-color: #f8f9fa !important;
		color: #0984e3 !important;
	}

	/* The Liquid Drop Animation */
	@keyframes liquidDrop {
		0% {
			opacity: 0;
			transform: translateY(-10px);
		}
		70% {
			transform: translateY(5px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Modal styles */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
	}

	.modal-content {
		background: white;
		border-radius: 12px;
		width: 90%;
		max-width: 800px;
		max-height: 80%;
		box-shadow: 0 20px 40px rgba(0,0,0,0.1);
		overflow: hidden;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		background: #f8f9fa;
		border-bottom: 1px solid #e2e8f0;
	}

	.modal-header h3 {
		margin: 0;
		color: #2d3436;
	}

	.close-btn {
		background: none;
		border: none;
		font-size: 1.2rem;
		cursor: pointer;
		color: #636e72;
		padding: 0.25rem;
	}

	.close-btn:hover {
		color: #d63031;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.queue-info {
		background: #e3f2fd;
		color: #1976d2;
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1rem;
		font-weight: 500;
	}

	.command-display {
		width: 100%;
		padding: 1rem;
		border: 1px solid #ddd;
		border-radius: 8px;
		font-family: 'Courier New', monospace;
		font-size: 0.85rem;
		background: #f8f9fa;
		resize: vertical;
		margin-bottom: 1rem;
	}

	.modal-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
	}

	.clear-btn {
		background: #e74c3c;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
	}

	.clear-btn:hover {
		background: #c0392b;
	}

	.copy-btn {
		background: #0984e3;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
	}

	.copy-btn:hover {
		background: #0770d4;
	}

	.empty-queue {
		text-align: center;
		color: #636e72;
		font-style: italic;
		padding: 2rem;
	}

	main {
		flex: 1;
		padding: 2rem;
		background: #f8f9fa;
		min-height: calc(100vh - 60px);
	}

	@media (max-width: 768px) {
		header {
			flex-direction: column;
			height: auto;
			padding: 1rem;
		}

		nav {
			margin: 1rem 0;
		}

		.dropdown-content {
			position: static;
			box-shadow: none;
			background: rgba(255, 255, 255, 0.1);
			margin-top: 0.5rem;
		}

		.dropdown-content a {
			color: white !important;
		}

		.modal-content {
			width: 95%;
			margin: 1rem;
		}
	}
</style>