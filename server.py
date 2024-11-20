
import socket
import subprocess
import tkinter as tk
from tkinter import scrolledtext

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("네트워크 침입 차단 프로그램")

        self.log_text = scrolledtext.ScrolledText(master, width=60, height=15)
        self.log_text.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.start_button = tk.Button(master, text="서버 시작", command=self.start_server)
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(master, text="서버 중지", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=1, padx=10, pady=10)

        self.server_socket = None
        self.running = False

    def start_server(self):
        self.log_text.insert(tk.END, "서버가 시작되었습니다.\n")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.running = True
        self.run_server()

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
        self.running = False
        self.log_text.insert(tk.END, "서버가 중지되었습니다.\n")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_server(self):
        host = '0.0.0.0'
        port = 12345

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

        self.log_text.insert(tk.END, f"서버가 {host}:{port}에서 실행 중입니다...\n")

        # 비동기적으로 클라이언트 접속을 처리하기 위해 after() 메서드 사용
        self.master.after(100, self.accept_clients)

    def accept_clients(self):
        if not self.running:
            return

        try:
            client_socket, client_address = self.server_socket.accept()
            self.log_text.insert(tk.END, f"클라이언트 {client_address}와 연결되었습니다.\n")

            with client_socket:
                data = client_socket.recv(1024)
                if data:
                    received_message = data.decode().strip()
                    self.log_text.insert(tk.END, f"받은 메시지: {received_message}\n")

                    if received_message != "알람 서버 연결 테스트":
                        try:
                            subprocess.run(["python3", "arp.py", "-t", "192.168.226.0/24", "-c", "sudo iptables -P INPUT DROP"])
                            response = "서버로부터의 응답 메시지"
                        except Exception as e:
                            response = f"오류 발생: {str(e)}"
                        client_socket.sendall(response.encode())
                    else:
                        client_socket.sendall("알람 서버 연결 테스트에 성공했습니다.".encode())
        except Exception as e:
            self.log_text.insert(tk.END, f"오류 발생: {str(e)}\n")

        # 다음 클라이언트 접속을 위해 다시 after() 메서드 호출
        if self.running:
            self.master.after(100, self.accept_clients)
        else:
            self.server_socket.close()

# Tkinter 애플리케이션 실행
if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()
