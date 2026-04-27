"""
Database configuration and connection pool management.
"""
import os
import logging
import mysql.connector
from mysql.connector import pooling

logger = logging.getLogger(__name__)

# ── Connection defaults (override via environment variables) ────────────────
DB_CONFIG: dict = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", "Challenge@897"),
    "database": os.getenv("DB_NAME",     "gambling_app"),
    "charset":  "utf8mb4",
    "use_pure": True,
    "connection_timeout": 10,
}


class DatabaseConfig:
    """Manages a MySQL connection pool and schema bootstrap."""

    _pool: pooling.MySQLConnectionPool | None = None

    # ── Pool ────────────────────────────────────────────────────────────────
    @classmethod
    def _init_pool(cls) -> pooling.MySQLConnectionPool:
        if cls._pool is None:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="gambling_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG,
            )
            logger.info("MySQL connection pool initialised (size=5).")
        return cls._pool

    @classmethod
    def get_connection(cls) -> mysql.connector.MySQLConnection:
        """Return a connection from the pool."""
        try:
            return cls._init_pool().get_connection()
        except mysql.connector.Error as exc:
            logger.error("Failed to obtain DB connection: %s", exc)
            raise DatabaseConnectionError(str(exc)) from exc

    # ── Schema bootstrap ────────────────────────────────────────────────────
    @classmethod
    def initialize_schema(cls) -> None:
        """
        Create the database (if absent) and run schema.sql.
        Connects WITHOUT specifying the database first so we can CREATE it.
        """
        no_db_cfg = {
            k: v for k, v in DB_CONFIG.items()
            if k not in ("database", "connection_timeout")
        }
        conn = mysql.connector.connect(**no_db_cfg)
        cursor = conn.cursor()
        try:
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__)
                ))),
                "sql", "schema.sql",
            )
            with open(schema_path, "r") as fh:
                raw_sql = fh.read()

            # Strip single-line comments then split on ";"
            lines = [
                ln for ln in raw_sql.splitlines()
                if not ln.strip().startswith("--")
            ]
            statements = [s.strip() for s in " ".join(lines).split(";")]

            for stmt in statements:
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
            logger.info("Schema initialised successfully.")
        except Exception as exc:
            conn.rollback()
            logger.error("Schema initialisation failed: %s", exc)
            raise
        finally:
            cursor.close()
            conn.close()

    # ── Health check ────────────────────────────────────────────────────────
    @classmethod
    def test_connection(cls) -> bool:
        try:
            conn = cls.get_connection()
            conn.close()
            return True
        except Exception:
            return False


class DatabaseConnectionError(Exception):
    """Raised when the application cannot reach MySQL."""
