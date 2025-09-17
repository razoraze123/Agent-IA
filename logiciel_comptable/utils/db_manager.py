"""Utility module providing access to the SQLite database.

This module exposes a :class:`DBManager` class offering a small helper API to
initialise the application database and to execute SQL queries.  A single
instance named :data:`db_manager` is created so the rest of the code base can
share the same connection easily.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any, Iterable, Optional


class DBManager:
    """Small wrapper around :mod:`sqlite3`.

    The manager keeps a persistent connection to the database file.  It also
    ensures the schema exists on start-up and exposes a convenience
    :meth:`execute` method to run SQL statements in a concise fashion.
    """

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self._connection: Optional[sqlite3.Connection] = None
        self.initialize_database()

    # ------------------------------------------------------------------
    # Connection handling
    def get_connection(self) -> sqlite3.Connection:
        """Return an open SQLite connection.

        The first call opens the database and activates foreign key support.
        Subsequent calls reuse the same connection object.
        """

        if self._connection is None:
            self._connection = sqlite3.connect(self.database_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self) -> None:
        """Close the current connection if it exists."""

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    # ------------------------------------------------------------------
    # Schema setup
    def initialize_database(self) -> None:
        """Create database tables when they are missing."""

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT,
                telephone TEXT,
                adresse TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date_facture TEXT NOT NULL,
                montant_ht REAL NOT NULL,
                taux_tva REAL NOT NULL,
                montant_ttc REAL NOT NULL,
                statut TEXT NOT NULL DEFAULT 'En attente',
                FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ecritures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_ecriture TEXT NOT NULL,
                libelle TEXT NOT NULL,
                compte_debit TEXT NOT NULL,
                compte_credit TEXT NOT NULL,
                montant REAL NOT NULL
            )
            """
        )

        conn.commit()

    # ------------------------------------------------------------------
    # Query execution helper
    def execute(
        self,
        query: str,
        parameters: Iterable[Any] | None = None,
        *,
        fetchone: bool = False,
        fetchall: bool = False,
        commit: bool = False,
    ) -> Any:
        """Execute a SQL query and optionally fetch results.

        Parameters
        ----------
        query:
            The SQL statement to execute.
        parameters:
            Positional parameters passed to :meth:`sqlite3.Cursor.execute`.
        fetchone / fetchall:
            Toggle fetching a single row or a list of rows.  When both are
            ``False`` the raw cursor is returned.
        commit:
            When ``True`` the transaction is committed after execution.
        """

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(parameters or ()))

        if commit:
            conn.commit()

        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return cursor


# Expose a shared manager for the whole application.
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "database.db"
db_manager = DBManager(DB_PATH)
