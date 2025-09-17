"""Business logic related to invoice management."""
from __future__ import annotations

from typing import Dict, List, Optional

from utils.db_manager import db_manager


STATUT_EN_ATTENTE = "En attente"
STATUT_PAYEE = "Payée"


def create_invoice(
    client_id: int,
    date_facture: str,
    montant_ht: float,
    taux_tva: float,
) -> int:
    """Create a new invoice and return its identifier."""

    montant_ttc = montant_ht * (1 + taux_tva / 100)
    cursor = db_manager.execute(
        """
        INSERT INTO factures (client_id, date_facture, montant_ht, taux_tva, montant_ttc, statut)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (client_id, date_facture, montant_ht, taux_tva, montant_ttc, STATUT_EN_ATTENTE),
        commit=True,
    )
    return cursor.lastrowid


def update_invoice_status(invoice_id: int, statut: str) -> None:
    """Update the status of an invoice."""

    db_manager.execute(
        "UPDATE factures SET statut = ? WHERE id = ?",
        (statut, invoice_id),
        commit=True,
    )


def get_all_invoices() -> List[Dict[str, Optional[str]]]:
    """Return the list of invoices including the related client name."""

    rows = db_manager.execute(
        """
        SELECT f.id,
               f.client_id,
               c.nom AS client,
               f.date_facture,
               f.montant_ht,
               f.taux_tva,
               f.montant_ttc,
               f.statut
          FROM factures AS f
          JOIN clients AS c ON c.id = f.client_id
         ORDER BY f.date_facture DESC, f.id DESC
        """,
        fetchall=True,
    )
    return [dict(row) for row in rows]


def get_invoice(invoice_id: int) -> Optional[Dict[str, Optional[str]]]:
    """Return a single invoice by its identifier."""

    row = db_manager.execute(
        """
        SELECT f.id,
               f.client_id,
               f.date_facture,
               f.montant_ht,
               f.taux_tva,
               f.montant_ttc,
               f.statut
          FROM factures AS f
         WHERE f.id = ?
        """,
        (invoice_id,),
        fetchone=True,
    )
    return dict(row) if row else None
