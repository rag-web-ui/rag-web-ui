import logging
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple

from alembic.config import Config
from alembic.config import main as alembic_main
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """
    Database migrator class
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.alembic_cfg = self._get_alembic_config()
        self.max_retries = 30
        self.retry_delay_seconds = 2

    @contextmanager
    def database_connection(self) -> Generator[Connection, None, None]:
        """
        Context manager for database connections with timeout

        Yields:
            SQLAlchemy connection object
        """
        engine = create_engine(
            self.db_url, connect_args={"connect_timeout": 3}  # 设置连接超时为3秒
        )
        try:
            with engine.connect() as connection:
                yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

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
            return True, current_rev or "None", "head"

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
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                # Check if migration is needed
                needs_migration, current_rev, head_rev = self.check_migration_needed()

                if needs_migration:
                    logger.info(
                        f"Current revision: {current_rev}, upgrading to: {head_rev}"
                    )
                    self.alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)

                    # 执行 alembic 升级
                    alembic_main(
                        argv=["--raiseerr", "upgrade", "head"], config=self.alembic_cfg
                    )

                    logger.info("Database migrations completed successfully")
                else:
                    logger.info(
                        f"Database is already at the latest version: {current_rev}"
                    )
                return
            except Exception as e:
                last_error = e
                logger.warning(
                    "Database is not ready yet (attempt %s/%s): %s",
                    attempt,
                    self.max_retries,
                    e,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_seconds)

        logger.error("Error during database migration after retries: %s", last_error)
        raise RuntimeError("Database migration failed after retries") from last_error
