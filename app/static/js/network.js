// Initialize the network visualization
let network = null;
let nodes = new vis.DataSet();
let edges = new vis.DataSet();

// Configuration for the network
const options = {
    nodes: {
        shape: 'dot',
        size: 30,
        font: {
            size: 14,
            color: '#343a40'
        },
        borderWidth: 2,
        color: {
            border: '#2B7CE9',
            background: '#97C2FC'
        }
    },
    edges: {
        width: 2,
        color: {
            color: '#848484',
            highlight: '#848484',
            hover: '#848484'
        },
        smooth: {
            type: 'continuous'
        }
    },
    physics: {
        enabled: true,
        barnesHut: {
            gravitationalConstant: -2000,
            centralGravity: 0.3,
            springLength: 95,
            springConstant: 0.04,
            damping: 0.09
        }
    },
    interaction: {
        hover: true,
        tooltipDelay: 200,
        hideEdgesOnDrag: true,
        navigationButtons: true,
        keyboard: true
    }
};

// Create the network
function initNetwork() {
    const container = document.getElementById('network');
    if (!container) {
        console.error('Network container not found');
        return;
    }

    const data = {
        nodes: nodes,
        edges: edges
    };
    network = new vis.Network(container, data, options);

    // Add click event listener
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            testUserConnection(nodeId);
        }
    });

    // Load initial network data
    updateNetwork();
}

// Update the network data
function updateNetwork() {
    fetch('/get_network_users')
        .then(response => response.json())
        .then(data => {
            // Clear existing data
            nodes.clear();
            edges.clear();

            // Add nodes with improved styling
            data.nodes.forEach(node => {
                nodes.add({
                    id: node.id,
                    label: node.label,
                    title: `User: ${node.label}`,
                    color: {
                        background: node.color || '#97C2FC',
                        border: node.color === '#ff0000' ? '#cc0000' : '#2B7CE9'
                    },
                    font: {
                        color: node.color === '#ff0000' ? '#ff0000' : '#343a40'
                    },
                    size: node.size || 30
                });
            });

            // Add edges
            data.edges.forEach(edge => {
                edges.add({
                    from: edge.from,
                    to: edge.to,
                    arrows: 'to',
                    color: {
                        color: '#848484',
                        highlight: '#2B7CE9',
                        hover: '#2B7CE9'
                    },
                    width: 2
                });
            });

            // Fit the network view
            if (network && nodes.length > 0) {
                network.fit({
                    animation: {
                        duration: 1000,
                        easingFunction: 'easeInOutQuad'
                    }
                });
            }
        })
        .catch(error => console.error('Error updating network:', error));
}

// Test user connection
function testUserConnection(userId) {
    fetch(`/ping_user/${userId}`)
        .then(response => response.json())
        .then(data => {
            // Update the node color based on connection status
            const node = nodes.get(userId);
            if (node) {
                nodes.update({
                    id: userId,
                    color: {
                        background: data.success ? '#4CAF50' : '#f44336',
                        border: data.success ? '#45a049' : '#da190b'
                    }
                });
            }
        })
        .catch(error => console.error('Error testing connection:', error));
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initNetwork();
    // Update network every 30 seconds
    setInterval(updateNetwork, 30000);
});
