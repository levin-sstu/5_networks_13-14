import socket
import ssl
import base64
import re
import os
from email.header import decode_header

class IMAPClient:
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.sock = None
        self.ssl_sock = None

    def connect(self):
        print(f"Connecting to {self.server}:{self.port}...")
        self.sock = socket.create_connection((self.server, self.port))
        context = ssl.create_default_context()
        self.ssl_sock = context.wrap_socket(self.sock, server_hostname=self.server)
        print(self._get_response())  # Серверное приветствие

    def login(self):
        print("Logging in...")
        login_cmd = f'A001 LOGIN {self.username} {self.password}\r\n'
        self.ssl_sock.sendall(login_cmd.encode())
        print(self._get_response())  # Ответ на логин

    def list_mailboxes(self):
        print("Fetching mailbox list...")
        list_cmd = 'A002 LIST "" "*"\r\n'
        self.ssl_sock.sendall(list_cmd.encode())
        response = self._get_response()
        print(response)
        return response

    def select_mailbox(self, mailbox="INBOX"):
        print(f"Selecting mailbox: {mailbox}")
        select_cmd = f'A003 SELECT {mailbox}\r\n'
        self.ssl_sock.sendall(select_cmd.encode())
        response = self._get_response()
        print(response)
        return response

    def fetch_emails(self):
        print("Fetching email list...")
        fetch_cmd = 'A004 FETCH 1:* (FLAGS BODY[HEADER.FIELDS (SUBJECT)])\r\n'
        self.ssl_sock.sendall(fetch_cmd.encode())
        response = self._get_response()
        emails = self._parse_email_headers(response)
        print(f"Found emails: {emails}")
        return emails

    def _parse_email_headers(self, response):
        """Парсинг и декодирование заголовков писем."""
        matches = re.findall(r'SUBJECT (.+)', response)
        decoded_subjects = []
        for match in matches:
            try:
                subject, encoding = decode_header(match)[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8', errors='replace')
                decoded_subjects.append(subject)
            except Exception as e:
                decoded_subjects.append(f"Error decoding: {e}")
        return decoded_subjects

    def logout(self):
        if self.ssl_sock:
            print("Logging out...")
            logout_cmd = 'A007 LOGOUT\r\n'
            self.ssl_sock.sendall(logout_cmd.encode())
            print(self._get_response())
            self.ssl_sock.close()

    def _get_response(self):
        response = b""
        while True:
            data = self.ssl_sock.recv(4096)
            response += data
            if b"\r\n" in data:
                break
        # Используем errors='replace' для избегания ошибок
        return response.decode(errors='replace')


# Использование клиента
if __name__ == "__main__":
    IMAP_SERVER = 'imap.mail.ru'
    IMAP_PORT = 993
    USERNAME = ''
    PASSWORD = ''

    client = IMAPClient(IMAP_SERVER, IMAP_PORT, USERNAME, PASSWORD)
    try:
        client.connect()
        client.login()
        client.list_mailboxes()
        client.select_mailbox("INBOX")
        emails = client.fetch_emails()

        for idx, email in enumerate(emails, start=1):
            print(f"{idx}: {email}")
    finally:
        client.logout()
