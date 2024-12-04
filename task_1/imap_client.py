import socket
import ssl
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("imap_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IMAPClient:
    def __init__(self, server: str, port: int, username: str, password: str):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        logger.info("IMAPClient initialized with server: %s, port: %d", server, port)

    def connect(self):
        logger.info("Connecting to IMAP server: %s:%d", self.server, self.port)
        try:
            context = ssl.create_default_context()
            raw_socket = socket.create_connection((self.server, self.port))
            self.connection = context.wrap_socket(raw_socket, server_hostname=self.server)
            logger.info("Connected successfully")
            self._read_response()  # Приветственное сообщение от сервера
        except Exception as e:
            logger.error("Failed to connect to server: %s", str(e))
            raise

    def login(self):
        logger.info("Logging in as user: %s", self.username)
        command = f'a1 LOGIN {self.username} {self.password}\r\n'
        response = self._send_command(command)
        if "OK" in response:
            logger.info("Login successful")
        else:
            logger.error("Login failed: %s", response)
            raise Exception("Login failed")

    def list_mailboxes(self):
        logger.info("Listing mailboxes")
        command = 'a2 LIST "" "*"\r\n'
        response = self._send_command(command)
        mailboxes = self._parse_mailboxes(response)
        logger.info("Retrieved %d mailboxes", len(mailboxes))
        return mailboxes

    def _read_response(self):
        response = self.connection.recv(4096).decode()
        logger.debug("Server response: %s", response)
        return response

    def _send_command(self, command: str):
        logger.debug("Sending command: %s", command.strip())
        self.connection.send(command.encode())
        response = self._read_response()
        return response

    def _parse_mailboxes(self, response: str):
        mailboxes = []
        for line in response.splitlines():
            if 'LIST' in line:
                parts = line.split(' ')
                mailbox = parts[-1].strip('"')
                mailboxes.append(mailbox)
        logger.debug("Parsed mailboxes: %s", mailboxes)
        return mailboxes

    def close(self):
        if self.connection:
            logger.info("Closing connection")
            self._send_command('a3 LOGOUT\r\n')
            self.connection.close()
            logger.info("Connection closed")
