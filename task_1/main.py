import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget, QMessageBox
from imap_client import IMAPClient
import os

os.environ['QT_PLUGIN_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'Lib', 'site-packages',
                                            'PyQt5', 'Qt5', 'plugins')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mail_viewer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MailViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMAP Mail Viewer")
        self.resize(600, 400)
        logger.info("MailViewer initialized")

        # Создаем интерфейс
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Список для отображения папок
        self.folder_list = QListWidget()
        self.layout.addWidget(self.folder_list)

        # Подключаем IMAP клиент
        self.imap_client = IMAPClient("imap.mail.ru", 993, "", "")

        # Загружаем папки
        self.load_mailboxes()

    def load_mailboxes(self):
        logger.info("Loading mailboxes")
        try:
            self.imap_client.connect()
            self.imap_client.login()
            mailboxes = self.imap_client.list_mailboxes()
            self.folder_list.addItems(mailboxes)
            logger.info("Mailboxes loaded successfully")
        except Exception as e:
            logger.error("Failed to load mailboxes: %s", str(e))
            QMessageBox.critical(self, "Error", f"Failed to load mailboxes: {str(e)}")
        finally:
            self.imap_client.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MailViewer()
    viewer.show()
    logger.info("Application started")
    sys.exit(app.exec())
