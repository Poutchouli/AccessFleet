<script>
	import { locale, _, isLoading } from 'svelte-i18n';
	import '../lib/i18n.js'; // Import to initialize
	import { onMount } from 'svelte';

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
</script>

<header>
	<h1>{!$isLoading ? $_('app.title') : 'IT Provisioning Platform'}</h1>
	<nav>
		<a href="/">Home</a>
		<a href="/users">Users</a>
		<a href="/requests">View Requests</a>
		<a href="/admin/forms">Admin: Forms</a>
		<div class="lang-switcher">
			<button class:active={$locale === 'en'} on:click={() => locale.set('en')}>EN</button>
			<button class:active={$locale === 'fr'} on:click={() => locale.set('fr')}>FR</button>
		</div>
	</nav>
</header>

<main>
	<slot />
</main>

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
	.lang-switcher {
		margin-left: auto;
	}
	nav button {
		background: none;
		border: 1px solid transparent;
		padding: 0.5rem;
		margin-left: 0.5rem;
		cursor: pointer;
		font-weight: bold;
		color: #4a5568;
	}
	nav button.active {
		color: #2c5282;
		border-bottom: 2px solid #2c5282;
	}
</style>