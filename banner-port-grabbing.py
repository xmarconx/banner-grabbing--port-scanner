import socket  # Ağ işlemleri / Network operations
import threading  # Çoklu işlem / Multithreading
import subprocess  # Sistem komutları / System commands
import os  # İşletim sistemi / OS operations
import sys  # Sistem çıkışı / System exit
from datetime import datetime  # Tarih saat / Date time
from concurrent.futures import ThreadPoolExecutor


# ===== Ekranı temizle ===== / Clear screen
def clear_screen():
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)


# ===== Başlangıç ===== / Start
clear_screen()

remoteServer = input("Enter a remote host to scan: ")

try:
    TARGET = socket.gethostbyname(remoteServer)
except socket.gaierror:
    print("Hostname could not be resolved. (example: google.com)")
    sys.exit()


# ===== Ayarlar ===== / Settings
SCAN_RANGE = range(1, 100)  # Tarama aralığı / Scan range
TIMEOUT = 2
OUTPUT_FILE = "report.txt"


# ===== Hızlı Port Tarama ===== / Fast port scan
def fast_scan(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((TARGET, port))
        sock.close()
        if result == 0:
            return port  # Açık port / Open port
    except:
        return None


# ===== Banner Grab ===== / Banner grabbing
def grab_banner(port):
    try:
        sock = socket.socket()
        sock.settimeout(TIMEOUT)
        sock.connect((TARGET, port))

        banner = ""

        try:
            if port == 80:
                request = (
                    f"HEAD / HTTP/1.1\r\n"
                    f"Host: {TARGET}\r\n"
                    "User-Agent: Mozilla/5.0\r\n"
                    "Connection: close\r\n\r\n"
                )
                sock.send(request.encode())

            raw_banner = sock.recv(1024).decode(errors="ignore")
            banner_lines = raw_banner.split("\n")
            banner = banner_lines[0] if banner_lines else ""
        except:
            banner = ""

        sock.close()
        return banner

    except:
        return None


# ===== Tarama Başlat ===== / Start scanning
def run_scan():
    print(f"\n[+] Target: {TARGET}")
    t1 = datetime.now()
    print(f"[+] Scan Start: {t1}\n")

    open_ports = []

    # 1️⃣ Hızlı tarama (açık portları bul)
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(fast_scan, SCAN_RANGE)

    for port in results:
        if port:
            open_ports.append(port)
            print(f"[FAST] Port {port}: Open")

    # 2️⃣ Sadece açık portlara banner grab
    final_results = []

    print("\n[+] Banner Grabbing Started\n")

    for port in open_ports:
        banner = grab_banner(port)

        if banner:
            result = f"[+] {port} OPEN -> {banner}"
        else:
            result = f"[+] {port} OPEN -> no banner"

        print(result)
        final_results.append(result)

    t2 = datetime.now()
    print(f"\n[+] Scan End: {t2}")
    print(f"[+] Total Duration: {t2 - t1}")

    return final_results


# ===== Rapor kaydet ===== / Save report
def save_report(results):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Scan Report ===\n")
        f.write(f"Target: {TARGET}\n")
        f.write(f"Date: {datetime.now()}\n\n")

        for line in results:
            f.write(line + "\n")

    print(f"\n[+] Report Saved: {OUTPUT_FILE}")


# ===== Çalıştır ===== / Run program
if __name__ == "__main__":
    results = run_scan()
    save_report(results)