"""Main application window containing navigation between modules."""
from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from ui.clients_ui import ClientsWidget
from ui.factures_ui import FacturesWidget
from ui.ecritures_ui import EcrituresWidget


class MainWindow(QMainWindow):
    """Navigation hub for the accounting software."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mini logiciel comptable")
        self.resize(1040, 680)

        self._stacked_widget: QStackedWidget | None = None
        self._module_title: QLabel | None = None
        self._nav_buttons: Dict[str, QPushButton] = {}

        self._clients_widget = ClientsWidget()
        self._factures_widget = FacturesWidget()
        self._ecritures_widget = EcrituresWidget()

        self._setup_ui()
        self._set_active_module("factures")

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        central_widget = QWidget()
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        content = self._create_content_area()

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content, 1)

        self.setCentralWidget(central_widget)

    # ------------------------------------------------------------------
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            """
            #sidebar {
                background-color: #f2f2f7;
                border-right: 1px solid #dcdde1;
            }
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        logo = QLabel("Mini logiciel\ncomptable")
        logo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        logo.setStyleSheet("font-size: 18px; font-weight: 600; color: #1f1f24;")
        layout.addWidget(logo)

        layout.addSpacing(12)

        self._nav_buttons["clients"] = self._create_nav_button(
            "Clients", self.style().standardIcon(QStyle.SP_FileIcon)
        )
        self._nav_buttons["factures"] = self._create_nav_button(
            "Factures", self.style().standardIcon(QStyle.SP_DriveHDIcon)
        )
        self._nav_buttons["ecritures"] = self._create_nav_button(
            "Comptabilité", self.style().standardIcon(QStyle.SP_ComputerIcon)
        )
        self._nav_buttons["quit"] = self._create_nav_button(
            "Quitter", self.style().standardIcon(QStyle.SP_DialogCloseButton)
        )

        for key in ("clients", "factures", "ecritures"):
            layout.addWidget(self._nav_buttons[key])

        layout.addStretch(1)
        layout.addWidget(self._nav_buttons["quit"])

        self._nav_buttons["clients"].clicked.connect(
            lambda: self._set_active_module("clients")
        )
        self._nav_buttons["factures"].clicked.connect(
            lambda: self._set_active_module("factures")
        )
        self._nav_buttons["ecritures"].clicked.connect(
            lambda: self._set_active_module("ecritures")
        )
        self._nav_buttons["quit"].clicked.connect(self._quit_application)

        return sidebar

    def _create_nav_button(self, text: str, icon: QIcon) -> QPushButton:
        button = QPushButton(text)
        button.setCheckable(True)
        button.setIcon(icon)
        button.setIconSize(QSize(22, 22))
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(42)
        button.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                padding: 10px 14px;
                border-radius: 10px;
                font-size: 15px;
                color: #2f2f35;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(52, 120, 246, 0.08);
            }
            QPushButton:checked {
                background-color: #3478f6;
                color: white;
            }
            QPushButton:checked:hover {
                background-color: #2967d1;
            }
            """
        )
        return button

    # ------------------------------------------------------------------
    def _create_content_area(self) -> QWidget:
        container = QWidget()
        container.setObjectName("contentArea")
        container.setStyleSheet(
            "#contentArea { background-color: white; }"
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(18)

        title = QLabel("Mini logiciel comptable")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 600; color: #1c1c21;")
        layout.addWidget(title)

        self._module_title = QLabel()
        self._module_title.setStyleSheet(
            "font-size: 19px; font-weight: 600; color: #2b2b30;"
        )
        layout.addWidget(self._module_title)

        self._stacked_widget = QStackedWidget()
        self._stacked_widget.addWidget(self._factures_widget)
        self._stacked_widget.addWidget(self._clients_widget)
        self._stacked_widget.addWidget(self._ecritures_widget)
        layout.addWidget(self._stacked_widget, 1)

        return container

    # ------------------------------------------------------------------
    def _set_active_module(self, module: str) -> None:
        if not self._stacked_widget or not self._module_title:
            return

        mapping = {
            "factures": (self._factures_widget, "Factures"),
            "clients": (self._clients_widget, "Clients"),
            "ecritures": (self._ecritures_widget, "Comptabilité"),
        }

        widget, title = mapping.get(module, (self._factures_widget, "Factures"))
        self._stacked_widget.setCurrentWidget(widget)
        self._module_title.setText(title)

        for key, button in self._nav_buttons.items():
            button.setChecked(key == module)

    # ------------------------------------------------------------------
    def _quit_application(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.quit()
