const webcam = document.getElementById('webcam');
const statusPill = document.getElementById('status-pill');
let lastAlert = 0;

// Start Webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { webcam.srcObject = stream; });

// Simple Logic: If no motion is detected or you leave the frame
function checkFocus() {
    // In a full version, we'd send the image to Python here
    // For now, let's simulate the connection
    let currentStatus = "focus"; 
    
    // Logic to update UI
    if (currentStatus === "focus") {
        statusPill.className = "pill focus";
        statusPill.innerText = "FOCUSING";
    } else {
        statusPill.className = "pill warning";
        statusPill.innerText = currentStatus.toUpperCase();
        
        // Tell Python to play the voice
        fetch('/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status: currentStatus, mode: "asian_mom"})
        });
    }
}

setInterval(checkFocus, 3000); // Check every 3 seconds