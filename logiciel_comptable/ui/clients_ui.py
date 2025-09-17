"""Graphical interface for client management."""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
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

from modules import clients as clients_module


class ClientsTableModel(QAbstractTableModel):
    """Table model exposing client records to a :class:`QTableView`."""

    headers = ["ID", "Nom", "Email", "Téléphone", "Adresse"]

    def __init__(self, clients: Optional[List[dict]] = None) -> None:
        super().__init__()
        self._clients: List[dict] = clients or []

    # ------------------------------------------------------------------
    # Model interface
    def rowCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._clients)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not (0 <= index.row() < len(self._clients)):
            return None

        client = self._clients[index.row()]

        if role in (Qt.DisplayRole, Qt.EditRole):
            column_key = ["id", "nom", "email", "telephone", "adresse"][index.column()]
            return client.get(column_key, "")

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    # ------------------------------------------------------------------
    # Helpers
    def update_clients(self, clients: List[dict]) -> None:
        self.beginResetModel()
        self._clients = clients
        self.endResetModel()

    def client_at(self, row: int) -> Optional[dict]:
        if 0 <= row < len(self._clients):
            return self._clients[row]
        return None


class ClientsWidget(QWidget):
    """Widget embedding all client management tools."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gestion des clients")
        self.table_model = ClientsTableModel([])

        self._setup_ui()
        self.refresh_table()

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("Clients enregistrés")
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
        self.nom_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.telephone_edit = QLineEdit()
        self.adresse_edit = QLineEdit()

        form_layout.addRow("Nom", self.nom_edit)
        form_layout.addRow("Email", self.email_edit)
        form_layout.addRow("Téléphone", self.telephone_edit)
        form_layout.addRow("Adresse", self.adresse_edit)
        main_layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter")
        self.update_button = QPushButton("Modifier")
        self.delete_button = QPushButton("Supprimer")
        self.clear_button = QPushButton("Vider le formulaire")

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)

        self.add_button.clicked.connect(self._create_client)
        self.update_button.clicked.connect(self._update_client)
        self.delete_button.clicked.connect(self._delete_client)
        self.clear_button.clicked.connect(self._clear_form)

    # ------------------------------------------------------------------
    def refresh_table(self) -> None:
        clients = clients_module.get_all_clients()
        self.table_model.update_clients(clients)
        self.table_view.resizeColumnsToContents()

    # ------------------------------------------------------------------
    def _get_selected_client(self) -> Optional[dict]:
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.table_model.client_at(indexes[0].row())

    def _on_selection_changed(self, *_) -> None:
        client = self._get_selected_client()
        if not client:
            return

        self.nom_edit.setText(client.get("nom", ""))
        self.email_edit.setText(client.get("email", ""))
        self.telephone_edit.setText(client.get("telephone", ""))
        self.adresse_edit.setText(client.get("adresse", ""))

    # ------------------------------------------------------------------
    def _validate_form(self) -> bool:
        if not self.nom_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom du client est obligatoire.")
            return False
        return True

    def _clear_form(self) -> None:
        self.nom_edit.clear()
        self.email_edit.clear()
        self.telephone_edit.clear()
        self.adresse_edit.clear()
        self.table_view.clearSelection()

    # ------------------------------------------------------------------
    def _create_client(self) -> None:
        if not self._validate_form():
            return

        clients_module.create_client(
            self.nom_edit.text().strip(),
            self.email_edit.text().strip(),
            self.telephone_edit.text().strip(),
            self.adresse_edit.text().strip(),
        )
        self.refresh_table()
        self._clear_form()

    def _update_client(self) -> None:
        client = self._get_selected_client()
        if not client:
            QMessageBox.information(self, "Modification", "Sélectionnez un client à modifier.")
            return
        if not self._validate_form():
            return

        clients_module.update_client(
            client["id"],
            nom=self.nom_edit.text().strip(),
            email=self.email_edit.text().strip(),
            telephone=self.telephone_edit.text().strip(),
            adresse=self.adresse_edit.text().strip(),
        )
        self.refresh_table()
        self._clear_form()

    def _delete_client(self) -> None:
        client = self._get_selected_client()
        if not client:
            QMessageBox.information(self, "Suppression", "Sélectionnez un client à supprimer.")
            return

        confirmation = QMessageBox.question(
            self,
            "Suppression",
            "Supprimer le client sélectionné ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            clients_module.delete_client(client["id"])
            self.refresh_table()
            self._clear_form()
