/**
 * Delete Action Handler with AJAX
 * Handles deletion of supervisors and employees without page reload.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup Delete Supervisor Modal
    const deleteSupBtn = document.getElementById('confirmDeleteSupBtn');
    if (deleteSupBtn) {
        deleteSupBtn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const url = `/manager/delete_supervisor/${id}`;
            performDelete(url, `sup-row-${id}`, 'deleteSupervisorModal');
        });
    }

    // 2. Setup Delete Employee Modal
    const deleteEmpBtn = document.getElementById('confirmDeleteEmpBtn');
    if (deleteEmpBtn) {
        deleteEmpBtn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const url = `/manager/delete_employee/${id}`;
            performDelete(url, `emp-row-${id}`, 'deleteEmployeeModal');
        });
    }
});

// Helper to open modal and set data - Exposed Globally
window.openDeleteSupervisorModal = function (id, name) {
    document.getElementById('delSupName').textContent = name;
    document.getElementById('confirmDeleteSupBtn').setAttribute('data-id', id);
    new bootstrap.Modal(document.getElementById('deleteSupervisorModal')).show();
};

window.openDeleteEmployeeModal = function (id, name) {
    document.getElementById('delEmpName').textContent = name;
    document.getElementById('confirmDeleteEmpBtn').setAttribute('data-id', id);
    new bootstrap.Modal(document.getElementById('deleteEmployeeModal')).show();
};

window.openPasswordModal = function (id, name) {
    document.getElementById('pwdSupName').textContent = name;
    const idField = document.querySelector('#passwordModal input[name="id"]');
    if (idField) idField.value = id;
    new bootstrap.Modal(document.getElementById('passwordModal')).show();
};

// Perform AJAX Delete
function performDelete(url, rowId, modalId) {
    const csrfToken = getCsrfToken();

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            // Hide Modal
            const modalEl = document.getElementById(modalId);
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            if (data.success) {
                // Remove Row with Animation
                const row = document.getElementById(rowId);
                if (row) {
                    row.classList.add('fade-out-row');
                    setTimeout(() => row.remove(), 500);
                }
                showAlert('success', data.message);
            } else {
                showAlert('danger', data.message || 'Delete failed.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An unexpected error occurred.');
            const modalEl = document.getElementById(modalId);
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        });
}

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function showAlert(type, message) {
    const container = document.getElementById('alert-container');
    if (!container) return;

    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show animate-fade-up" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    container.innerHTML = alertHtml;

    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 4000);
}
