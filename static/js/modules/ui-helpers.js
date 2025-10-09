/**
 * UI Helpers Module
 * Common UI utilities and helper functions
 */

/**
 * Show notification to user
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `cyber-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    const container = document.querySelector('.notifications-container') || document.body;
    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Show modal dialog
 * @param {HTMLElement} modal - Modal element to show
 */
function showModal(modal) {
    modal.style.display = 'flex';
    document.querySelectorAll('#overlay').forEach(o => {
        o.classList.add('active');
    });

    setTimeout(() => {
        modal.classList.remove('hidden-modal');
        modal.classList.add('show-modal');
    }, 10);
}

/**
 * Hide modal dialog
 * @param {HTMLElement} modal - Modal element to hide
 */
function hideModal(modal) {
    modal.classList.remove('show-modal');
    modal.classList.add('hidden-modal');

    setTimeout(() => {
        modal.style.display = 'none';
        document.querySelectorAll('#overlay').forEach(o => {
            o.classList.remove('active');
        });
    }, 450);
}

/**
 * Close hint box
 * @param {string} hintId - ID of hint element
 */
function closeHint(hintId) {
    const hint = document.getElementById(hintId);
    if (hint) hint.style.display = 'none';
}

/**
 * Show hint box
 * @param {string} hintId - ID of hint element
 */
function showHint(hintId) {
    const hint = document.getElementById(hintId);
    if (hint && hint.style.display === 'none') {
        hint.style.display = 'block';
        setTimeout(() => closeHint(hintId), 8000);
    }
}

/**
 * Initialize tab switching functionality
 */
function initializeTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;

            // Update button states
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Activate selected tab
            this.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

/**
 * Initialize dropdown functionality
 */
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');

    document.addEventListener('click', (e) => {
        dropdowns.forEach(dropdown => {
            const isButton = dropdown.querySelector('.dropbtn').contains(e.target);

            if (isButton) {
                dropdown.classList.toggle('is-active');
            } else {
                dropdown.classList.remove('is-active');
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('is-active');
            });
        }
    });
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

/**
 * Initialize resizable panels
 */
function initializeResizablePanels() {
    var m_pos;
    var resize_el = document.getElementById("resize");

    if (!resize_el) return;

    function resize(e) {
        var parent = resize_el.parentNode;
        var dy = m_pos - e.y;
        m_pos = e.y;
        parent.style.height = (parent.offsetHeight + dy) + "px";
    }

    resize_el.addEventListener("mousedown", function(e) {
        m_pos = e.y;
        document.addEventListener("mousemove", resize, false);
    }, false);

    document.addEventListener("mouseup", function() {
        document.removeEventListener("mousemove", resize, false);
    }, false);
}

/**
 * Initialize all UI components
 */
function initializeUI() {
    initializeTabs();
    initializeDropdowns();
    initializeResizablePanels();

    // Initialize notifications container
    if (!document.querySelector('.notifications-container')) {
        const notificationsContainer = document.createElement('div');
        notificationsContainer.className = 'notifications-container';
        document.body.appendChild(notificationsContainer);
    }
}

// Make functions globally available
window.showNotification = showNotification;
window.showModal = showModal;
window.hideModal = hideModal;
window.closeHint = closeHint;
window.showHint = showHint;
window.debounce = debounce;
window.initializeUI = initializeUI;