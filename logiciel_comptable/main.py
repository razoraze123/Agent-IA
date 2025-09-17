"""Entry point of the mini accounting application."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils import db_manager as db_module


def main() -> int:
    """Start the Qt event loop and show the main window."""

    # Ensure the database is initialised before launching the UI.
    _ = db_module.db_manager

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
