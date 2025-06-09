// QR code scanner for employee

window.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('scan-btn');
  const output = document.getElementById('scanner-output');
  const readerElem = document.getElementById('qr-reader');
  let scanner;

  function onScanSuccess(decodedText) {
    output.textContent = `Scanned Ticket ID: ${decodedText}`;
    scanner.stop().then(() => {
      fetch('/scan-ticket/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket_id: decodedText })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            alert(`Assigned to Device: ${data.device_id}`);
          } else {
            alert(data.error);
          }
        })
        .catch(() => alert('Error contacting server'));
    });
  }

  btn?.addEventListener('click', () => {
    btn.disabled = true;
    readerElem.style.display = 'block';
    scanner = new Html5Qrcode('qr-reader');
    scanner.start({ facingMode: 'environment' }, { fps: 10, qrbox: 250 }, onScanSuccess)
      .catch(err => {
        console.error(err);
        output.textContent = 'Unable to start scanner';
      });
  });
});
