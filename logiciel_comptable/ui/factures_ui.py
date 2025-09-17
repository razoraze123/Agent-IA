"""Graphical interface for invoices."""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from modules import clients as clients_module
from modules import factures as factures_module


class FacturesTableModel(QAbstractTableModel):
    """Model used to display invoices."""

    headers = [
        "ID",
        "Client",
        "Date",
        "Montant HT",
        "TVA (%)",
        "Montant TTC",
        "Statut",
    ]

    def __init__(self, factures: Optional[List[dict]] = None) -> None:
        super().__init__()
        self._factures: List[dict] = factures or []

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._factures)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not (0 <= index.row() < len(self._factures)):
            return None

        facture = self._factures[index.row()]
        keys = ["id", "client", "date_facture", "montant_ht", "taux_tva", "montant_ttc", "statut"]

        if role == Qt.DisplayRole:
            value = facture.get(keys[index.column()], "")
            if keys[index.column()] in {"montant_ht", "montant_ttc"} and isinstance(value, (int, float)):
                return f"{value:.2f} €"
            if keys[index.column()] == "taux_tva" and isinstance(value, (int, float)):
                return f"{value:.2f}"
            return value
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def update_factures(self, factures: List[dict]) -> None:
        self.beginResetModel()
        self._factures = factures
        self.endResetModel()

    def facture_at(self, row: int) -> Optional[dict]:
        if 0 <= row < len(self._factures):
            return self._factures[row]
        return None


class FacturesWidget(QWidget):
    """Widget used to create and list invoices."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gestion des factures")
        self.table_model = FacturesTableModel([])

        self._setup_ui()
        self.refresh_clients()
        self.refresh_table()

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("Factures")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(title)

        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table_view)

        form_layout = QFormLayout()
        self.client_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.montant_ht_spin = QDoubleSpinBox()
        self.montant_ht_spin.setMaximum(1_000_000_000)
        self.montant_ht_spin.setDecimals(2)
        self.montant_ht_spin.setPrefix("€ ")

        self.tva_spin = QDoubleSpinBox()
        self.tva_spin.setMaximum(1000)
        self.tva_spin.setDecimals(2)
        self.tva_spin.setValue(20.0)

        self.ttc_label = QLabel("€ 0.00")

        form_layout.addRow("Client", self.client_combo)
        form_layout.addRow("Date", self.date_edit)
        form_layout.addRow("Montant HT", self.montant_ht_spin)
        form_layout.addRow("TVA (%)", self.tva_spin)
        form_layout.addRow("Montant TTC", self.ttc_label)
        main_layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Créer la facture")
        self.paid_button = QPushButton("Marquer payée")
        self.pending_button = QPushButton("Marquer en attente")
        self.refresh_button = QPushButton("Rafraîchir")

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.paid_button)
        buttons_layout.addWidget(self.pending_button)
        buttons_layout.addWidget(self.refresh_button)
        main_layout.addLayout(buttons_layout)

        self.create_button.clicked.connect(self._create_invoice)
        self.paid_button.clicked.connect(lambda: self._update_status(factures_module.STATUT_PAYEE))
        self.pending_button.clicked.connect(lambda: self._update_status(factures_module.STATUT_EN_ATTENTE))
        self.refresh_button.clicked.connect(self.refresh_table)

        self.montant_ht_spin.valueChanged.connect(self._update_ttc_display)
        self.tva_spin.valueChanged.connect(self._update_ttc_display)

    # ------------------------------------------------------------------
    def refresh_clients(self) -> None:
        clients = clients_module.get_all_clients()
        self.client_combo.clear()
        for client in clients:
            self.client_combo.addItem(client.get("nom", ""), client.get("id"))

    def refresh_table(self) -> None:
        factures = factures_module.get_all_invoices()
        self.table_model.update_factures(factures)
        self.table_view.resizeColumnsToContents()
        self._update_ttc_display()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.refresh_clients()
        self.refresh_table()

    # ------------------------------------------------------------------
    def _get_selected_facture(self) -> Optional[dict]:
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.table_model.facture_at(indexes[0].row())

    def _on_selection_changed(self, *_) -> None:
        facture = self._get_selected_facture()
        if not facture:
            return

        # Fill the form with the selected invoice
        index = self.client_combo.findData(facture.get("client_id"))
        if index >= 0:
            self.client_combo.setCurrentIndex(index)
        date_value = QDate.fromString(facture.get("date_facture", ""), "yyyy-MM-dd")
        if date_value.isValid():
            self.date_edit.setDate(date_value)
        montant_ht = facture.get("montant_ht") or 0
        taux_tva = facture.get("taux_tva") or 0
        self.montant_ht_spin.setValue(float(montant_ht))
        self.tva_spin.setValue(float(taux_tva))
        self._update_ttc_display()

    def _update_ttc_display(self) -> None:
        montant_ht = self.montant_ht_spin.value()
        tva = self.tva_spin.value()
        montant_ttc = montant_ht * (1 + tva / 100)
        self.ttc_label.setText(f"€ {montant_ttc:.2f}")

    # ------------------------------------------------------------------
    def _validate_form(self) -> bool:
        if self.client_combo.count() == 0:
            QMessageBox.warning(self, "Validation", "Veuillez créer un client avant d'émettre une facture.")
            return False
        if self.montant_ht_spin.value() <= 0:
            QMessageBox.warning(self, "Validation", "Le montant HT doit être supérieur à zéro.")
            return False
        return True

    def _create_invoice(self) -> None:
        if not self._validate_form():
            return

        client_id = self.client_combo.currentData()
        date_facture = self.date_edit.date().toString("yyyy-MM-dd")
        montant_ht = self.montant_ht_spin.value()
        tva = self.tva_spin.value()

        factures_module.create_invoice(client_id, date_facture, montant_ht, tva)
        self.refresh_table()
        QMessageBox.information(self, "Facture", "La facture a été créée avec succès.")

    def _update_status(self, statut: str) -> None:
        facture = self._get_selected_facture()
        if not facture:
            QMessageBox.information(self, "Facture", "Sélectionnez une facture dans la liste.")
            return

        factures_module.update_invoice_status(facture["id"], statut)
        self.refresh_table()
