<script>
	import { onMount } from 'svelte';
	import { Chart } from 'chart.js/auto';

	let volumeChartCanvas;
	let statusChartCanvas;
	let volumeChart;
	let statusChart;
	let isLoading = true;
	let error = null;
	let totalRequests = 0;
	let avgDaily = 0;
	
	// Data variables that will trigger reactive chart creation
	let volumeData = null;
	let statusData = null;

	// Fetch data when the component mounts
	onMount(async () => {
		try {
			// Fetch volume data
			const volumeResponse = await fetch('/api/analytics/request-volume');
			if (!volumeResponse.ok) throw new Error('Failed to fetch volume data');
			volumeData = (await volumeResponse.json()).reverse(); // Reverse to show oldest to newest

			// Fetch status breakdown
			const statusResponse = await fetch('/api/analytics/status-breakdown');
			if (!statusResponse.ok) throw new Error('Failed to fetch status data');
			statusData = await statusResponse.json();

			// Calculate totals
			totalRequests = statusData.reduce((sum, item) => sum + item.count, 0);
			avgDaily = volumeData.length > 0 ? (totalRequests / volumeData.length).toFixed(1) : 0;

			isLoading = false;
		} catch (err) {
			error = err.message;
			isLoading = false;
		}
	});

	// Reactive statement: Create volume chart when canvas and data are both available
	$: if (volumeChartCanvas && volumeData && !isLoading) {
		// Destroy the old chart instance if it exists, to prevent memory leaks
		if (volumeChart) {
			volumeChart.destroy();
		}

		const volumeLabels = volumeData.map(item => item.date);
		const volumeValues = volumeData.map(item => item.count);

		volumeChart = new Chart(volumeChartCanvas, {
			type: 'line',
			data: {
				labels: volumeLabels,
				datasets: [{
					label: 'New Requests per Day',
					data: volumeValues,
					borderColor: 'rgb(75, 192, 192)',
					backgroundColor: 'rgba(75, 192, 192, 0.2)',
					tension: 0.1,
					fill: true
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Request Volume Over Time'
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						ticks: {
							stepSize: 1
						}
					}
				}
			}
		});
	}

	// Reactive statement: Create status chart when canvas and data are both available
	$: if (statusChartCanvas && statusData && !isLoading) {
		// Destroy the old chart instance if it exists, to prevent memory leaks
		if (statusChart) {
			statusChart.destroy();
		}

		const statusLabels = statusData.map(item => item.status);
		const statusValues = statusData.map(item => item.count);
		const statusColors = [
			'rgba(255, 206, 84, 0.8)',
			'rgba(54, 162, 235, 0.8)',
			'rgba(75, 192, 192, 0.8)',
			'rgba(255, 99, 132, 0.8)'
		];

		statusChart = new Chart(statusChartCanvas, {
			type: 'doughnut',
			data: {
				labels: statusLabels,
				datasets: [{
					data: statusValues,
					backgroundColor: statusColors,
					borderWidth: 2,
					borderColor: '#fff'
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Request Status Distribution'
					}
				}
			}
		});
	}
</script>

<h2>Analytics Dashboard</h2>

{#if isLoading}
	<p>Loading analytics data...</p>
{:else if error}
	<p class="error">Error: {error}</p>
{:else}
	<div class="analytics-container">
		<!-- KPI Cards -->
		<div class="kpi-grid">
			<div class="kpi-card">
				<h3>Total Requests</h3>
				<div class="kpi-value">{totalRequests}</div>
			</div>
			<div class="kpi-card">
				<h3>Average Daily</h3>
				<div class="kpi-value">{avgDaily}</div>
			</div>
		</div>

		<!-- Charts Grid -->
		<div class="charts-grid">
			<div class="chart-container">
				<canvas bind:this={volumeChartCanvas}></canvas>
			</div>
			
			<div class="chart-container">
				<canvas bind:this={statusChartCanvas}></canvas>
			</div>
		</div>
		
		<div class="insights-section">
			<div class="insight-card">
				<h3>📊 Insights</h3>
				<ul>
					<li>Track request volume trends to predict resource needs</li>
					<li>Monitor status distribution to identify bottlenecks</li>
					<li>Use data to optimize IT provisioning processes</li>
				</ul>
			</div>
		</div>
	</div>
{/if}

<style>
	.analytics-container {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		margin-top: 1rem;
	}

	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.kpi-card {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border-radius: 12px;
		padding: 1.5rem;
		text-align: center;
		box-shadow: 0 4px 15px rgba(0,0,0,0.1);
	}

	.kpi-card h3 {
		margin: 0 0 0.5rem 0;
		font-size: 0.9rem;
		opacity: 0.9;
		text-transform: uppercase;
		letter-spacing: 1px;
	}

	.kpi-value {
		font-size: 2.5rem;
		font-weight: bold;
		margin: 0;
	}

	.charts-grid {
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 2rem;
		margin-bottom: 2rem;
	}

	.chart-container {
		position: relative;
		height: 400px;
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 4px 15px rgba(0,0,0,0.1);
	}

	.insights-section {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
	}

	.insight-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 4px 15px rgba(0,0,0,0.1);
		border-left: 4px solid #667eea;
	}

	.insight-card h3 {
		margin: 0 0 1rem 0;
		color: #2d3748;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.insight-card ul {
		margin: 0;
		padding-left: 1.2rem;
		color: #4a5568;
	}

	.insight-card li {
		margin-bottom: 0.5rem;
	}

	.error {
		color: #e53e3e;
		background: #fed7d7;
		padding: 1rem;
		border-radius: 8px;
		border: 1px solid #feb2b2;
	}

	h2 {
		color: #2d3748;
		margin-bottom: 1rem;
		font-size: 2rem;
	}

	@media (max-width: 768px) {
		.charts-grid {
			grid-template-columns: 1fr;
		}
		
		.kpi-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
