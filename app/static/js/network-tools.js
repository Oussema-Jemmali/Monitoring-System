// Show IP Address functionality
document.getElementById('show-ip-btn').addEventListener('click', function() {
    fetch('/get_ip')
        .then(response => response.json())
        .then(data => {
            if (data.ip) {
                document.getElementById('ip-display').textContent = data.ip;
            } else {
                document.getElementById('ip-display').textContent = 'Error getting IP';
            }
        })
        .catch(error => {
            document.getElementById('ip-display').textContent = 'Error getting IP';
            console.error('Error:', error);
        });
});

// Calculate CIDR functionality
document.getElementById('calculate-cidr-btn').addEventListener('click', function() {
    const ipInput = document.getElementById('ip-input').value;
    if (!ipInput) {
        document.getElementById('cidr-results').innerHTML = 
            '<div class="alert alert-danger mt-2">Please enter an IP address</div>';
        return;
    }
    
    fetch('/calculate_cidr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ip: ipInput })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('cidr-results').innerHTML = 
                    `<div class="alert alert-danger mt-2">Error: ${data.error}</div>`;
            } else {
                document.getElementById('cidr-results').innerHTML = `
                    <div class="alert alert-info mt-2">
                        <p><strong>Network:</strong> ${data.network}</p>
                        <p><strong>Netmask:</strong> ${data.netmask}</p>
                        <p><strong>CIDR:</strong> ${data.cidr}</p>
                        <p><strong>Broadcast:</strong> ${data.broadcast}</p>
                        <p><strong>First Host:</strong> ${data.first_host}</p>
                        <p><strong>Last Host:</strong> ${data.last_host}</p>
                    </div>`;
            }
        })
        .catch(error => {
            document.getElementById('cidr-results').innerHTML = 
                '<div class="alert alert-danger mt-2">Error calculating CIDR</div>';
            console.error('Error:', error);
        });
});

// Ping IP functionality
document.getElementById('ping-ip-btn').addEventListener('click', function() {
    const ipInput = document.getElementById('ping-ip-input').value;
    if (!ipInput) {
        document.getElementById('ping-results').innerHTML = 
            '<div class="alert alert-danger mt-2">Please enter an IP address</div>';
        return;
    }

    // Show loading state
    document.getElementById('ping-results').innerHTML = 
        '<div class="alert alert-info mt-2">Pinging ' + ipInput + '...</div>';

    fetch('/ping_ip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ip: ipInput })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('ping-results').innerHTML = 
                    `<div class="alert alert-danger mt-2">Error: ${data.error}</div>`;
            } else if (!data.success) {
                document.getElementById('ping-results').innerHTML = 
                    `<div class="alert alert-warning mt-2">Host ${ipInput} is unreachable</div>`;
            } else {
                document.getElementById('ping-results').innerHTML = `
                    <div class="alert alert-success mt-2">
                        <h5>Ping Results for ${ipInput}</h5>
                        <pre>${data.output}</pre>
                    </div>`;
            }
        })
        .catch(error => {
            document.getElementById('ping-results').innerHTML = 
                '<div class="alert alert-danger mt-2">Error performing ping</div>';
            console.error('Error:', error);
        });
});

// System Information functionality
document.getElementById('show-system-info-btn').addEventListener('click', function() {
    fetch('/system_info')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('system-info').innerHTML = 
                    `<div class="alert alert-danger">Error: ${data.error}</div>`;
            } else {
                document.getElementById('system-info').innerHTML = `
                    <div class="card mt-3">
                        <div class="card-body">
                            <h5>Operating System</h5>
                            <ul class="list-unstyled">
                                <li><strong>Name:</strong> ${data.os.name}</li>
                                <li><strong>Version:</strong> ${data.os.version}</li>
                                <li><strong>Architecture:</strong> ${data.os.architecture}</li>
                            </ul>
                            
                            <h5>CPU</h5>
                            <ul class="list-unstyled">
                                <li><strong>Brand:</strong> ${data.cpu.brand}</li>
                                <li><strong>Cores:</strong> ${data.cpu.cores}</li>
                                <li><strong>Threads:</strong> ${data.cpu.threads}</li>
                                <li><strong>Current Usage:</strong> ${data.cpu.usage}</li>
                                <li><strong>Frequency:</strong> ${data.cpu.frequency}</li>
                            </ul>
                            
                            <h5>Memory</h5>
                            <ul class="list-unstyled">
                                <li><strong>Total:</strong> ${data.ram.total}</li>
                                <li><strong>Available:</strong> ${data.ram.available}</li>
                                <li><strong>Used:</strong> ${data.ram.used} (${data.ram.percent})</li>
                            </ul>
                            
                            <h5>Disk Information</h5>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Drive</th>
                                            <th>Total</th>
                                            <th>Used</th>
                                            <th>Free</th>
                                            <th>Usage</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.disks.map(disk => `
                                            <tr>
                                                <td>${disk.device}</td>
                                                <td>${disk.total}</td>
                                                <td>${disk.used}</td>
                                                <td>${disk.free}</td>
                                                <td>
                                                    <div class="progress">
                                                        <div class="progress-bar" role="progressbar" 
                                                             style="width: ${disk.percent};" 
                                                             aria-valuenow="${disk.percent}" 
                                                             aria-valuemin="0" 
                                                             aria-valuemax="100">
                                                            ${disk.percent}
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>`;
            }
        })
        .catch(error => {
            document.getElementById('system-info').innerHTML = 
                '<div class="alert alert-danger">Error fetching system information</div>';
            console.error('Error:', error);
        });
});
