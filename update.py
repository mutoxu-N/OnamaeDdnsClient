from dns import resolver
import os
import socket
import ssl
import requests
import json
import time


def log(message):
    with open("log.txt", "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")


def main():
    # get current ip
    req = requests.get("https://inet-ip.info/ip")
    current_ip = req.text

    # ログイン
    update = False

    for fqdn in config["FQDNs"]:
        host, domain = fqdn["host"], fqdn["domain"]

        # get dns ip
        dns_ip = resolver.resolve(
            f"{host}.{domain}", "A").response.answer[0][0].address

        if dns_ip != current_ip:
            update = True
            log(f"UPDATE: {host}.{domain} {dns_ip} -> {current_ip}")

            msg = "LOGIN\n"
            msg += f"USERID: {config['user_id']}\n"
            msg += f"PASSWORD: {config['password']}\n"
            msg += ".\n"

            msg += "MODIP\n"
            msg += f"HOSTNAME: {host.encode('idna').decode()}\n"
            msg += f"DOMNAME: {domain.encode('idna').decode()}\n"
            msg += f"IPV4: {current_ip}\n"
            msg += ".\n"

            # 送信
            msg += "LOGOUT\n"
            msg += ".\n"

            try:
                context = ssl.create_default_context()
                with socket.create_connection(('ddnsclient.onamae.com', 65010), timeout=15) as sock, \
                        context.wrap_socket(sock, server_hostname='ddnsclient.onamae.com') as ssl_sock:
                    ssl_sock.sendall(msg.encode())

                    buffer = bytearray()
                    while True:
                        data = ssl_sock.recv(1024)
                        buffer += data
                        if not data:
                            break
                    print("--- sended ---")
                    print(msg)
                    print("--- received ---")
                    print(buffer.decode())
            except:
                log(f"ERROR: {host}.{domain} {dns_ip} -> {current_ip}")

    if not update:
        log(f"NOT UPDATED (IP:{current_ip})")
        return


if __name__ == "__main__":
    if not os.path.isfile("log.txt"):
        with open("log.txt", "w") as f:
            pass

    # load config
    with open("config.json", "r") as f:
        config = json.load(f)

    main()
