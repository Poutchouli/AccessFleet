<script>
    import { onMount } from 'svelte';
    import { user } from '$lib/stores/session.js';

    let walkthroughs = [];
    let loading = true;
    let error = '';

    onMount(async () => {
        if ($user?.role === 'admin') {
            try {
                const response = await fetch('/api/admin/walkthrough-templates/', {
                    headers: {
                        'user-id': $user.id.toString()
                    }
                });
                if (response.ok) {
                    walkthroughs = await response.json();
                } else {
                    error = 'Failed to load walkthroughs';
                }
            } catch (err) {
                error = 'Error loading walkthroughs: ' + err.message;
            }
        }
        loading = false;
    });

    async function deleteWalkthrough(id) {
        if (!confirm('Are you sure you want to delete this walkthrough?')) return;
        
        try {
            const response = await fetch(`/api/admin/walkthrough-templates/${id}`, {
                method: 'DELETE',
                headers: {
                    'user-id': $user.id.toString()
                }
            });
            if (response.ok) {
                walkthroughs = walkthroughs.filter(w => w.id !== id);
            } else {
                alert('Failed to delete walkthrough');
            }
        } catch (err) {
            alert('Error deleting walkthrough: ' + err.message);
        }
    }
</script>

{#if $user?.role === 'admin'}
    <div class="container">
        <h2>Manage Walkthrough Templates</h2>
        
        <div class="actions">
            <a href="/admin/walkthroughs/create" class="create-btn">
                Create New Walkthrough
            </a>
        </div>

        {#if loading}
            <p>Loading walkthroughs...</p>
        {:else if error}
            <div class="error">{error}</div>
        {:else if walkthroughs.length === 0}
            <div class="empty-state">
                <p>No walkthrough templates exist yet.</p>
                <a href="/admin/walkthroughs/create" class="create-btn">
                    Create the first one
                </a>
            </div>
        {:else}
            <div class="walkthroughs-grid">
                {#each walkthroughs as walkthrough}
                    <div class="walkthrough-card">
                        <h3>{walkthrough.name}</h3>
                        <p class="description">{walkthrough.description}</p>
                        
                        <div class="stats">
                            <span class="stat">
                                <strong>{walkthrough.steps?.length || 0}</strong> steps
                            </span>
                            {#if walkthrough.tools && walkthrough.tools.length > 0}
                                <span class="stat">
                                    <strong>{walkthrough.tools.length}</strong> tools
                                </span>
                            {/if}
                        </div>

                        {#if walkthrough.tools && walkthrough.tools.length > 0}
                            <div class="tools">
                                <h4>Associated Tools:</h4>
                                <div class="tool-tags">
                                    {#each walkthrough.tools as tool}
                                        <span class="tool-tag">{tool}</span>
                                    {/each}
                                </div>
                            </div>
                        {/if}

                        <div class="actions">
                            <a href="/admin/walkthroughs/edit/{walkthrough.id}" class="edit-btn">
                                Edit
                            </a>
                            <button 
                                class="delete-btn" 
                                on:click={() => deleteWalkthrough(walkthrough.id)}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
{:else}
    <div class="unauthorized">
        <h2>Access Denied</h2>
        <p>This page is only accessible to administrators.</p>
    </div>
{/if}

<style>
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    .actions {
        margin-bottom: 2rem;
    }

    .create-btn {
        background-color: #28a745;
        color: white;
        padding: 0.75rem 1.5rem;
        text-decoration: none;
        border-radius: 4px;
        font-weight: 500;
        display: inline-block;
        transition: background-color 0.2s;
    }

    .create-btn:hover {
        background-color: #218838;
    }

    .error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    .empty-state {
        text-align: center;
        padding: 3rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 2px dashed #dee2e6;
    }

    .walkthroughs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 2rem;
    }

    .walkthrough-card {
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .walkthrough-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .walkthrough-card h3 {
        margin: 0 0 0.5rem 0;
        color: #333;
    }

    .description {
        color: #666;
        margin-bottom: 1rem;
        line-height: 1.4;
    }

    .stats {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .stat {
        background-color: #f8f9fa;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.875rem;
        color: #495057;
    }

    .tools {
        margin-bottom: 1.5rem;
    }

    .tools h4 {
        margin: 0 0 0.5rem 0;
        font-size: 0.875rem;
        color: #495057;
    }

    .tool-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .tool-tag {
        background-color: #007bff;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .walkthrough-card .actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }

    .edit-btn {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 4px;
        font-size: 0.875rem;
        flex: 1;
        text-align: center;
        transition: background-color 0.2s;
    }

    .edit-btn:hover {
        background-color: #0056b3;
    }

    .delete-btn {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.875rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .delete-btn:hover {
        background-color: #c82333;
    }

    .unauthorized {
        text-align: center;
        padding: 2rem;
        color: #721c24;
    }
</style>
