import requests
import json
import urllib.parse
import random
import time
import shutil  # Import for terminal size
from datetime import datetime, timedelta

class Colors:
    RESET = "\033[0m"
    DARK_BLUE = "\033[94m"  # Warna biru tua
    GREEN = "\033[92m"      # Warna hijau
    RED = "\033[91m"        # Warna merah
    YELLOW = "\033[93m"     # Warna kuning

def print_pattern():
    terminal_size = shutil.get_terminal_size()
    width = terminal_size.columns

    pattern = [
        "█████████  ██████████    ██████      ████████  ████████    ██      ██  ██     ██",
        "██      ██     ██       ██    ██   ██          ██      ██  ██      ██  ██    ██",
        "██      ██     ██      ██      ██  ██          ██      ██  ██      ██  ██   ██",
        "█████████      ██      ██      ██  ██████████  ██      ██  ██      ██  ██████",
        "██             ██      ██████████          ██  ██      ██  ██      ██  ██   ██",
        "██             ██      ██      ██          ██  ██      ██  ██      ██  ██    ██",
        "██             ██  ██  ██      ██  ████████    ████████      ██████    ██     ██"
    ]

    # Adjust the pattern to fit the terminal width
    for line in pattern:
        print(Colors.DARK_BLUE + line.center(width) + Colors.RESET)

# Menampilkan pola di awal
print_pattern()

def read_data_check_chain():
    with open('data.txt', 'r') as file:
        return file.read().strip()

def sync_user(data_check_chain):
    url = "https://clicker-api.crashgame247.io/user/sync"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }

    decoded_data = urllib.parse.unquote(data_check_chain)
    params = dict(item.split("=") for item in decoded_data.split("&"))
    user_data = json.loads(params["user"])

    init_data = {
        "query_id": params["query_id"],
        "user": user_data,
        "auth_date": params["auth_date"],
        "hash": params["hash"]
    }

    payload = {
        "dataCheckChain": data_check_chain,
        "initData": init_data
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        balance = data.get("balance", {}).get("amount")

        first_name = data.get("user", {}).get("firstName", "N/A")
        is_banned = data.get("user", {}).get("isBanned")
        is_banned = "Yes" if is_banned else "No" if is_banned is not None else "N/A"

        return token, balance, first_name, is_banned
    else:
        print(Colors.RED + "Error pada sync_user: " + str(response.status_code) + Colors.RESET)
        print("Response Text:", response.text)
        return None, None, None, None

def claim_bonus(token):
    url = "https://clicker-api.crashgame247.io/user/bonus/claim"
    headers = {
        "Origin": "https://clicker.crashgame247.io",
        "Referer": "https://clicker.crashgame247.io/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain,*/*",
        "Authorization": f"Bearer {token}"
    }

    response = requests.patch(url, headers=headers)
    if response.status_code == 200:
        print(Colors.GREEN + "Bonus claimed successfully!" + Colors.RESET)
        data = response.json()
        balance = data.get("balance", {}).get("amount")
        return balance
    else:
        print(Colors.RED + "Error pada claim_bonus: " + str(response.status_code) + Colors.RESET)
        try:
            error_data = response.json()
            print("Error Message:", error_data.get("message", "No error message provided"))
        except json.JSONDecodeError:
            print("Response text:", response.text)
        
        if response.status_code == 500:
            print("Internal Server Error, silakan coba lagi nanti.")
        return None

def update_clicks(token, clicks):
    url = "https://clicker-api.crashgame247.io/meta/clicker"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "clicks": clicks
    }

    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            print("Clicks updated successfully!")
        else:
            print(Colors.RED + "Error updating clicks. Status code: " + str(response.status_code) + Colors.RESET)
            print("Response:", response.text)
            if response.status_code == 500:
                print("Internal Server Error, silakan coba lagi nanti.")

    except Exception as e:
        print(Colors.RED + "Error: " + str(e) + Colors.RESET)

# Menjalankan fungsi dalam perulangan
last_claim_time = None  # Waktu klaim bonus terakhir
while True:
    data_check_chain = read_data_check_chain()
    token, balance, first_name, is_banned = sync_user(data_check_chain)
    
    if token:
        random_amount = random.randint(300, 800)
        new_balance = balance + random_amount
        print(f"\n{Colors.YELLOW}New Balance after adding random amount: {new_balance}{Colors.RESET}")
        print(f"{Colors.YELLOW}Amount added to balance: {random_amount}{Colors.RESET}")

        while True:
            token, balance, first_name, is_banned = sync_user(data_check_chain)
            new_balance = balance + random_amount
            
            print("\n" + Colors.GREEN + "Current Balance: " + str(new_balance) + Colors.RESET)
            print(Colors.GREEN + "First Name: " + first_name + Colors.RESET)
            print(Colors.GREEN + "Banned: " + is_banned + Colors.RESET)
            
            update_clicks(token, new_balance)

            for remaining in range(random_amount, 0, -1):
                print(f"Waiting for {remaining} seconds...", end='\r')
                time.sleep(1)
                
            print()  # Tambahkan baris baru setelah hitungan mundur
            
            if last_claim_time is None or datetime.now() >= last_claim_time + timedelta(hours=6):
                balance = claim_bonus(token)
                if balance is not None:
                    new_balance = balance + random_amount
                    last_claim_time = datetime.now()
                else:
                    break
            else:
                print(Colors.YELLOW + "Bonus can only be claimed once every 6 hours." + Colors.RESET)

    time.sleep(5)
