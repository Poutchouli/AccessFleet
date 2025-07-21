<script>
    import { page } from '$app/stores';
    import { user } from '$lib/stores/session.js';
    import { onMount } from 'svelte';
    import { invalidateAll } from '$app/navigation'; // Import invalidateAll for data refresh
    import { goto } from '$app/navigation'; // Import goto for SvelteKit navigation

    let template = null;
    let name = '';
    let description = '';
    let steps = [];
    let selectedTools = [];
    let isLoading = true;
    let isSubmitting = false;

    const templateId = $page.params.id;

    // Define our available tools
    const availableTools = [
        { id: 'new_user_form', name: 'New User Creation Form' },
        { id: 'temp_account_assignment', name: 'TEMP Account Assignment' },
        { id: 'mailbox_modifications', name: 'Mailbox Access Management' },
        { id: 'status_updates', name: 'Request Status Updates' },
        { id: 'audit_logging', name: 'Audit Log Review' }
    ];

    onMount(async () => {
        await loadTemplate();
    });

    async function loadTemplate() {
        try {
            const response = await fetch(`/api/admin/walkthrough-templates/${templateId}`, {
                headers: { 'user-id': $user.id.toString() }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load template');
            }
            
            template = await response.json();
            name = template.name;
            description = template.description;
            steps = template.steps || [];
            selectedTools = template.tools || [];
        } catch (error) {
            alert(`Error loading template: ${error.message}`);
            // Use SvelteKit navigation instead of window.location.href
            await goto('/admin/walkthroughs');
        } finally {
            isLoading = false;
        }
    }

    function addStep() {
        steps = [...steps, { type: 'note', content: '' }];
    }

    function removeStep(index) {
        steps = steps.filter((_, i) => i !== index);
    }

    function updateStep(index, field, value) {
        steps[index][field] = value;
        steps = steps; // Trigger reactivity
    }

    async function updateTemplate() {
        if (!name.trim() || !description.trim()) {
            alert('Please provide both a name and description for the template.');
            return;
        }

        if (steps.length === 0 || steps.every(step => !step.content.trim())) {
            alert('Please add at least one step with content.');
            return;
        }

        isSubmitting = true;

        try {
            const response = await fetch(`/api/admin/walkthrough-templates/${templateId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'user-id': $user.id.toString()
                },
                body: JSON.stringify({ 
                    name: name.trim(), 
                    description: description.trim(), 
                    steps, 
                    tools: selectedTools 
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update template');
            }
            
            // Invalidate all data before navigating to ensure fresh data load
            await invalidateAll();
            
            // Navigate back to the list page using SvelteKit's goto
            await goto('/admin/walkthroughs');
            
            alert('Template updated successfully!');
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            isSubmitting = false;
        }
    }

    async function deleteTemplate() {
        if (!confirm('Are you sure you want to delete this template? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/walkthrough-templates/${templateId}`, {
                method: 'DELETE',
                headers: { 'user-id': $user.id.toString() }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete template');
            }
            
            // Invalidate all data before navigating to ensure fresh data load
            await invalidateAll();
            
            // Navigate back to the list page using SvelteKit's goto
            await goto('/admin/walkthroughs');
            
            alert('Template deleted successfully!');
        } catch (error) {
            alert(`Error deleting template: ${error.message}`);
        }
    }
</script>

{#if $user?.role === 'admin'}
    <div class="container">
        <div class="header">
            <h2>Edit Walkthrough Template</h2>
            <a href="/admin/walkthroughs" class="back-btn">← Back to Walkthroughs</a>
        </div>

        {#if isLoading}
            <div class="loading">
                <p>Loading template...</p>
            </div>
        {:else if template}
            <form on:submit|preventDefault={updateTemplate}>
                <div class="form-section">
                    <h3>Basic Information</h3>
                    <div class="form-group">
                        <label for="name">Template Name *</label>
                        <input 
                            type="text" 
                            id="name" 
                            bind:value={name} 
                            placeholder="e.g., New Employee Onboarding"
                            required
                        />
                    </div>

                    <div class="form-group">
                        <label for="description">Description *</label>
                        <textarea 
                            id="description" 
                            bind:value={description} 
                            placeholder="Describe what this walkthrough is for..."
                            rows="3"
                            required
                        ></textarea>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Steps</h3>
                    <p class="help-text">Define the step-by-step process for administrators to follow.</p>
                    
                    {#each steps as step, index}
                        <div class="step-item">
                            <div class="step-header">
                                <h4>Step {index + 1}</h4>
                                {#if steps.length > 1}
                                    <button 
                                        type="button" 
                                        class="remove-step-btn"
                                        on:click={() => removeStep(index)}
                                    >
                                        Remove
                                    </button>
                                {/if}
                            </div>

                            <div class="form-group">
                                <label for="step-type-{index}">Step Type</label>
                                <select 
                                    id="step-type-{index}"
                                    value={step.type}
                                    on:change={(e) => updateStep(index, 'type', e.target.value)}
                                >
                                    <option value="note">Note/Instruction</option>
                                    <option value="task">Task/Action</option>
                                    <option value="check">Verification/Check</option>
                                    <option value="warning">Warning/Caution</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="step-content-{index}">Content</label>
                                <textarea 
                                    id="step-content-{index}"
                                    value={step.content}
                                    on:input={(e) => updateStep(index, 'content', e.target.value)}
                                    placeholder="Enter the step content..."
                                    rows="3"
                                ></textarea>
                            </div>
                        </div>
                    {/each}

                    <button type="button" class="add-step-btn" on:click={addStep}>
                        + Add Step
                    </button>
                </div>

                <div class="form-section">
                    <h3>Associated Tools</h3>
                    <p class="help-text">Select the tools that should appear when this walkthrough is active.</p>
                    
                    <div class="tools-grid">
                        {#each availableTools as tool}
                            <label class="tool-option">
                                <input 
                                    type="checkbox" 
                                    bind:group={selectedTools} 
                                    value={tool.id} 
                                />
                                <span class="tool-name">{tool.name}</span>
                            </label>
                        {/each}
                    </div>
                </div>

                <div class="form-actions">
                    <button type="button" class="delete-btn" on:click={deleteTemplate}>
                        Delete Template
                    </button>
                    <div class="primary-actions">
                        <button type="button" class="cancel-btn" on:click={() => goto('/admin/walkthroughs')}>
                            Cancel
                        </button>
                        <button type="submit" class="save-btn" disabled={isSubmitting}>
                            {isSubmitting ? 'Updating...' : 'Update Template'}
                        </button>
                    </div>
                </div>
            </form>
        {:else}
            <div class="error">
                <p>Template not found or failed to load.</p>
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
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    .back-btn {
        background-color: #6c757d;
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 4px;
        font-size: 0.875rem;
        transition: background-color 0.2s;
    }

    .back-btn:hover {
        background-color: #5a6268;
    }

    .loading, .error {
        text-align: center;
        padding: 2rem;
        color: #666;
    }

    .form-section {
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }

    .form-section h3 {
        margin: 0 0 1rem 0;
        color: #333;
        border-bottom: 2px solid #f8f9fa;
        padding-bottom: 0.5rem;
    }

    .help-text {
        color: #666;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        font-style: italic;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #333;
    }

    .form-group input,
    .form-group textarea,
    .form-group select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
        font-family: inherit;
    }

    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
        outline: none;
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
    }

    .step-item {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .step-header h4 {
        margin: 0;
        color: #495057;
    }

    .remove-step-btn {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .remove-step-btn:hover {
        background-color: #c82333;
    }

    .add-step-btn {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .add-step-btn:hover {
        background-color: #218838;
    }

    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }

    .tool-option {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.2s, border-color 0.2s;
    }

    .tool-option:hover {
        background-color: #e9ecef;
        border-color: #007bff;
    }

    .tool-option input[type="checkbox"] {
        width: auto;
        margin: 0;
    }

    .tool-name {
        font-weight: 500;
        color: #333;
    }

    .form-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 2rem;
        border-top: 1px solid #eee;
    }

    .primary-actions {
        display: flex;
        gap: 1rem;
    }

    .delete-btn {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .delete-btn:hover {
        background-color: #c82333;
    }

    .cancel-btn {
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .cancel-btn:hover {
        background-color: #5a6268;
    }

    .save-btn {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 4px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .save-btn:hover:not(:disabled) {
        background-color: #0056b3;
    }

    .save-btn:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }

    .unauthorized {
        text-align: center;
        padding: 2rem;
        color: #721c24;
    }
</style>
