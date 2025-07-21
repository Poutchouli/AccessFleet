<script>
	import { locale, _, isLoading } from 'svelte-i18n';
	import { commandQueue } from '$lib/stores/commandQueue.js'; // Import our queue store
	import { user, login, logout } from '$lib/stores/session.js'; // Import session store
	import '../lib/i18n.js'; // Import to initialize
	import { onMount } from 'svelte';

	let showQueueModal = false;

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
</script>

<header>
	<h1>{!$isLoading ? $_('app.title') : 'IT Provisioning Platform'}</h1>
	<nav>
		<!-- Navigation for unlogged users -->
		{#if !$user}
			<a href="/">Home</a>
		{/if}

		<!-- Navigation for managers -->
		{#if $user && $user.role === 'manager'}
			<a href="/requests">View My Requests</a>
			<a href="/requests/new">Submit New Request</a>
			<a href="/shared-mailboxes">My Shared Mailboxes</a>
			<a href="/mailboxes">Manage Mailboxes</a>
		{/if}

		<!-- Navigation for admins -->
		{#if $user && $user.role === 'admin'}
			<a href="/">Home</a>
			<a href="/users">Users</a>
			<a href="/shared-mailboxes">Shared Mailboxes</a>
			<a href="/requests">View Requests</a>
			<a href="/admin/dashboard">Admin: Dashboard</a>
			<a href="/admin/forms">Admin: Forms</a>
			<a href="/admin/walkthroughs">Admin: Walkthroughs</a>
			<a href="/admin/temp-accounts">Admin: TEMP Accounts</a>
			<a href="/admin/new-user">Admin: New User</a>
			<a href="/admin/initialize">Admin: Initialize Data</a>
			<a href="/admin/analytics">Admin: Analytics</a>
			<a href="/admin/audit">Admin: Audit Log</a>
			<a href="/admin/db-explorer">Admin: DB Explorer</a>
		{/if}

		<div class="controls">
			{#if $commandQueue.length > 0}
				<button on:click={() => showQueueModal = true} class="queue-button">
					Command Queue ({$commandQueue.length})
				</button>
			{/if}

			<!-- User authentication controls -->
			{#if $user}
				<span>Welcome, {$user.full_name} ({$user.role})</span>
				<button on:click={logout} class="auth-button">Logout</button>
			{:else}
				<select on:change={handleLoginChange} class="login-select">
					<option value="">Login As...</option>
					<option value="1">Admin User (ID 1)</option>
					<option value="2">Manager User (ID 2 - Sarah)</option>
					<option value="3">Manager User (ID 3 - John)</option>
				</select>
			{/if}

			<div class="lang-switcher">
				<button class:active={$locale === 'en'} on:click={() => locale.set('en')}>EN</button>
				<button class:active={$locale === 'fr'} on:click={() => locale.set('fr')}>FR</button>
			</div>
		</div>
	</nav>
</header>

<main>
	<slot />
</main>

{#if showQueueModal}
	<div class="modal-backdrop" on:click={() => showQueueModal = false}>
		<div class="modal" on:click|stopPropagation>
			<h4>Queued PowerShell Commands</h4>
			<p>Copy the entire script below and run it in your PowerShell console.</p>
			<textarea readonly rows="10">{$commandQueue.join('\n')}</textarea>
			<button on:click={clearQueue}>Clear Queue & Close</button>
		</div>
	</div>
{/if}

<style>
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.5rem;
		background-color: white;
		border-bottom: 1px solid #e2e8f0;
	}
	h1 {
		font-size: 1.25rem;
		margin: 0;
	}
	nav {
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-grow: 1; /* Allow nav to grow */
	}
	nav a {
		color: #4a5568;
		text-decoration: none;
		font-weight: bold;
		padding: 0.5rem;
	}
	nav a:hover {
		color: #2c5282;
	}
	.controls {
		display: flex;
		align-items: center;
		margin-left: auto; /* Push controls to the right */
		gap: 1rem;
	}
	.queue-button {
		background-color: #e2e8f0;
		border: 1px solid #cbd5e0;
		border-radius: 5px;
		padding: 0.5rem 1rem;
		cursor: pointer;
		font-weight: bold;
		color: #2d3748;
	}
	.queue-button:hover {
		background-color: #cbd5e0;
	}
	.lang-switcher {
		display: flex;
		gap: 0.25rem;
	}
	nav .lang-switcher button {
		background: none;
		border: 1px solid transparent;
		padding: 0.5rem;
		cursor: pointer;
		font-weight: bold;
		color: #4a5568;
	}
	nav .lang-switcher button.active {
		color: #2c5282;
		border-bottom: 2px solid #2c5282;
	}
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
	}
	.modal {
		background-color: white;
		padding: 2rem;
		border-radius: 5px;
		width: 80%;
		max-width: 700px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}
	.modal textarea {
		width: 100%;
		font-family: monospace;
		padding: 0.5rem;
		border: 1px solid #cbd5e0;
		border-radius: 3px;
		margin: 1rem 0;
	}
	.modal button {
		background-color: #2c5282;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 5px;
		cursor: pointer;
		font-weight: bold;
	}
	.modal button:hover {
		background-color: #2a4a7c;
	}

	/* Authentication styling */
	.auth-button {
		background-color: #e53e3e;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 5px;
		cursor: pointer;
		font-weight: bold;
		margin-left: 0.5rem;
	}
	.auth-button:hover {
		background-color: #c53030;
	}

	.login-select {
		padding: 0.5rem;
		border: 1px solid #cbd5e0;
		border-radius: 5px;
		background-color: white;
		cursor: pointer;
		font-weight: bold;
	}

	.controls span {
		color: #2d3748;
		font-weight: bold;
		margin-right: 0.5rem;
	}
</style>