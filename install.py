import os
import shutil
import tkinter as tk
from tkinter import messagebox
import subprocess

class InstallerGUI:
    def __init__(self, master):
        self.master = master
        master.title("방화벽 어플 설치 마법사")
        master.geometry("400x300")
        master.configure(bg="#f0f0f0")

        self.label = tk.Label(master, text="환영합니다! 방화벽 어플 설치 마법사를 시작합니다.", bg="#f0f0f0")
        self.label.pack(pady=20)

        self.install_button = tk.Button(master, text="설치 시작", command=self.start_installation, bg="#87cefa", fg="black")
        self.install_button.pack(pady=10)

        self.quit_button = tk.Button(master, text="취소", command=master.quit, bg="#87cefa", fg="black")
        self.quit_button.pack(pady=10)

    def start_installation(self):
        try:
            # 필요한 패키지 설치
            self.label.config(text="필요한 패키지를 설치하고 있습니다...")
            self.master.update()

            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "python3-pip", "-y"], check=True)
            subprocess.run(["pip3", "install", "scapy", "paramiko"], check=True)

            # 설치 파일들을 특정 경로로 복사
            self.label.config(text="설치 파일들을 복사 중입니다...")
            self.master.update()

            install_path = "/usr/local/my_firewall_app"
            os.makedirs(install_path, exist_ok=True)
            shutil.copy("server.py", install_path)
            shutil.copy("arp.py", install_path)

            # 실행 권한 부여
            os.chmod(os.path.join(install_path, "server.py"), 0o755)
            os.chmod(os.path.join(install_path, "arp.py"), 0o755)

            # 설치 완료 메시지
            messagebox.showinfo("설치 완료", f"방화벽 어플이 {install_path}에 성공적으로 설치되었습니다.")

            # 설치 후 자동 실행 여부 질문
            if messagebox.askyesno("설치 완료", "설치가 완료되었습니다. 서버를 지금 시작하시겠습니까?"):
                subprocess.run(["python3", os.path.join(install_path, "server.py")])

        except subprocess.CalledProcessError as e:
            messagebox.showerror("설치 오류", f"설치 중 오류가 발생했습니다: {e}")
        except Exception as e:
            messagebox.showerror("오류", f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    installer_gui = InstallerGUI(root)
    root.mainloop()

