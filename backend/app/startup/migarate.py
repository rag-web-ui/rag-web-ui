import logging
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DatabaseError, OperationalError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """
    Database migrator class
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.alembic_cfg = self._get_alembic_config()

    @contextmanager
    def database_connection(self, timeout: int = 3) -> Generator[Connection, None, None]:
        """
        Context manager for database connections

        Yields:
            SQLAlchemy connection object
        """
        engine = create_engine(self.db_url, connect_args={"connect_timeout": timeout})
        try:
            with engine.connect() as connection:
                yield connection
        except (OperationalError, DatabaseError) as e:
            logger.error(f"Database connection error: {e}")
            raise

    def wait_for_db(self, max_retries: int = 30, retry_interval: int = 3, timeout: int = 3) -> bool:
        """
        Wait for database to be ready

        Args:
            max_retries (int): Maximum number of retries
            retry_interval (int): Interval between retries in seconds

        Returns:
            bool: True if database is ready, False otherwise
        """
        for i in range(max_retries):
            try:
                with self.database_connection(timeout=timeout):
                    logger.info("Database is ready!")
                    return True
            except OperationalError:
                logger.error(f"Database not ready, waiting... ({i+1}/{max_retries})")
                time.sleep(retry_interval)
        return False

    def check_migration_needed(self) -> Tuple[bool, str, str]:
        """
        Check if database migration is needed

        Returns:
            Tuple containing:
                - bool: Whether migration is needed
                - str: Current revision
                - str: Head revision
        """
        with self.database_connection() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            heads = context.get_current_heads()

        if not heads:
            logger.warning("No migration heads found. Database might not be initialized.")
            return True, current_rev or "None", "No heads found"

        head_rev = heads[0]
        return current_rev != head_rev, current_rev or "None", head_rev

    def _get_alembic_config(self) -> Config:
        """
        Create and configure Alembic config

        Returns:
            Alembic config object
        """
        project_root = Path(__file__).resolve().parents[2]  # Go up 3 levels from migrate.py
        alembic_cfg = Config(project_root / "alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)
        return alembic_cfg

    def run_migrations(self) -> None:
        """
        Run database migrations if needed

        Raises:
            Exception: If migration fails
        """
        try:
            # First wait for database to be ready
            self.wait_for_db()

            # Check if migration is needed
            needs_migration, current_rev, head_rev = self.check_migration_needed()

            if needs_migration:
                logger.info(f"Current revision: {current_rev}, upgrading to: {head_rev}")
                command.upgrade(self.alembic_cfg, "head")
                logger.info("Database migrations completed successfully")
            else:
                logger.info("Database is already at the latest version")

        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            raise
