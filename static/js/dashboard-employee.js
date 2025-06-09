
document.addEventListener("DOMContentLoaded", () => {
    const scanBtn = document.getElementById("scan-btn");
    const scannerOutput = document.getElementById("scanner-output");
  
    scanBtn?.addEventListener("click", () => {
      // For MVP, simulate scanning
      const fakeTicketId = "TICKET123";
      scannerOutput.textContent = `Scanned Ticket ID: ${fakeTicketId}`;
      alert("Ticket ID " + fakeTicketId + " scanned. Contacting server...");
      
      // Later: Send to backend
      fetch('/api/assign-device/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket_id: fakeTicketId })
      })
      .then(res => res.json())
      .then(data => alert(data.message))
      .catch(err => alert("Error assigning device"));
    });
  });


  export async function joinEvent() {
    const code = document.getElementById('event-code').value;
    const res = await fetch('/join-employee-event/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ event_code: code })
    });
    const data = await res.json();
    alert(data.success ? `Joined event ID ${data.event_id}` : data.error);
  }
  
  export async function scanTicket() {
    const ticketID = document.getElementById('ticket-id').value;
    const res = await fetch('/scan-ticket/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ ticket_id: ticketID })
    });
    const data = await res.json();
    alert(data.success ? `Assigned to Device: ${data.device_id}` : data.error);
  }
  
  