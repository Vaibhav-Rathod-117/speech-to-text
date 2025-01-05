from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import json
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from googletrans import Translator
 
app = Flask(__name__)

recognizer = sr.Recognizer()
translator = Translator()

# Email configuration
# 'wnon lavf hvxj ojqe'
# SMTP_SERVER = 'smtp.gmail.com'
# SMTP_PORT = 587
# SENDER_EMAIL = input("")  
# SENDER_PASSWORD = input("") 


# Function to translate text
def translate_text(text, output_lang):
    try:
        translation = translator.translate(text, dest=output_lang)
        return translation.text
    except json.JSONDecodeError:
        return "Error: Failed to translate text. Please try again later."
    except TypeError:
        return "Error: No valid translation response received."

# Global variables to store recognized text
recognized_subject = ""
recognized_body = ""

# Function to convert speech to text
def speech_to_text(input_lang, append=False, is_subject=True):
    global recognized_subject, recognized_body

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("Listening... (will stop after 5 seconds of silence)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language=input_lang)

            if is_subject:  # If recognizing subject
                if append:  # Append to existing subject
                    recognized_subject += " " + text
                else:
                    recognized_subject = text
                print(f"Recognized Subject: {recognized_subject}")
                return recognized_subject
            else:  # If recognizing body
                if append:  # Append to existing body
                    recognized_body += " " + text
                else:
                    recognized_body = text
                print(f"Recognized Body: {recognized_body}")
                return recognized_body
        except sr.UnknownValueError:
            return "Error: Could not understand the audio."
        except sr.WaitTimeoutError:
            return "Error: No speech detected, stopping."
        except sr.RequestError as e:
            return f"Error: Could not request results from Google Speech Recognition service; {e}"

# Function to send email
# def send_email(recipient_email, subject, body_text):
#     message = MIMEMultipart()
#     message['From'] = SENDER_EMAIL
#     message['To'] = recipient_email
#     message['Subject'] = subject

def send_email(sender_email, sender_password, recipient_email, subject, body_text, attachment_path=None):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the body text
    message.attach(MIMEText(body_text, 'plain'))

    # Attach the file, if provided
    if attachment_path:
        try:
            with open(attachment_path, 'rb') as attachment_file:
                attachment = MIMEApplication(attachment_file.read())
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(attachment_path)}"'
                )
                message.attach(attachment)
        except Exception as e:
            print(f"Error attaching file: {e}")
            return jsonify({'error': 'Failed to attach file.'}), 500

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        # Connect to the server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': f'Error sending email: {str(e)}'}), 500

# Main API routes
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle sending email
@app.route('/send_email', methods=['POST'])
def handle_send_email():
    data = request.get_json()
    sender_email = data.get('senderEmail')
    sender_password = data.get('senderPassword')
    recipient_email = data.get('recipientEmail')
    subject = data.get('subject')
    body_text = data.get('bodyText')
    

    if not sender_email or not sender_password or not recipient_email:
        return jsonify({'error': 'Missing required email fields'}), 400

    try:
        send_email(sender_email, sender_password, recipient_email, subject, body_text)
    except Exception as e:
        return jsonify({'error': f'Error sending email: {str(e)}'}), 500

    return jsonify({'message': 'Email sent successfully!'})

# Route to handle file uploads separately
# @app.route('/upload_attachment', methods=['POST'])
# def upload_attachment():
#     if 'attachment' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['attachment']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#         # Specify the upload folder path
#     upload_folder = 'uploads'
#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder) 

#     # Save the file
#     attachment_path = os.path.join(upload_folder, file.filename)
#     file.save(attachment_path)

@app.route('/upload_attachment', methods=['POST'])
def upload_attachment():
    if 'file' not in request.files:
        return 'No file part', 400  # Ensure this isn't the issue

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400  # Ensure this isn't the issue

    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    attachment_path = os.path.join(upload_folder, secure_filename(file.filename))
    file.save(attachment_path)

    return jsonify({'message': f'File {file.filename} uploaded successfully', 'attachment_path': attachment_path}), 200


# Start speech recognition route
@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    data = request.json
    input_lang = data['inputLang']
    append = data.get('append', False)  # Check if we want to append the new text to previous one
    is_subject = data.get('isSubject', True)  # Determine if recognizing subject or body

    recognized_text_result = speech_to_text(input_lang, append, is_subject)

    if "Error" in recognized_text_result:
        return jsonify({'error': recognized_text_result}), 400
    else:
        return jsonify({'text': recognized_text_result})

# Stop recognition route
@app.route('/stop_recognition', methods=['POST'])
def stop_recognition():
    return jsonify({'message': 'Recognition stopped', 'recognizedSubject': recognized_subject, 'recognizedBody': recognized_body}), 200

# Translation route
@app.route('/translate', methods=['POST'])
def translate_text_route():
    data = request.json
    text = data['text']
    output_lang = data['outputLang']

    translated_text = translate_text(text, output_lang)

    if "Error" in translated_text:
        return jsonify({'error': translated_text}), 500
    else:
        return jsonify({'translated': translated_text})

# Route to handle sending email
@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    recipient_email = data['recipientEmail']
    
    # Translate subject and body before sending
    translated_subject = translate_text(recognized_subject, 'en')  
    translated_body = translate_text(recognized_body, 'en')  

    # Send email with the translated subject and body
    send_email(recipient_email, translated_subject, translated_body)
    return jsonify({'message': 'Email sent successfully!'})

if __name__ == '__main__':
    app.run(debug=True, port=5500)
