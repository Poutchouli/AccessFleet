<script>
    import { onMount } from 'svelte';
    import { user } from '$lib/stores/session.js';

    let mailboxes = [];
    let pendingChanges = {}; // To track additions and removals
    let notification = '';
    let isSubmitting = false;

    onMount(async () => {
        if ($user) {
            try {
                const response = await fetch('/api/manager/mailboxes', {
                    headers: {
                        'user-id': $user.id.toString()
                    }
                });
                if (response.ok) {
                    mailboxes = await response.json();
                    // Initialize pendingChanges for each mailbox
                    mailboxes.forEach(mailbox => {
                        pendingChanges[mailbox.id] = {
                            add_users: [],
                            remove_users: []
                        };
                    });
                } else {
                    notification = 'Failed to load mailboxes';
                }
            } catch (error) {
                notification = 'Error loading mailboxes: ' + error.message;
            }
        }
    });

    function addUser(mailboxId, userName) {
        if (!userName.trim()) return;
        
        const email = userName.trim().toLowerCase();
        
        // Check if user is already in the current users list
        const mailbox = mailboxes.find(m => m.id === mailboxId);
        const currentUsers = mailbox.full_access_users ? 
            mailbox.full_access_users.split(';').map(u => u.trim().toLowerCase()) : [];
        
        if (currentUsers.includes(email)) {
            notification = `User ${email} already has access to this mailbox`;
            return;
        }
        
        // Check if user is already in pending additions
        if (pendingChanges[mailboxId].add_users.includes(email)) {
            notification = `User ${email} is already pending addition`;
            return;
        }
        
        // Remove from pending removals if exists
        const removeIndex = pendingChanges[mailboxId].remove_users.indexOf(email);
        if (removeIndex > -1) {
            pendingChanges[mailboxId].remove_users.splice(removeIndex, 1);
        } else {
            // Add to pending additions
            pendingChanges[mailboxId].add_users.push(email);
        }
        
        // Clear the input
        document.getElementById('add-user-' + mailboxId).value = '';
        pendingChanges = pendingChanges; // Trigger reactivity
        notification = '';
    }

    function removeUser(mailboxId, userEmail) {
        const email = userEmail.trim().toLowerCase();
        
        // Check if user is in pending additions
        const addIndex = pendingChanges[mailboxId].add_users.indexOf(email);
        if (addIndex > -1) {
            pendingChanges[mailboxId].add_users.splice(addIndex, 1);
        } else {
            // Add to pending removals
            if (!pendingChanges[mailboxId].remove_users.includes(email)) {
                pendingChanges[mailboxId].remove_users.push(email);
            }
        }
        
        pendingChanges = pendingChanges; // Trigger reactivity
        notification = '';
    }
    
    function cancelChange(mailboxId, userEmail, type) {
        const email = userEmail.toLowerCase();
        if (type === 'add') {
            const index = pendingChanges[mailboxId].add_users.indexOf(email);
            if (index > -1) {
                pendingChanges[mailboxId].add_users.splice(index, 1);
            }
        } else if (type === 'remove') {
            const index = pendingChanges[mailboxId].remove_users.indexOf(email);
            if (index > -1) {
                pendingChanges[mailboxId].remove_users.splice(index, 1);
            }
        }
        pendingChanges = pendingChanges; // Trigger reactivity
    }
    
    async function generateRequest() {
        if (!$user || isSubmitting) return;
        
        isSubmitting = true;
        notification = '';
        
        // Build modifications array
        const modifications = [];
        
        for (const [mailboxIdStr, changes] of Object.entries(pendingChanges)) {
            const mailboxId = parseInt(mailboxIdStr);
            const mailbox = mailboxes.find(m => m.id === mailboxId);
            
            if (changes.add_users.length > 0 || changes.remove_users.length > 0) {
                modifications.push({
                    mailbox_id: mailboxId,
                    mailbox_name: mailbox.display_name,
                    add_users: changes.add_users,
                    remove_users: changes.remove_users
                });
            }
        }
        
        if (modifications.length === 0) {
            notification = 'No changes to submit';
            isSubmitting = false;
            return;
        }
        
        try {
            const response = await fetch('/api/requests/mailbox-modifications', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'user-id': $user.id.toString()
                },
                body: JSON.stringify({ modifications })
            });
            
            if (response.ok) {
                notification = 'Request submitted successfully! Admins will review your changes.';
                // Clear pending changes
                mailboxes.forEach(mailbox => {
                    pendingChanges[mailbox.id] = {
                        add_users: [],
                        remove_users: []
                    };
                });
                pendingChanges = pendingChanges; // Trigger reactivity
            } else {
                const error = await response.json();
                notification = 'Failed to submit request: ' + (error.detail || 'Unknown error');
            }
        } catch (error) {
            notification = 'Error submitting request: ' + error.message;
        }
        
        isSubmitting = false;
    }
    
    function handleKeyPress(event, mailboxId) {
        if (event.key === 'Enter') {
            addUser(mailboxId, event.target.value);
        }
    }
    
    // Check if there are any pending changes
    $: hasPendingChanges = Object.values(pendingChanges).some(changes => 
        changes.add_users.length > 0 || changes.remove_users.length > 0
    );
</script>

{#if $user?.role === 'manager'}
    <div class="container">
        <h2>Manage Shared Mailbox Access</h2>
        
        {#if notification}
            <div class="notification" class:success={notification.includes('successfully')} class:error={notification.includes('Failed') || notification.includes('Error')}>
                {notification}
            </div>
        {/if}

        {#if mailboxes.length === 0}
            <p class="no-mailboxes">No mailboxes assigned to you for management.</p>
        {:else}
            {#each mailboxes as mailbox}
                <div class="mailbox-card">
                    <h3>{mailbox.display_name}</h3>
                    <p class="email">{mailbox.primary_smtp_address}</p>
                    
                    <div class="user-section">
                        <h4>Current Users with Full Access:</h4>
                        <div class="user-list">
                            {#if mailbox.full_access_users}
                                {#each mailbox.full_access_users.split(';') as userEmail}
                                    <div class="user-item">
                                        <span class="user-email">{userEmail.trim()}</span>
                                        {#if pendingChanges[mailbox.id].remove_users.includes(userEmail.trim().toLowerCase())}
                                            <span class="pending-remove">Pending Removal</span>
                                            <button class="cancel-btn" on:click={() => cancelChange(mailbox.id, userEmail, 'remove')}>
                                                Cancel
                                            </button>
                                        {:else}
                                            <button class="remove-btn" on:click={() => removeUser(mailbox.id, userEmail)}>
                                                Remove
                                            </button>
                                        {/if}
                                    </div>
                                {/each}
                            {:else}
                                <p class="no-users">No users currently have access</p>
                            {/if}
                        </div>
                    </div>

                    {#if pendingChanges[mailbox.id].add_users.length > 0}
                        <div class="pending-section">
                            <h4>Pending Additions:</h4>
                            <div class="user-list">
                                {#each pendingChanges[mailbox.id].add_users as userEmail}
                                    <div class="user-item pending">
                                        <span class="user-email">{userEmail}</span>
                                        <span class="pending-add">Pending Addition</span>
                                        <button class="cancel-btn" on:click={() => cancelChange(mailbox.id, userEmail, 'add')}>
                                            Cancel
                                        </button>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <div class="add-user-form">
                        <input 
                            type="email" 
                            placeholder="Enter user email to add" 
                            id="add-user-{mailbox.id}"
                            on:keypress={(e) => handleKeyPress(e, mailbox.id)}
                        />
                        <button 
                            class="add-btn"
                            on:click={() => addUser(mailbox.id, document.getElementById('add-user-' + mailbox.id).value)}
                        >
                            Add User
                        </button>
                    </div>
                </div>
            {/each}

            <div class="action-section">
                <button 
                    class="submit-btn" 
                    on:click={generateRequest} 
                    disabled={!hasPendingChanges || isSubmitting}
                >
                    {isSubmitting ? 'Submitting...' : 'Submit Request'}
                </button>
                
                {#if hasPendingChanges}
                    <p class="changes-info">
                        You have pending changes. Click "Submit Request" to send them for admin approval.
                    </p>
                {/if}
            </div>
        {/if}
    </div>
{:else}
    <div class="unauthorized">
        <h2>Access Denied</h2>
        <p>This page is only accessible to managers.</p>
    </div>
{/if}

<style>
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .notification {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .notification.success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .notification.error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .mailbox-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .mailbox-card h3 {
        margin: 0 0 0.5rem 0;
        color: #333;
    }
    
    .email {
        color: #666;
        font-style: italic;
        margin-bottom: 1.5rem;
    }
    
    .user-section, .pending-section {
        margin-bottom: 1.5rem;
    }
    
    .user-section h4, .pending-section h4 {
        margin: 0 0 0.75rem 0;
        color: #555;
        font-size: 1rem;
    }
    
    .user-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .user-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 4px;
    }
    
    .user-item.pending {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
    }
    
    .user-email {
        flex: 1;
        font-family: monospace;
    }
    
    .pending-add {
        color: #856404;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .pending-remove {
        color: #dc3545;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .remove-btn, .cancel-btn, .add-btn {
        padding: 0.25rem 0.75rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.875rem;
        transition: background-color 0.2s;
    }
    
    .remove-btn {
        background-color: #dc3545;
        color: white;
    }
    
    .remove-btn:hover {
        background-color: #c82333;
    }
    
    .cancel-btn {
        background-color: #6c757d;
        color: white;
    }
    
    .cancel-btn:hover {
        background-color: #5a6268;
    }
    
    .add-btn {
        background-color: #28a745;
        color: white;
    }
    
    .add-btn:hover {
        background-color: #218838;
    }
    
    .add-user-form {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .add-user-form input {
        flex: 1;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
    }
    
    .action-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 2px solid #eee;
        text-align: center;
    }
    
    .submit-btn {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 4px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .submit-btn:hover:not(:disabled) {
        background-color: #0056b3;
    }
    
    .submit-btn:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }
    
    .changes-info {
        margin-top: 1rem;
        color: #856404;
        font-style: italic;
    }
    
    .no-mailboxes, .no-users {
        color: #666;
        font-style: italic;
        text-align: center;
        padding: 2rem;
    }
    
    .unauthorized {
        text-align: center;
        padding: 2rem;
        color: #721c24;
    }
</style>
