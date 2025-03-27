document.addEventListener('DOMContentLoaded', function() {
    const notificationIcon = document.getElementById('notification-icon');
    const notificationModal = document.getElementById('notification-modal');
    const closeNotificationModal = document.getElementById('close-notification-modal');
    const notificationList = document.getElementById('notification-list');
    const markAllReadButton = document.getElementById('mark-all-read');
    
    if (!notificationIcon) return;

    // Open notification modal when clicking the icon
    notificationIcon.addEventListener('click', function() {
        notificationModal.style.display = 'block';
        loadNotifications();
    });
    
    // Close notification modal when clicking the close button
    if (closeNotificationModal) {
        closeNotificationModal.addEventListener('click', function() {
            notificationModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === notificationModal) {
            notificationModal.style.display = 'none';
        }
    });
    
    // Mark all notifications as read
    if (markAllReadButton) {
        markAllReadButton.addEventListener('click', function() {
            markAllNotificationsAsRead();
        });
    }
    
    // Load notifications from the API
    function loadNotifications() {
        notificationList.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
        
        fetch('/orders/api/notifications/')
            .then(response => response.json())
            .then(data => {
                renderNotifications(data);
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                notificationList.innerHTML = `<div class="empty-notifications">Nepavyko įkelti pranešimų.</div>`;
            });
    }
    
    // Render notifications in the modal
    function renderNotifications(notifications) {
        if (notifications.length === 0) {
            notificationList.innerHTML = `<div class="empty-notifications">Nėra naujų pranešimų.</div>`;
            return;
        }
        
        let notificationHTML = '';
        
        notifications.forEach(notification => {
            const unreadClass = notification.is_read ? '' : 'unread';
            const statusIndicator = notification.is_read ? '' : '<div class="status-indicator"></div>';
            const formattedDate = formatDate(notification.created_at);
            
            let actionButton = '';
            if (notification.action_url) {
                actionButton = `
                    <div class="notification-actions">
                        <a href="${notification.action_url}" class="notification-action">Peržiūrėti</a>
                        <a href="#" class="notification-action mark-read" data-id="${notification.id}">Pažymėti kaip skaitytą</a>
                    </div>
                `;
            }
            
            notificationHTML += `
                <div class="notification-item ${unreadClass}" data-id="${notification.id}">
                    <div class="notification-content">
                        <div class="notification-title">${notification.title}</div>
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-time">${formattedDate}</div>
                        ${actionButton}
                    </div>
                    <div class="notification-status">
                        ${statusIndicator}
                    </div>
                </div>
            `;
        });
        
        notificationList.innerHTML = notificationHTML;
        
        // Add event listeners to mark-read buttons
        document.querySelectorAll('.mark-read').forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const notificationId = this.getAttribute('data-id');
                markNotificationAsRead(notificationId);
            });
        });
        
        // Add event listeners to notification items
        document.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', function(event) {
                if (!event.target.classList.contains('notification-action')) {
                    const notificationId = this.getAttribute('data-id');
                    markNotificationAsRead(notificationId);
                    
                    // If the notification has an action URL, navigate to it
                    const actionUrl = this.querySelector('.notification-action');
                    if (actionUrl && actionUrl.getAttribute('href') !== '#') {
                        window.location.href = actionUrl.getAttribute('href');
                    }
                }
            });
        });
    }
    
    // Mark a specific notification as read
    function markNotificationAsRead(notificationId) {
        fetch(`/orders/api/notifications/${notificationId}/mark-read/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI
                const notificationItem = document.querySelector(`.notification-item[data-id="${notificationId}"]`);
                if (notificationItem) {
                    notificationItem.classList.remove('unread');
                    const statusIndicator = notificationItem.querySelector('.status-indicator');
                    if (statusIndicator) {
                        statusIndicator.remove();
                    }
                }
                
                // Update notification count
                updateNotificationCount();
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    }
    
    // Mark all notifications as read
    function markAllNotificationsAsRead() {
        fetch('/orders/api/notifications/mark-all-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload notifications
                loadNotifications();
                
                // Update notification count
                updateNotificationCount(0);
            }
        })
        .catch(error => {
            console.error('Error marking all notifications as read:', error);
        });
    }
    
    // Update notification count in the UI
    function updateNotificationCount(count = null) {
        if (count !== null) {
            // Set the count directly if provided
            updateNotificationCountUI(count);
        } else {
            // Otherwise, fetch the current count
            fetch('/orders/api/notifications/unread-count/')
                .then(response => response.json())
                .then(data => {
                    updateNotificationCountUI(data.count);
                })
                .catch(error => {
                    console.error('Error getting notification count:', error);
                });
        }
    }
    
    // Update the notification count UI element
    function updateNotificationCountUI(count) {
        let countElement = notificationIcon.querySelector('.notification-count');
        
        if (count > 0) {
            if (!countElement) {
                countElement = document.createElement('span');
                countElement.className = 'notification-count';
                notificationIcon.appendChild(countElement);
            }
            countElement.textContent = count;
        } else {
            if (countElement) {
                countElement.remove();
            }
        }
    }
    
    // Format date to a user-friendly string
    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) {
            return 'Ką tik';
        } else if (diffMins < 60) {
            return `${diffMins} min. ago`;
        } else if (diffHours < 24) {
            return `${diffHours} val. ago`;
        } else if (diffDays < 7) {
            return `${diffDays} d. ago`;
        } else {
            return date.toLocaleDateString('lt-LT');
        }
    }
    
    // Helper function to get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Check for unread notifications when the page loads
    updateNotificationCount();
    
    // Periodically check for new notifications (every 60 seconds)
    setInterval(updateNotificationCount, 60000);
});