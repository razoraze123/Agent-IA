"""Main application window containing navigation between modules."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from ui.clients_ui import ClientsWidget
from ui.factures_ui import FacturesWidget
from ui.ecritures_ui import EcrituresWidget


class MainWindow(QMainWindow):
    """Navigation hub for the accounting software."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mini logiciel comptable")
        self.resize(800, 600)

        self._clients_window: ClientsWidget | None = None
        self._factures_window: FacturesWidget | None = None
        self._ecritures_window: EcrituresWidget | None = None

        self._setup_ui()

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)

        title = QLabel("Bienvenue dans le mini logiciel comptable")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "Choisissez un module pour commencer à gérer vos données comptables."
        )
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        clients_button = QPushButton("Gestion des clients")
        factures_button = QPushButton("Gestion des factures")
        ecritures_button = QPushButton("Journal comptable")

        clients_button.setMinimumHeight(40)
        factures_button.setMinimumHeight(40)
        ecritures_button.setMinimumHeight(40)

        layout.addWidget(clients_button)
        layout.addWidget(factures_button)
        layout.addWidget(ecritures_button)
        layout.addStretch()

        clients_button.clicked.connect(self.open_clients_module)
        factures_button.clicked.connect(self.open_factures_module)
        ecritures_button.clicked.connect(self.open_ecritures_module)

        self.setCentralWidget(central_widget)

    # ------------------------------------------------------------------
    def _ensure_clients_window(self) -> ClientsWidget:
        if self._clients_window is None:
            self._clients_window = ClientsWidget()
        return self._clients_window

    def _ensure_factures_window(self) -> FacturesWidget:
        if self._factures_window is None:
            self._factures_window = FacturesWidget()
        return self._factures_window

    def _ensure_ecritures_window(self) -> EcrituresWidget:
        if self._ecritures_window is None:
            self._ecritures_window = EcrituresWidget()
        return self._ecritures_window

    def open_clients_module(self) -> None:
        window = self._ensure_clients_window()
        window.show()
        window.raise_()
        window.activateWindow()

    def open_factures_module(self) -> None:
        window = self._ensure_factures_window()
        window.show()
        window.raise_()
        window.activateWindow()

    def open_ecritures_module(self) -> None:
        window = self._ensure_ecritures_window()
        window.show()
        window.raise_()
        window.activateWindow()
