"""Graphical interface for accounting entries."""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from modules import ecritures as ecritures_module


class EcrituresTableModel(QAbstractTableModel):
    """Table model displaying accounting entries."""

    headers = [
        "ID",
        "Date",
        "Libellé",
        "Compte débit",
        "Compte crédit",
        "Montant",
    ]

    def __init__(self, ecritures: Optional[List[dict]] = None) -> None:
        super().__init__()
        self._ecritures: List[dict] = ecritures or []

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._ecritures)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not (0 <= index.row() < len(self._ecritures)):
            return None

        ecriture = self._ecritures[index.row()]
        keys = ["id", "date_ecriture", "libelle", "compte_debit", "compte_credit", "montant"]

        if role == Qt.DisplayRole:
            value = ecriture.get(keys[index.column()], "")
            if keys[index.column()] == "montant" and isinstance(value, (int, float)):
                return f"{value:.2f} €"
            return value
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def update_ecritures(self, ecritures: List[dict]) -> None:
        self.beginResetModel()
        self._ecritures = ecritures
        self.endResetModel()


class EcrituresWidget(QWidget):
    """Widget used to create and list accounting entries."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Journal comptable")
        self.table_model = EcrituresTableModel([])

        self._setup_ui()
        self.refresh_table()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("Journal des écritures")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(title)

        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table_view)

        form_layout = QFormLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.libelle_edit = QLineEdit()
        self.compte_debit_edit = QLineEdit()
        self.compte_credit_edit = QLineEdit()

        self.montant_spin = QDoubleSpinBox()
        self.montant_spin.setMaximum(1_000_000_000)
        self.montant_spin.setDecimals(2)
        self.montant_spin.setPrefix("€ ")

        form_layout.addRow("Date", self.date_edit)
        form_layout.addRow("Libellé", self.libelle_edit)
        form_layout.addRow("Compte débit", self.compte_debit_edit)
        form_layout.addRow("Compte crédit", self.compte_credit_edit)
        form_layout.addRow("Montant", self.montant_spin)
        main_layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Ajouter l'écriture")
        self.refresh_button = QPushButton("Rafraîchir")

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.refresh_button)
        main_layout.addLayout(buttons_layout)

        self.create_button.clicked.connect(self._create_entry)
        self.refresh_button.clicked.connect(self.refresh_table)

    def refresh_table(self) -> None:
        ecritures = ecritures_module.get_all_entries()
        self.table_model.update_ecritures(ecritures)
        self.table_view.resizeColumnsToContents()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.refresh_table()

    def _validate_form(self) -> bool:
        if not self.libelle_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le libellé est obligatoire.")
            return False
        if not self.compte_debit_edit.text().strip() or not self.compte_credit_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Les comptes débit et crédit sont obligatoires.")
            return False
        if self.montant_spin.value() <= 0:
            QMessageBox.warning(self, "Validation", "Le montant doit être supérieur à zéro.")
            return False
        return True

    def _create_entry(self) -> None:
        if not self._validate_form():
            return

        ecritures_module.create_entry(
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.libelle_edit.text().strip(),
            self.compte_debit_edit.text().strip(),
            self.compte_credit_edit.text().strip(),
            self.montant_spin.value(),
        )
        self.refresh_table()
        self._clear_form()
        QMessageBox.information(self, "Écriture", "L'écriture a été enregistrée.")

    def _clear_form(self) -> None:
        self.libelle_edit.clear()
        self.compte_debit_edit.clear()
        self.compte_credit_edit.clear()
        self.montant_spin.setValue(0.0)
