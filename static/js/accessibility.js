/**
 * Accessibility Enhancements
 * 
 * This script provides various accessibility improvements for the application:
 * - Better keyboard navigation
 * - ARIA attribute management
 * - Focus management
 * - Screen reader announcements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize accessibility features
    initAccessibility();
});

/**
 * Initialize all accessibility enhancements
 */
function initAccessibility() {
    // Handle focus management
    setupFocusManagement();
    
    // Enhance form accessibility
    enhanceFormAccessibility();
    
    // Improve dropdown accessibility
    setupDropdownAccessibility();
    
    // Set up accessible alerts
    setupAccessibleAlerts();
    
    // Add escape key handler for modals/dialogs
    setupEscapeKeyHandler();
}

/**
 * Set up proper focus management
 */
function setupFocusManagement() {
    // Add focus indicators to all interactive elements that don't have them
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex="0"]');
    
    interactiveElements.forEach(element => {
        if (!element.classList.contains('focus:outline-none') && 
            !element.classList.contains('focus:ring-2')) {
            element.classList.add('focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500');
        }
    });
}

/**
 * Enhance form accessibility
 */
function enhanceFormAccessibility() {
    // Ensure all form inputs have associated labels
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Skip inputs with type="hidden"
        if (input.type === 'hidden') return;
        
        // Check if input has an id
        if (!input.id) {
            // Generate a unique ID
            const uniqueId = 'input-' + Math.random().toString(36).substr(2, 9);
            input.id = uniqueId;
        }
        
        // Check if input has an associated label
        const hasLabel = document.querySelector(`label[for="${input.id}"]`);
        
        if (!hasLabel) {
            // Try to find a parent label
            const parentLabel = input.closest('label');
            if (!parentLabel) {
                console.warn(`Input with id "${input.id}" does not have an associated label.`);
            }
        }
        
        // Add required attribute if aria-required is true
        if (input.getAttribute('aria-required') === 'true' && !input.hasAttribute('required')) {
            input.setAttribute('required', 'required');
        }
    });
}

/**
 * Set up dropdown accessibility
 */
function setupDropdownAccessibility() {
    const dropdowns = document.querySelectorAll('[aria-haspopup="true"]');
    
    dropdowns.forEach(dropdown => {
        const dropdownButton = dropdown;
        const dropdownMenu = document.getElementById(dropdown.getAttribute('aria-controls'));
        
        if (!dropdownMenu) return;
        
        // Ensure aria-expanded is set correctly
        if (!dropdownButton.hasAttribute('aria-expanded')) {
            dropdownButton.setAttribute('aria-expanded', 'false');
        }
        
        // Update aria-expanded when dropdown visibility changes
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const isHidden = dropdownMenu.classList.contains('hidden');
                    dropdownButton.setAttribute('aria-expanded', !isHidden);
                }
            });
        });
        
        observer.observe(dropdownMenu, { attributes: true });
    });
}

/**
 * Set up accessible alerts
 */
function setupAccessibleAlerts() {
    // Find all flash messages
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Ensure the alert has the appropriate role
        if (!alert.hasAttribute('role')) {
            alert.setAttribute('role', 'alert');
        }
        
        // Ensure it has aria-live for screen readers
        if (!alert.hasAttribute('aria-live')) {
            alert.setAttribute('aria-live', 'assertive');
        }
    });
}

/**
 * Set up escape key handler for modals/dialogs
 */
function setupEscapeKeyHandler() {
    document.addEventListener('keydown', function(event) {
        // Check if the key pressed was Escape
        if (event.key === 'Escape') {
            // Close any open dropdowns
            const openDropdowns = document.querySelectorAll('[aria-expanded="true"]');
            openDropdowns.forEach(dropdown => {
                const dropdownId = dropdown.getAttribute('aria-controls');
                const dropdownMenu = document.getElementById(dropdownId);
                
                if (dropdownMenu) {
                    dropdown.setAttribute('aria-expanded', 'false');
                    dropdownMenu.classList.add('hidden');
                }
            });
            
            // Close any open modals/dialogs
            const openModals = document.querySelectorAll('[role="dialog"]:not(.hidden)');
            openModals.forEach(modal => {
                modal.classList.add('hidden');
            });
        }
    });
}

/**
 * Announce a message to screen readers
 * 
 * @param {string} message - Message to announce
 * @param {string} politeness - Can be 'assertive' or 'polite'
 */
function announceToScreenReader(message, politeness = 'assertive') {
    // Create or get the live region
    let liveRegion = document.getElementById('sr-announcer');
    
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'sr-announcer';
        liveRegion.setAttribute('aria-live', politeness);
        liveRegion.setAttribute('role', 'status');
        liveRegion.className = 'sr-only';
        document.body.appendChild(liveRegion);
    } else {
        liveRegion.setAttribute('aria-live', politeness);
    }
    
    // Set the message
    liveRegion.textContent = '';
    
    // Use setTimeout to ensure the DOM update and announcement
    setTimeout(() => {
        liveRegion.textContent = message;
    }, 50);
}
