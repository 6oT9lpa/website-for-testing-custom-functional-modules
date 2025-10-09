/**
 * Profile Page Script
 * Main entry point for profile page functionality
 * Initializes UI components and user hints
 */

/**
 * Initialize user hints system
 */
function initializeHints() {
    // Show hints for new users
    const registrationTime = new Date(window.userRegistrationTime || Date.now()).getTime();
    const threeHoursAgo = Date.now() - (3 * 60 * 60 * 1000);

    if (registrationTime > threeHoursAgo) {
        showHint('welcomeHint');
        setTimeout(() => showHint('modulesHint'), 3500);
        setTimeout(() => showHint('activationHint'), 7000);
    }

    // Setup tab change hints
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            if (tabId === 'functions') {
                showHint('modulesHint');
            }
        });
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    initializeHints();
});
