// Translate recognized subject
document.getElementById('translateBtn').addEventListener('click', () => {
    const subjectText = document.getElementById('recognizedSubject').value;
    const bodyText = document.getElementById('recognizedBody').value;
    const outputLang = document.getElementById('outputLang').value;

    // Translate subject
    fetch('/translate', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: subjectText,
            outputLang: outputLang
        })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('translatedSubject').value = data.translated;
      });

    // Translate body
    fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: bodyText,
            outputLang: outputLang
        })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('translatedBody').value = data.translated;
      });
});

// Recognize Email Subject
document.getElementById('speakSubjectBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: false,  // Start fresh for the subject
            isSubject: true
        })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('recognizedSubject').value = data.text;
      });
});

// Continue Recognizing Email Subject (Append new speech)
document.getElementById('continueSubjectBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: true,  // Append new text to the existing subject
            isSubject: true
        })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('recognizedSubject').value = data.text;
      });
});

// Recognize Email Body
document.getElementById('speakBodyBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: false,  // Start fresh for the body
            isSubject: false
        })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('recognizedBody').value = data.text;
      });
});

// Continue Recognizing Email Body (Append new speech)
document.getElementById('continueBodyBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: true,  // Append new text to the existing body
            isSubject: false
        })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('recognizedBody').value = data.text;
      });
});

// Stop recognition manually
document.getElementById('stopBtn').addEventListener('click', () => {
    fetch('/stop_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }).then(response => response.json())
      .then(data => {
          // Handle the recognized text or any other action
          document.getElementById('recognizedSubject').value = data.recognizedSubject;
          document.getElementById('recognizedBody').value = data.recognizedBody; // Use the recognized body
      });
});

// Send Email with Subject and Body
// document.getElementById('sendEmailBtn').addEventListener('click', () => {
//     const recipientEmail = document.getElementById('recipientEmail').value;
    
//     // Use recognized text directly as the subject and body.
//     const subject = document.getElementById('translatedSubject').value; // Use translated subject
//     const bodyText = document.getElementById('translatedBody').value; // Use translated body

//     fetch('/send_email', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//             recipientEmail: recipientEmail,
//             subject: subject,
//             bodyText: bodyText
//         })
//     }).then(response => response.json())
//       .then(data => {
//           alert(data.message);  // Show success message
//       });
// });

// Send Email with Translated Subject and Body
// Function to send email without using FormData
document.getElementById('sendEmailBtn').addEventListener('click', () => {
    const senderEmail = document.getElementById('senderEmail').value;
    const senderPassword = document.getElementById('senderpassword').value;
    const recipientEmail = document.getElementById('recipientEmail').value;
    const subject = document.getElementById('translatedSubject').value;
    const bodyText = document.getElementById('translatedBody').value;
    const attachmentPath = document.getElementById('attachment').files[0] ? '/uploads/' + document.getElementById('attachment').files[0].name : null;

    fetch('/send_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            senderEmail: senderEmail,
            senderPassword: senderPassword,
            recipientEmail: recipientEmail,
            subject: subject,
            bodyText: bodyText,
            attachmentPath: attachmentPath
        })
    }).then(response => response.json())
      .then(data => {
          alert(data.message || data.error);
      }).catch(error => {
          console.error('Error:', error);
      });
});


// Function to upload a file separately
// document.getElementById('attachment').addEventListener('change', () => {
//     const file = document.getElementById('attachment').files[0];
//     if (file) {
//         const formData = new FormData();
//         formData.append('attachment', file);

//         fetch('/upload_attachment', {
//             method: 'POST',
//             body: formData
//         }).then(response => response.json())
//           .then(data => {
//               alert(data.message || data.error);
//           }).catch(error => {
//               console.error('Error:', error);
//           });
//     }
// });

document.getElementById('uploadBtn').addEventListener('click', function() {
    const fileInput = document.getElementById('attachment');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload_attachment', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to upload file');
            }
            return response.text();
        })
        .then(data => {
            console.log(data);
            alert('File uploaded successfully!');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error uploading file');
        });
    } else {
        alert('No file selected');
    }
});