// Load header and footer components
async function loadComponent(componentId, filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`Failed to load ${filePath}`);
        }
        const html = await response.text();
        document.getElementById(componentId).innerHTML = html;
    } catch (error) {
        console.error(`Error loading component: ${error.message}`);
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', async () => {
    // Load header and footer
    await loadComponent('header-container', 'components/header.html');
    await loadComponent('footer-container', 'components/footer.html');
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Check backend connection
    checkConnection();
});

// Initialize all event listeners
function initializeEventListeners() {
    // Feed Now button
    const feedNowBtn = document.getElementById('feedNowBtn');
    if (feedNowBtn) {
        feedNowBtn.addEventListener('click', handleFeedNow);
    }
    
    // Set Schedule button
    const setScheduleBtn = document.getElementById('setScheduleBtn');
    if (setScheduleBtn) {
        setScheduleBtn.addEventListener('click', handleSetSchedule);
    }
    
    // Set Quantity button
    const setQuantityBtn = document.getElementById('setQuantityBtn');
    if (setQuantityBtn) {
        setQuantityBtn.addEventListener('click', handleSetQuantity);
    }
    
    // Smooth scrolling for Quick Links
    document.querySelectorAll('.quick-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// Handle Feed Now button click
async function handleFeedNow() {
    const btn = document.getElementById('feedNowBtn');
    const originalText = btn.textContent;
    
    try {
        btn.textContent = 'Feeding...';
        btn.disabled = true;
        
        const response = await fetch('/api/feed', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            alert('Feeding successful! Fed at: ' + new Date().toLocaleString());
            updateLastFed();
        } else {
            throw new Error('Failed to feed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to feed. Please check the connection.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Handle Set Schedule button click
async function handleSetSchedule() {
    const feedTime = document.getElementById('feedTime').value;
    const feedAmount = document.getElementById('feedAmount').value;
    
    if (!feedTime) {
        alert('Please select a feed time');
        return;
    }
    
    try {
        const response = await fetch('/api/schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                time: feedTime,
                amount: parseInt(feedAmount)
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            alert('Schedule set successfully!');
            loadSchedules();
            updateNextFeed(feedTime);
        } else {
            throw new Error('Failed to set schedule');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to set schedule. Please check the connection.');
    }
}

// Load and display schedules
async function loadSchedules() {
    try {
        const response = await fetch('/api/schedules');
        if (response.ok) {
            const schedules = await response.json();
            displaySchedules(schedules);
        }
    } catch (error) {
        console.error('Error loading schedules:', error);
    }
}

// Display schedules in the list
function displaySchedules(schedules) {
    const scheduleList = document.getElementById('scheduleList');
    
    if (!schedules || schedules.length === 0) {
        scheduleList.innerHTML = '<p class="text-muted">No schedules set</p>';
        return;
    }
    
    scheduleList.innerHTML = schedules.map(schedule => `
        <div class="schedule-item">
            <div class="schedule-item-info">
                <span>⏰ ${schedule.time}</span>
                <span>🐟 ${schedule.amount}g</span>
            </div>
            <button class="btn btn-danger" onclick="deleteSchedule('${schedule.id}')">Delete</button>
        </div>
    `).join('');
}

// Delete a schedule
async function deleteSchedule(scheduleId) {
    if (!confirm('Are you sure you want to delete this schedule?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/schedule/${scheduleId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Schedule deleted successfully!');
            loadSchedules();
        } else {
            throw new Error('Failed to delete schedule');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete schedule. Please check the connection.');
    }
}

// Check backend connection
async function checkConnection() {
    const statusElement = document.getElementById('connectionStatus');
    
    try {
        const response = await fetch('/api/status', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            statusElement.textContent = 'Online';
            statusElement.className = 'status-value status-online';
            
            // Load existing data
            loadSchedules();
        } else {
            throw new Error('Connection failed');
        }
    } catch (error) {
        console.error('Connection error:', error);
        statusElement.textContent = 'Offline';
        statusElement.className = 'status-value status-offline';
    }
    
    // Check connection every 30 seconds
    setTimeout(checkConnection, 30000);
}

// Handle Set Quantity button click
async function handleSetQuantity() {
    const defaultQuantity = document.getElementById('defaultQuantity').value;
    
    if (!defaultQuantity || defaultQuantity < 1) {
        alert('Please enter a valid quantity');
        return;
    }
    
    try {
        const response = await fetch('/api/quantity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quantity: parseInt(defaultQuantity)
            })
        });
        
        if (response.ok) {
            alert('Default quantity updated successfully!');
        } else {
            throw new Error('Failed to update quantity');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update quantity. Please check the connection.');
    }
}

// Update last fed time
function updateLastFed() {
    const lastFedElement = document.getElementById('lastFed');
    const now = new Date();
    const options = { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true };
    lastFedElement.textContent = `Last fed on ${now.toLocaleDateString('en-US', options)}`;
}

// Update next feed time
function updateNextFeed(feedTime) {
    const nextFeedElement = document.getElementById('nextFeed');
    const today = new Date();
    const [hours, minutes] = feedTime.split(':');
    const feedDate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), hours, minutes);
    
    // If the time has passed today, show tomorrow's time
    if (feedDate < today) {
        feedDate.setDate(feedDate.getDate() + 1);
    }
    
    nextFeedElement.textContent = feedDate.toLocaleString();
}

// Update feed remaining
function updateFeedRemaining(count) {
    const feedRemainingElement = document.getElementById('feedRemaining');
    feedRemainingElement.textContent = `${count} more feed remaining`;
}

// Update battery status
function updateBatteryStatus(percentage) {
    const batteryStatusElement = document.getElementById('batteryStatus');
    batteryStatusElement.textContent = `${percentage}% of the Battery remaining`;
}
