// Calibration page JavaScript
const API_BASE = '';

// DOM elements
let dutyCycleDisplay;
let pulseDurationDisplay;
let messageDiv;

// Button elements
let dutyDecreaseLargeBtn;
let dutyDecreaseBtn;
let dutyIncreaseBtn;
let dutyIncreaseLargeBtn;
let durationDecreaseBtn;
let durationIncreaseBtn;
let testBtn;
let saveBtn;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    dutyCycleDisplay = document.getElementById('duty-cycle-value');
    pulseDurationDisplay = document.getElementById('pulse-duration-value');
    messageDiv = document.getElementById('message');
    
    // Duty cycle buttons
    dutyDecreaseLargeBtn = document.getElementById('duty-decrease-large');
    dutyDecreaseBtn = document.getElementById('duty-decrease');
    dutyIncreaseBtn = document.getElementById('duty-increase');
    dutyIncreaseLargeBtn = document.getElementById('duty-increase-large');
    
    // Pulse duration buttons
    durationDecreaseBtn = document.getElementById('duration-decrease');
    durationIncreaseBtn = document.getElementById('duration-increase');
    
    // Action buttons
    testBtn = document.getElementById('test-btn');
    saveBtn = document.getElementById('save-btn');
    
    // Attach event listeners
    dutyDecreaseLargeBtn.addEventListener('click', () => adjustDutyCycle(10));
    dutyDecreaseBtn.addEventListener('click', () => adjustDutyCycle(1));
    dutyIncreaseBtn.addEventListener('click', () => adjustDutyCycle(-1));
    dutyIncreaseLargeBtn.addEventListener('click', () => adjustDutyCycle(-10));
    
    durationDecreaseBtn.addEventListener('click', () => adjustPulseDuration(-5));
    durationIncreaseBtn.addEventListener('click', () => adjustPulseDuration(5));
    
    testBtn.addEventListener('click', testCalibration);
    saveBtn.addEventListener('click', saveCalibration);
    
    // Load current calibration values
    loadCalibration();
});

// Load current calibration from backend
async function loadCalibration() {
    try {
        const response = await fetch(`${API_BASE}/api/calibration/get`);
        if (!response.ok) {
            throw new Error('Failed to load calibration');
        }
        const data = await response.json();
        dutyCycleDisplay.textContent = data.duty_cycle;
        pulseDurationDisplay.textContent = data.pulse_duration;
    } catch (error) {
        console.error('Error loading calibration:', error);
        showMessage('Error loading calibration values', 'error');
    }
}

// Adjust duty cycle by increment
async function adjustDutyCycle(increment) {
    disableAllButtons();
    try {
        const response = await fetch(`${API_BASE}/api/calibration/adjust_duty`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ increment: increment })
        });
        
        if (!response.ok) {
            throw new Error('Failed to adjust duty cycle');
        }
        
        const data = await response.json();
        dutyCycleDisplay.textContent = data.duty_cycle;
        pulseDurationDisplay.textContent = data.pulse_duration;
        showMessage(`Duty cycle adjusted to ${data.duty_cycle}`, 'success');
    } catch (error) {
        console.error('Error adjusting duty cycle:', error);
        showMessage('Error adjusting duty cycle', 'error');
    } finally {
        enableAllButtons();
    }
}

// Adjust pulse duration by increment
async function adjustPulseDuration(increment) {
    disableAllButtons();
    try {
        const response = await fetch(`${API_BASE}/api/calibration/adjust_duration`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ increment: increment })
        });
        
        if (!response.ok) {
            throw new Error('Failed to adjust pulse duration');
        }
        
        const data = await response.json();
        dutyCycleDisplay.textContent = data.duty_cycle;
        pulseDurationDisplay.textContent = data.pulse_duration;
        showMessage(`Pulse duration adjusted to ${data.pulse_duration}ms`, 'success');
    } catch (error) {
        console.error('Error adjusting pulse duration:', error);
        showMessage('Error adjusting pulse duration', 'error');
    } finally {
        enableAllButtons();
    }
}

// Test current calibration
async function testCalibration() {
    disableAllButtons();
    testBtn.textContent = 'Testing...';
    try {
        const response = await fetch(`${API_BASE}/api/calibration/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error('Failed to test calibration');
        }
        
        const data = await response.json();
        if (data.success) {
            showMessage(`Test successful! Duty: ${data.duty_cycle}, Duration: ${data.pulse_duration}ms`, 'success');
        } else {
            showMessage('Test failed: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error testing calibration:', error);
        showMessage('Error testing calibration', 'error');
    } finally {
        testBtn.textContent = 'Test';
        enableAllButtons();
    }
}

// Save current calibration
async function saveCalibration() {
    disableAllButtons();
    saveBtn.textContent = 'Saving...';
    try {
        const dutyCycle = parseInt(dutyCycleDisplay.textContent);
        const pulseDuration = parseInt(pulseDurationDisplay.textContent);
        
        const response = await fetch(`${API_BASE}/api/calibration/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duty_cycle: dutyCycle,
                pulse_duration: pulseDuration
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to save calibration');
        }
        
        const data = await response.json();
        showMessage(`Calibration saved successfully! Duty: ${data.duty_cycle}, Duration: ${data.pulse_duration}ms`, 'success');
    } catch (error) {
        console.error('Error saving calibration:', error);
        showMessage('Error saving calibration', 'error');
    } finally {
        saveBtn.textContent = 'Save';
        enableAllButtons();
    }
}

// Display message to user
function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = 'message ' + type;
    messageDiv.style.display = 'block';
    
    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    }
}

// Disable all buttons during operations
function disableAllButtons() {
    dutyDecreaseLargeBtn.disabled = true;
    dutyDecreaseBtn.disabled = true;
    dutyIncreaseBtn.disabled = true;
    dutyIncreaseLargeBtn.disabled = true;
    durationDecreaseBtn.disabled = true;
    durationIncreaseBtn.disabled = true;
    testBtn.disabled = true;
    saveBtn.disabled = true;
}

// Enable all buttons after operations
function enableAllButtons() {
    dutyDecreaseLargeBtn.disabled = false;
    dutyDecreaseBtn.disabled = false;
    dutyIncreaseBtn.disabled = false;
    dutyIncreaseLargeBtn.disabled = false;
    durationDecreaseBtn.disabled = false;
    durationIncreaseBtn.disabled = false;
    testBtn.disabled = false;
    saveBtn.disabled = false;
}
