// Function to populate the existing lists table from Chrome storage
function populateListsTable() {
    chrome.storage.sync.get(null, function(items) {
        var listsTable = document.getElementById('listsTable');
        // Clear any existing rows (except the header row)
        listsTable.innerHTML = '<tr><th>Name</th><th>Type</th><th>ID (Optional)</th></tr>';
        for (var key in items) {
            var list = items[key];
            var row = document.createElement('tr');
            row.innerHTML = '<td>' + list.name + '</td><td>' + list.type + '</td><td>' + (list.id || '') + '</td>';
            listsTable.appendChild(row);
        }
    });
}

// Function to handle the form submission and save the new list
document.getElementById('listForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Prevent the form from submitting the traditional way

    var listName = document.getElementById('listName').value;
    var listType = document.getElementById('listType').value;
    var listID = document.getElementById('listID').value || null;  // Default to null if no ID is provided

    // Create a list object
    var list = {
        name: listName,
        type: listType,
        id: listID
    };

    // Save the list object to Chrome storage
    chrome.storage.sync.set({ [listName]: list }, function() {
        console.log('List saved:', list);
        // Clear the form fields
        document.getElementById('listForm').reset();
        // Repopulate the lists table
        populateListsTable();
    });
});

// Populate the existing lists table when the popup is opened
populateListsTable();
