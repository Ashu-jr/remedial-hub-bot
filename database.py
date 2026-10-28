"""Database management module for Remedial Hub Telegram Bot.

Provides asynchronous SQLite database operations using aiosqlite, including
table initialization, student registration CRUD, statistics calculation,
user tracking for broadcasts, and student record exports.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiosqlite

from config import config

logger = logging.getLogger(__name__)


class Database:
    """Async SQLite Database manager."""

    def __init__(self, db_path: str = config.DB_NAME) -> None:
        self.db_path = db_path

    async def init_db(self) -> None:
        """Initialize SQLite database tables and indexes."""
        async with aiosqlite.connect(self.db_path) as db:
            # Table to track all users who interacted with the bot (for broadcast reach)
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Table for remedial student registrations
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT NOT NULL,
                    stream TEXT NOT NULL,
                    bank TEXT NOT NULL,
                    file_id TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    invite_link TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Indexes for faster queries
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_students_status ON students(status)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_students_stream ON students(stream)"
            )
            await db.commit()
            logger.info("Database initialized successfully at '%s'", self.db_path)

    async def record_user(
        self, user_id: int, username: Optional[str] = None, full_name: Optional[str] = None
    ) -> None:
        """Record or update basic user profile on interaction."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = COALESCE(excluded.username, users.username),
                    full_name = COALESCE(excluded.full_name, users.full_name)
                """,
                (user_id, username, full_name),
            )
            await db.commit()

    async def upsert_student(
        self,
        user_id: int,
        username: Optional[str],
        full_name: str,
        stream: str,
        bank: str,
        file_id: str,
        file_type: str,
        status: str = "Pending",
    ) -> None:
        """Insert a new student registration or update an existing one."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO students (
                    user_id, username, full_name, stream, bank,
                    file_id, file_type, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name,
                    stream = excluded.stream,
                    bank = excluded.bank,
                    file_id = excluded.file_id,
                    file_type = excluded.file_type,
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (
                    user_id,
                    username,
                    full_name,
                    stream,
                    bank,
                    file_id,
                    file_type,
                    status,
                    now,
                    now,
                ),
            )
            await db.commit()
            logger.info("Student %d (%s) saved with status '%s'", user_id, full_name, status)

    async def get_student(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve student record by Telegram user ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM students WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def update_student_status(
        self, user_id: int, status: str, invite_link: Optional[str] = None
    ) -> bool:
        """Update student status ('Approved', 'Rejected', etc.) and optional invite link."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            if invite_link is not None:
                cursor = await db.execute(
                    """
                    UPDATE students
                    SET status = ?, invite_link = ?, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (status, invite_link, now, user_id),
                )
            else:
                cursor = await db.execute(
                    """
                    UPDATE students
                    SET status = ?, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (status, now, user_id),
                )
            await db.commit()
            return cursor.rowcount > 0

    async def get_statistics(self) -> Dict[str, int]:
        """Calculate live statistics for admin dashboard."""
        async with aiosqlite.connect(self.db_path) as db:
            stats: Dict[str, int] = {
                "total_users": 0,
                "total_students": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0,
                "natural": 0,
                "social": 0,
                "cbe": 0,
                "boa": 0,
                "telebirr": 0,
            }

            # Count registered bot users
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                row = await cursor.fetchone()
                stats["total_users"] = row[0] if row else 0

            # Count total students
            async with db.execute("SELECT COUNT(*) FROM students") as cursor:
                row = await cursor.fetchone()
                stats["total_students"] = row[0] if row else 0

            # Count by status
            async with db.execute(
                "SELECT status, COUNT(*) FROM students GROUP BY status"
            ) as cursor:
                async for status, count in cursor:
                    key = status.lower()
                    if key in stats:
                        stats[key] = count

            # Count by stream
            async with db.execute(
                "SELECT stream, COUNT(*) FROM students GROUP BY stream"
            ) as cursor:
                async for stream, count in cursor:
                    if "natural" in stream.lower():
                        stats["natural"] += count
                    elif "social" in stream.lower():
                        stats["social"] += count

            # Count by bank
            async with db.execute(
                "SELECT bank, COUNT(*) FROM students GROUP BY bank"
            ) as cursor:
                async for bank, count in cursor:
                    bank_lower = bank.lower()
                    if "cbe" in bank_lower:
                        stats["cbe"] += count
                    elif "abyssinia" in bank_lower or "boa" in bank_lower:
                        stats["boa"] += count
                    elif "telebirr" in bank_lower:
                        stats["telebirr"] += count

            return stats

    async def get_all_user_ids(self) -> List[int]:
        """Fetch all unique user IDs for broadcast messaging."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT user_id FROM users
                UNION
                SELECT user_id FROM students
                """
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_all_students_for_export(self) -> List[Dict[str, Any]]:
        """Retrieve all student records for CSV export."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM students ORDER BY created_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


# Global database instance
db = Database()
