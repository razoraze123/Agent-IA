"""Graphical interface for invoices."""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from modules import clients as clients_module
from modules import factures as factures_module


def _format_currency(value: float) -> str:
    """Format monetary values using a French-style notation."""

    formatted = f"{value:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} €"


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
            if keys[index.column()] in {"montant_ht", "montant_ttc"} and isinstance(
                value, (int, float)
            ):
                return _format_currency(float(value))
            if keys[index.column()] == "taux_tva" and isinstance(value, (int, float)):
                return f"{value:.2f} %"
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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        form_card = QFrame()
        form_card.setObjectName("invoiceFormCard")
        form_card.setStyleSheet(
            """
            #invoiceFormCard {
                background-color: #f7f8fb;
                border: 1px solid #e0e0e5;
                border-radius: 12px;
            }
            """
        )
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(14)

        label_style = "color: #5c5c66; font-weight: 600;"

        client_label = QLabel("Client")
        client_label.setStyleSheet(label_style)
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(220)

        date_label = QLabel("Date")
        date_label.setStyleSheet(label_style)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())

        montant_label = QLabel("Montant HT")
        montant_label.setStyleSheet(label_style)
        self.montant_ht_spin = QDoubleSpinBox()
        self.montant_ht_spin.setMaximum(1_000_000_000)
        self.montant_ht_spin.setDecimals(2)
        self.montant_ht_spin.setSuffix(" €")
        self.montant_ht_spin.setAlignment(Qt.AlignRight)
        self.montant_ht_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.montant_ht_spin.setSingleStep(10.0)

        tva_label = QLabel("TVA")
        tva_label.setStyleSheet(label_style)
        self.tva_spin = QDoubleSpinBox()
        self.tva_spin.setMaximum(1000)
        self.tva_spin.setDecimals(2)
        self.tva_spin.setSuffix(" %")
        self.tva_spin.setValue(20.0)
        self.tva_spin.setAlignment(Qt.AlignRight)
        self.tva_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)

        ttc_title = QLabel("Montant TTC")
        ttc_title.setStyleSheet(label_style)
        self.ttc_label = QLabel(_format_currency(0.0))
        self.ttc_label.setStyleSheet(
            "font-size: 18px; font-weight: 600; color: #1f1f24;"
        )

        self.paid_checkbox = QCheckBox("Payée")

        self.create_button = QPushButton("Créer facture")
        self.create_button.setMinimumHeight(40)
        self.create_button.setCursor(Qt.PointingHandCursor)

        form_layout.addWidget(client_label, 0, 0)
        form_layout.addWidget(self.client_combo, 0, 1)
        form_layout.addWidget(date_label, 0, 2)
        form_layout.addWidget(self.date_edit, 0, 3)

        form_layout.addWidget(montant_label, 1, 0)
        form_layout.addWidget(self.montant_ht_spin, 1, 1)
        form_layout.addWidget(tva_label, 1, 2)
        form_layout.addWidget(self.tva_spin, 1, 3)

        form_layout.addWidget(ttc_title, 2, 0)
        form_layout.addWidget(self.ttc_label, 2, 1)
        form_layout.addWidget(self.paid_checkbox, 2, 2)
        form_layout.addWidget(self.create_button, 2, 3)

        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(3, 1)

        main_layout.addWidget(form_card)

        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setStyleSheet(
            """
            QTableView {
                border: 1px solid #e0e0e5;
                border-radius: 12px;
                gridline-color: #dadade;
                alternate-background-color: #f7f8fb;
            }
            QTableView::item:selected {
                background-color: rgba(52, 120, 246, 0.18);
                color: #1f1f24;
            }
            """
        )
        self.table_view.verticalHeader().setVisible(False)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setHighlightSections(False)
        self.table_view.setColumnHidden(0, True)
        self.table_view.setColumnHidden(3, True)
        self.table_view.setColumnHidden(4, True)
        self.table_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        main_layout.addWidget(self.table_view, 1)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(12)
        footer_layout.addStretch(1)

        self.edit_button = QPushButton("Modifier…")
        self.delete_button = QPushButton("Supprimer")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setCursor(Qt.PointingHandCursor)

        footer_layout.addWidget(self.edit_button)
        footer_layout.addWidget(self.delete_button)
        main_layout.addLayout(footer_layout)

        self.create_button.clicked.connect(self._create_invoice)
        self.edit_button.clicked.connect(self._edit_invoice)
        self.delete_button.clicked.connect(self._delete_invoice)
        self.montant_ht_spin.valueChanged.connect(self._update_ttc_display)
        self.tva_spin.valueChanged.connect(self._update_ttc_display)

    # ------------------------------------------------------------------
    def refresh_clients(self) -> None:
        clients = clients_module.get_all_clients()
        self.client_combo.clear()
        self.client_combo.addItem("Sélectionner…", None)
        for client in clients:
            self.client_combo.addItem(client.get("nom", ""), client.get("id"))
        self.client_combo.setCurrentIndex(0)

    def refresh_table(self) -> None:
        factures = factures_module.get_all_invoices()
        self.table_model.update_factures(factures)
        selection_model = self.table_view.selectionModel()
        if selection_model:
            selection_model.clearSelection()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
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
        has_selection = facture is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
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
        self.paid_checkbox.setChecked(
            facture.get("statut") == factures_module.STATUT_PAYEE
        )
        self._update_ttc_display()

    def _update_ttc_display(self) -> None:
        montant_ht = self.montant_ht_spin.value()
        tva = self.tva_spin.value()
        montant_ttc = montant_ht * (1 + tva / 100)
        self.ttc_label.setText(_format_currency(montant_ttc))

    # ------------------------------------------------------------------
    def _validate_form(self) -> bool:
        if self.client_combo.count() <= 1:
            QMessageBox.warning(self, "Validation", "Veuillez créer un client avant d'émettre une facture.")
            return False
        if self.client_combo.currentData() is None:
            QMessageBox.warning(self, "Validation", "Sélectionnez un client pour la facture.")
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
        statut = (
            factures_module.STATUT_PAYEE
            if self.paid_checkbox.isChecked()
            else factures_module.STATUT_EN_ATTENTE
        )

        factures_module.create_invoice(
            client_id, date_facture, montant_ht, tva, statut
        )
        self.refresh_table()
        self.montant_ht_spin.setValue(0.0)
        self.paid_checkbox.setChecked(False)
        QMessageBox.information(self, "Facture", "La facture a été créée avec succès.")

    def _edit_invoice(self) -> None:
        facture = self._get_selected_facture()
        if not facture:
            QMessageBox.information(self, "Facture", "Sélectionnez une facture à modifier.")
            return
        if not self._validate_form():
            return

        statut = (
            factures_module.STATUT_PAYEE
            if self.paid_checkbox.isChecked()
            else factures_module.STATUT_EN_ATTENTE
        )

        factures_module.update_invoice(
            facture["id"],
            self.client_combo.currentData(),
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.montant_ht_spin.value(),
            self.tva_spin.value(),
            statut,
        )
        self.refresh_table()
        QMessageBox.information(self, "Facture", "La facture a été mise à jour.")

    def _delete_invoice(self) -> None:
        facture = self._get_selected_facture()
        if not facture:
            QMessageBox.information(self, "Facture", "Sélectionnez une facture à supprimer.")
            return

        confirmation = QMessageBox.question(
            self,
            "Suppression",
            "Supprimer la facture sélectionnée ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            factures_module.delete_invoice(facture["id"])
            self.refresh_table()
