/**
 * Search & Filter Engine
 * Lightweight, logic for filtering tables and grids.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInputs = document.querySelectorAll('.search-input');

    searchInputs.forEach(input => {
        input.addEventListener('keyup', function () {
            const query = this.value.toLowerCase();
            const targetId = this.getAttribute('data-target');
            const targetContainer = document.getElementById(targetId);

            if (!targetContainer) return;

            // Determine if we are filtering a table or a grid/list
            const isTable = targetContainer.tagName === 'TBODY';

            let items;
            if (isTable) {
                items = targetContainer.querySelectorAll('tr');
            } else {
                // If not a table, looks for direct children or specific class cards
                items = targetContainer.querySelectorAll('.search-item');
                // If no specific class, fallback to direct children
                if (items.length === 0) items = targetContainer.children;
            }

            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const match = text.includes(query);

                if (match) {
                    item.style.display = '';
                    // Optional: Highlight logic could go here
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});
