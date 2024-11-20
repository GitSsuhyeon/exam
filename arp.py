import scapy.all as scapy
import argparse
import paramiko

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', dest='target', help='Target IP Address/Adresses')
    parser.add_argument('-c', '--command', dest='command', help='Command to execute on the target host (SSH)')
    options = parser.parse_args()

    if not options.target:
        parser.error("[-] Please specify an IP Address or Addresses, use --help for more info.")
    if not options.command:
        parser.error("[-] Please specify a command to execute, use --help for more info.")
    return options

def scan(ip):
    arp_req_frame = scapy.ARP(pdst=ip)
    broadcast_ether_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame
    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout=1, verbose=False)[0]
    result = []
    for i in range(0, len(answered_list)):
        if answered_list[i][1].psrc not in ["192.168.226.254", "192.168.226.2","192.168.226.136","192.168.226.1"]:  # 제외할 IP 주소를 여기에 추가
            client_dict = {"ip": answered_list[i][1].psrc, "mac": answered_list[i][1].hwsrc}
            result.append(client_dict)
    return result

def execute_command_ssh(ip, username, password, command):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        print(f"\n[*] Output from {ip}:\n{output}")
        ssh_client.close()
    except paramiko.AuthenticationException:
        print(f"\n[-] Failed to authenticate with {ip}. Check username and password.")
    except paramiko.SSHException as e:
        print(f"\n[-] SSH error occurred while connecting to {ip}: {e}")
    except Exception as e:
        print(f"\n[-] An error occurred while connecting to {ip}: {e}")

options = get_args()
scanned_output = scan(options.target)

for host in scanned_output:
    print(f"\n[*] Executing command on {host['ip']}...")
    execute_command_ssh(host["ip"], "user", "1111", options.command)
