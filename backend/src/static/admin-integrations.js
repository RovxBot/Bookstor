// API Integrations Management JavaScript

let currentIntegrationId = null;

function showAddIntegrationModal() {
    currentIntegrationId = null;
    document.getElementById('modalTitle').textContent = 'Add API Integration';
    document.getElementById('integrationForm').reset();
    document.getElementById('integrationId').value = '';
    document.getElementById('name').disabled = false;
    document.getElementById('integrationModal').style.display = 'flex';
}

function closeIntegrationModal() {
    document.getElementById('integrationModal').style.display = 'none';
    currentIntegrationId = null;
}

async function editIntegration(integrationId) {
    // Get integration data from the card
    const card = document.querySelector(`[data-integration-id="${integrationId}"]`);
    if (!card) return;

    currentIntegrationId = integrationId;
    document.getElementById('modalTitle').textContent = 'Edit API Integration';
    document.getElementById('integrationId').value = integrationId;

    // Extract data from the card
    const displayName = card.querySelector('.integration-info h3').textContent;
    const name = card.querySelector('.integration-name').textContent;
    const description = card.querySelector('.integration-description')?.textContent || '';
    const baseUrl = card.querySelector('.detail-row:nth-child(1) code').textContent;
    const priority = card.querySelector('.priority-badge').textContent;

    // Fill form
    document.getElementById('name').value = name;
    document.getElementById('name').disabled = true; // Can't change name
    document.getElementById('display_name').value = displayName;
    document.getElementById('description').value = description;
    document.getElementById('base_url').value = baseUrl === 'Not set' ? '' : baseUrl;
    document.getElementById('priority').value = priority;

    document.getElementById('integrationModal').style.display = 'flex';
}

async function saveIntegration(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const integrationId = document.getElementById('integrationId').value;

    try {
        let response;
        if (integrationId) {
            // Update existing integration
            response = await fetch(`/admin/api/integrations/${integrationId}`, {
                method: 'PATCH',
                body: formData
            });
        } else {
            // Create new integration
            response = await fetch('/admin/api/integrations', {
                method: 'POST',
                body: formData
            });
        }

        const data = await response.json();

        if (response.ok) {
            showNotification('Integration saved successfully', 'success');
            closeIntegrationModal();
            // Reload page to show updated data
            setTimeout(() => window.location.reload(), 500);
        } else {
            showNotification(data.detail || 'Failed to save integration', 'error');
        }
    } catch (error) {
        console.error('Error saving integration:', error);
        showNotification('An error occurred while saving', 'error');
    }
}

async function toggleIntegration(integrationId, enabled) {
    const formData = new FormData();
    formData.append('is_enabled', enabled);

    try {
        const response = await fetch(`/admin/api/integrations/${integrationId}`, {
            method: 'PATCH',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(
                `Integration ${enabled ? 'enabled' : 'disabled'} successfully`,
                'success'
            );
            // Update the badge
            const card = document.querySelector(`[data-integration-id="${integrationId}"]`);
            const badge = card.querySelector('.status-label .badge');
            if (enabled) {
                badge.className = 'badge badge-success';
                badge.textContent = 'Enabled';
            } else {
                badge.className = 'badge badge-secondary';
                badge.textContent = 'Disabled';
            }
        } else {
            showNotification(data.detail || 'Failed to toggle integration', 'error');
            // Revert the toggle
            const toggle = document.querySelector(`[data-integration-id="${integrationId}"] input[type="checkbox"]`);
            toggle.checked = !enabled;
        }
    } catch (error) {
        console.error('Error toggling integration:', error);
        showNotification('An error occurred', 'error');
        // Revert the toggle
        const toggle = document.querySelector(`[data-integration-id="${integrationId}"] input[type="checkbox"]`);
        toggle.checked = !enabled;
    }
}

async function deleteIntegration(integrationId, displayName) {
    if (!confirm(`Are you sure you want to delete "${displayName}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`/admin/api/integrations/${integrationId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Integration deleted successfully', 'success');
            // Remove the card from the page
            const card = document.querySelector(`[data-integration-id="${integrationId}"]`);
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.remove();
                // Check if there are no more integrations
                const remainingCards = document.querySelectorAll('.integration-card');
                if (remainingCards.length === 0) {
                    window.location.reload();
                }
            }, 300);
        } else {
            showNotification(data.detail || 'Failed to delete integration', 'error');
        }
    } catch (error) {
        console.error('Error deleting integration:', error);
        showNotification('An error occurred while deleting', 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add to page
    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => notification.classList.add('show'), 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('integrationModal');
    if (e.target === modal) {
        closeIntegrationModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeIntegrationModal();
    }
});

