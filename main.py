import requests
import json
import urllib.parse
import random
import time
from datetime import datetime, timedelta

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
        
        # Mengambil firstName dan isBanned jika ada
        first_name = data.get("user", {}).get("firstName", "N/A")
        is_banned = data.get("user", {}).get("isBanned")  # Ambil nilai isBanned tanpa default

        # Mengubah nilai is_banned menjadi "Yes" atau "No"
        is_banned = "Yes" if is_banned else "No" if is_banned is not None else "N/A"

        return token, balance, first_name, is_banned
    else:
        print("Error pada sync_user:", response.status_code)
        print("Response Text:", response.text)
        return None, None, None, None

def claim_bonus(token):
    url = "https://clicker-api.crashgame247.io/user/bonus/claim"
    headers = {
        "Origin": "https://clicker.crashgame247.io",
        "Referer": "https://clicker.crashgame247.io/",
        "Sec-Ch-Ua": '"Not A Brand",v="8", "Chromium",v="120", "Mises";v="120"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain,*/*",
        "Authorization": f"Bearer {token}"
    }

    response = requests.patch(url, headers=headers)
    if response.status_code == 200:
        print("Bonus claimed successfully!")
        data = response.json()
        balance = data.get("balance", {}).get("amount")
        return balance
    else:
        # Mencetak pesan kesalahan yang lebih mendetail
        print("Error pada claim_bonus:", response.status_code)
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
        "Authority": "clicker-api.crashgame247.io",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://clicker.crashgame247.io",
        "Referer": "https://clicker.crashgame247.io/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "clicks": clicks
    }

    try:
        print("Payload yang akan dikirim:", json.dumps(payload))
        
        response = requests.patch(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            print("Clicks updated successfully!")
        else:
            print("Error updating clicks. Status code:", response.status_code)
            print("Response:", response.text)
            if response.status_code == 500:
                print("Internal Server Error, silakan coba lagi nanti.")

    except Exception as e:
        print("Error:", e)

# Menjalankan fungsi dalam perulangan
last_claim_time = None  # Waktu klaim bonus terakhir
while True:
    data_check_chain = read_data_check_chain()
    token, balance, first_name, is_banned = sync_user(data_check_chain)
    
    if token:
        random_amount = random.randint(300, 800)  # Dapatkan angka acak antara 300 dan 800
        new_balance = balance + random_amount  # Tambah random_amount ke balance
        print(f"New Balance after adding random amount: {new_balance}")
        print(f"Amount added to balance: {random_amount}")  # Menampilkan jumlah yang ditambahkan

        # Perulangan untuk mencetak saldo dan informasi pengguna
        while True:
            print("Current Balance:", new_balance)  # Mencetak saldo saat ini
            print("First Name:", first_name)  # Mencetak First Name
            print("Banned:", is_banned)  # Mencetak status banned tanpa "Is"
            
            update_clicks(token, new_balance)  # Memanggil fungsi update_clicks
            
            # Hitung mundur
            for remaining in range(random_amount, 0, -1):
                print(f"Waiting for {remaining} seconds...", end='\r')
                time.sleep(1)  # Tidur selama 1 detik
                
            print()  # Tambahkan baris baru setelah hitungan mundur
            
            # Klaim bonus jika sudah 6 jam
            if last_claim_time is None or datetime.now() >= last_claim_time + timedelta(hours=6):
                balance = claim_bonus(token)
                if balance is not None:
                    new_balance = balance + random_amount  # Perbarui balance baru setelah klaim bonus
                    last_claim_time = datetime.now()  # Update waktu klaim terakhir
                else:
                    break  # Keluar dari loop jika klaim bonus gagal
            else:
                print("Bonus can only be claimed once every 6 hours.")

    time.sleep(5)  # Tunggu 5 detik sebelum memulai siklus berikutnya
