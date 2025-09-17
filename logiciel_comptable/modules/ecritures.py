"""Business logic to handle accounting journal entries."""
from __future__ import annotations

from typing import Dict, List

from utils.db_manager import db_manager


def create_entry(
    date_ecriture: str,
    libelle: str,
    compte_debit: str,
    compte_credit: str,
    montant: float,
) -> int:
    """Insert a new accounting entry and return its identifier."""

    cursor = db_manager.execute(
        """
        INSERT INTO ecritures (date_ecriture, libelle, compte_debit, compte_credit, montant)
        VALUES (?, ?, ?, ?, ?)
        """,
        (date_ecriture, libelle, compte_debit, compte_credit, montant),
        commit=True,
    )
    return cursor.lastrowid


def get_all_entries() -> List[Dict[str, str]]:
    """Return all accounting entries ordered by date descending."""

    rows = db_manager.execute(
        """
        SELECT id, date_ecriture, libelle, compte_debit, compte_credit, montant
          FROM ecritures
         ORDER BY date_ecriture DESC, id DESC
        """,
        fetchall=True,
    )
    return [dict(row) for row in rows]
