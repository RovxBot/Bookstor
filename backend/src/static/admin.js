// Admin Panel JavaScript

// Utility function for API calls
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Confirm dialog
function confirmAction(message) {
    return confirm(message);
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    console.log('Bookstor Admin Panel loaded');
});

