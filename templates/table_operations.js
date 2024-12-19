// static/js/table_operations.js

document.addEventListener('DOMContentLoaded', function() {
    // Add Record Form Submission
    const addForm = document.getElementById('addForm');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(addForm);
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error adding record: ' + data.message);
                }
            });
        });
    }
});

function editRecord(id) {
    // Get the row data
    const row = document.querySelector(`tr[data-id="${id}"]`);
    const cells = row.querySelectorAll('td');
    const data = {};
    
    cells.forEach((cell, index) => {
        const fieldName = document.querySelector('th:nth-child(' + (index + 1) + ')').textContent;
        data[fieldName] = cell.textContent;
    });
    
    // Create edit form
    const form = document.createElement('form');
    form.className = 'edit-form';
    
    for (let field in data) {
        if (field !== 'Actions') {
            const input = document.createElement('input');
            input.type = 'text';
            input.name = field;
            input.value = data[field];
            input.className = 'border rounded px-2 py-1 w-full mb-2';
            
            const label = document.createElement('label');
            label.textContent = field;
            label.className = 'block text-sm font-bold mb-1';
            
            form.appendChild(label);
            form.appendChild(input);
        }
    }
    
    // Add save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.className = 'bg-green-500 text-white px-4 py-2 rounded mr-2';
    saveButton.onclick = function() {
        const formData = new FormData(form);
        
        fetch(`${window.location.href}/${id}`, {
            method: 'PUT',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error updating record: ' + data.message);
            }
        });
    };
    
    // Add cancel button
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.className = 'bg-gray-500 text-white px-4 py-2 rounded';
    cancelButton.onclick = function() {
        modal.remove();
    };
    
    form.appendChild(saveButton);
    form.appendChild(cancelButton);
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'bg-white p-6 rounded-lg w-96';
    modalContent.appendChild(form);
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}

function deleteRecord(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        fetch(`${window.location.href}/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting record: ' + data.message);
            }
        });
    }
}