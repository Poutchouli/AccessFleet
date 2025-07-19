<script>
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	let message = $_('backend_status.loading');
	let backendMessage = '';

	onMount(async () => {
		try {
			const response = await fetch('/api');
			if (!response.ok) throw new Error('Network response was not ok');
			const data = await response.json();
			backendMessage = data.message;
			// Note: 'message' is reactive and will update when the locale changes
		} catch (error) {
			backendMessage = $_('backend_status.failed');
			console.error(error);
		}
	});
</script>

<h2>{$_('backend_status.message', { values: { message: backendMessage } })}</h2>