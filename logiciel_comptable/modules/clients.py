"""Business logic related to client management."""
from __future__ import annotations

from typing import Dict, List, Optional

from utils.db_manager import db_manager


def create_client(nom: str, email: str, telephone: str, adresse: str) -> int:
    """Insert a new client and return its identifier."""

    cursor = db_manager.execute(
        """
        INSERT INTO clients (nom, email, telephone, adresse)
        VALUES (?, ?, ?, ?)
        """,
        (nom, email, telephone, adresse),
        commit=True,
    )
    return cursor.lastrowid


def update_client(
    client_id: int,
    *,
    nom: str,
    email: str,
    telephone: str,
    adresse: str,
) -> None:
    """Update client information."""

    db_manager.execute(
        """
        UPDATE clients
           SET nom = ?,
               email = ?,
               telephone = ?,
               adresse = ?
         WHERE id = ?
        """,
        (nom, email, telephone, adresse, client_id),
        commit=True,
    )


def delete_client(client_id: int) -> None:
    """Delete a client from the database."""

    db_manager.execute(
        "DELETE FROM clients WHERE id = ?",
        (client_id,),
        commit=True,
    )


def get_all_clients() -> List[Dict[str, Optional[str]]]:
    """Return all clients ordered alphabetically by name."""

    rows = db_manager.execute(
        "SELECT id, nom, email, telephone, adresse FROM clients ORDER BY nom",
        fetchall=True,
    )
    return [dict(row) for row in rows]


def get_client(client_id: int) -> Optional[Dict[str, Optional[str]]]:
    """Retrieve a single client by its identifier."""

    row = db_manager.execute(
        "SELECT id, nom, email, telephone, adresse FROM clients WHERE id = ?",
        (client_id,),
        fetchone=True,
    )
    return dict(row) if row else None
