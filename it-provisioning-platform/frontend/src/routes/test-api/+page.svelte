<script>
	import { onMount } from 'svelte';
	
	let testResults = [];
	let loading = false;

	async function testAPI(endpoint, name) {
		loading = true;
		try {
			console.log(`Testing ${name} at ${endpoint}`);
			const response = await fetch(endpoint);
			console.log(`Response status for ${name}:`, response.status);
			
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}
			
			const data = await response.json();
			testResults = [...testResults, {
				name,
				endpoint,
				status: 'SUCCESS',
				data: Array.isArray(data) ? `Array with ${data.length} items` : 'Object',
				error: null
			}];
		} catch (err) {
			console.error(`Error testing ${name}:`, err);
			testResults = [...testResults, {
				name,
				endpoint,
				status: 'ERROR',
				data: null,
				error: err.message
			}];
		}
		loading = false;
	}

	async function runAllTests() {
		testResults = [];
		await testAPI('http://localhost:8000/', 'Backend Root');
		await testAPI('http://localhost:8000/form-definitions', 'Form Definitions');
		await testAPI('http://localhost:8000/requests', 'Requests');
		await testAPI('http://localhost:8000/analytics/request-volume', 'Analytics Volume');
	}

	onMount(() => {
		runAllTests();
	});
</script>

<div class="container">
	<h2>API Testing Page</h2>
	<p>This page tests all the API endpoints to diagnose fetch issues.</p>
	
	<button on:click={runAllTests} disabled={loading}>
		{loading ? 'Testing...' : 'Run Tests Again'}
	</button>

	<div class="results">
		{#each testResults as result}
			<div class="test-result {result.status.toLowerCase()}">
				<h3>{result.name}</h3>
				<p><strong>Endpoint:</strong> {result.endpoint}</p>
				<p><strong>Status:</strong> {result.status}</p>
				{#if result.status === 'SUCCESS'}
					<p><strong>Data:</strong> {result.data}</p>
				{:else}
					<p><strong>Error:</strong> {result.error}</p>
				{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 20px;
	}

	button {
		background: #007bff;
		color: white;
		border: none;
		padding: 10px 20px;
		border-radius: 5px;
		cursor: pointer;
		margin-bottom: 20px;
	}

	button:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.results {
		display: grid;
		gap: 15px;
	}

	.test-result {
		border: 2px solid;
		border-radius: 8px;
		padding: 15px;
	}

	.test-result.success {
		border-color: #28a745;
		background-color: #d4edda;
	}

	.test-result.error {
		border-color: #dc3545;
		background-color: #f8d7da;
	}

	.test-result h3 {
		margin: 0 0 10px 0;
		color: #333;
	}

	.test-result p {
		margin: 5px 0;
		color: #555;
	}
</style>
