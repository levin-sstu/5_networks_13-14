import socket
import ssl
import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QListWidget
import os

os.environ['QT_PLUGIN_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'Lib', 'site-packages',
                                            'PyQt5', 'Qt5', 'plugins')


class IMAPClient:
    def __init__(self, server, port, username, password, use_ssl=True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.sock = None

    def connect(self):
        raw_socket = socket.create_connection((self.server, self.port))
        if self.use_ssl:
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(raw_socket, server_hostname=self.server)
        else:
            self.sock = raw_socket
        self._get_response()  # Read initial server greeting

    def login(self):
        self._send_command(f'LOGIN {self.username} {self.password}')
        self._get_response()

    def get_mailboxes(self):
        self._send_command('LIST "" "*"')
        response = self._get_response()
        return [line.split(' "/" ')[-1].strip('"') for line in response if 'LIST' in line]

    def select_mailbox(self, mailbox):
        self._send_command(f'SELECT {mailbox}')
        self._get_response()

    def fetch_contacts(self):
        self._send_command('FETCH 1:* (BODY[HEADER.FIELDS (FROM)])')
        response = self._get_response()
        contacts = set(re.findall(r'From: .*<([^>]+)>', "\n".join(response)))
        return sorted(contacts)

    def _send_command(self, command):
        tag = "A0001"
        self.sock.sendall(f"{tag} {command}\r\n".encode('utf-8'))

    def _get_response(self):
        data = b""
        while True:
            chunk = self.sock.recv(4096)
            data += chunk
            if b'\r\n' in chunk:
                break
        return data.decode('utf-8').split("\r\n")

    def logout(self):
        self._send_command('LOGOUT')
        self.sock.close()

class IMAPApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMAP Contacts Viewer")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.label = QLabel("Contacts:")
        self.list_widget = QListWidget()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Initialize IMAP client
        self.imap_client = IMAPClient(
            server='imap.mail.ru',
            port=993,
            username='',
            password=''
        )
        self.fetch_and_display_contacts()

    def fetch_and_display_contacts(self):
        try:
            self.imap_client.connect()
            self.imap_client.login()
            self.imap_client.select_mailbox("INBOX")
            contacts = self.imap_client.fetch_contacts()
            self.list_widget.addItems(contacts)
        except Exception as e:
            self.label.setText(f"Error: {e}")
        finally:
            self.imap_client.logout()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IMAPApp()
    window.show()
    sys.exit(app.exec())
