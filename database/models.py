"""
E.A.D.A Database Repository
---------------------------
Handles SQLite database creation and CRUD operations
for task-decision history.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import Config


class Database:
    """
    SQLite repository for storing AI decision history.

    A new connection is created for each operation. This is safer
    when the same database object is shared across Flask requests.
    """

    ALLOWED_ACTIONS = {
        "Execute Immediately",
        "Allocate Resources",
        "Split Task",
        "Delay Task"
    }

    ALLOWED_RISK_LEVELS = {
        "Low",
        "Medium",
        "High"
    }

    def __init__(
        self,
        database_path: Optional[str] = None
    ):
        self.database_path = Path(
            database_path or Config.DATABASE_PATH
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.create_table()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and configure a SQLite connection.
        """

        connection = sqlite3.connect(
            str(self.database_path),
            timeout=10
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        return connection

    def create_table(self) -> None:
        """
        Create the decision-history table when it does not exist.

        The schema remains compatible with the original project.
        """

        query = """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                action TEXT NOT NULL,
                reward REAL NOT NULL,
                confidence INTEGER NOT NULL,
                risk TEXT NOT NULL,
                explanation TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """

        try:
            with self._get_connection() as connection:
                connection.execute(query)
                connection.commit()

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to create database table: {error}"
            ) from error

    def save_task(
        self,
        task: str,
        action: str,
        reward: float,
        confidence: int,
        risk: str,
        explanation: str
    ) -> int:
        """
        Store an AI task decision.

        Returns:
            ID of the newly inserted history record.
        """

        validated_data = self._validate_task_data(
            task=task,
            action=action,
            reward=reward,
            confidence=confidence,
            risk=risk,
            explanation=explanation
        )

        query = """
            INSERT INTO history (
                task,
                action,
                reward,
                confidence,
                risk,
                explanation,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        values = (
            validated_data["task"],
            validated_data["action"],
            validated_data["reward"],
            validated_data["confidence"],
            validated_data["risk"],
            validated_data["explanation"],
            created_at
        )

        try:
            with self._get_connection() as connection:
                cursor = connection.execute(
                    query,
                    values
                )

                connection.commit()

                return int(cursor.lastrowid)

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to save task decision: {error}"
            ) from error

    def get_history(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        as_dict: bool = False
    ) -> list:
        """
        Retrieve decision history in newest-first order.

        Args:
            limit:
                Maximum number of records. When omitted, all
                records are returned.

            offset:
                Number of records to skip.

            as_dict:
                When True, return dictionaries. When False,
                return tuples for compatibility with the old code.
        """

        offset_value = max(0, int(offset))

        query = """
            SELECT
                id,
                task,
                action,
                reward,
                confidence,
                risk,
                explanation,
                created_at
            FROM history
            ORDER BY id DESC
        """

        parameters = []

        if limit is not None:
            limit_value = max(1, int(limit))

            query += " LIMIT ? OFFSET ?"

            parameters.extend([
                limit_value,
                offset_value
            ])

        try:
            with self._get_connection() as connection:
                rows = connection.execute(
                    query,
                    parameters
                ).fetchall()

            return self._format_rows(
                rows,
                as_dict
            )

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to retrieve decision history: {error}"
            ) from error

    def get_task_by_id(
        self,
        record_id: int,
        as_dict: bool = True
    ):
        """
        Retrieve one history record by its ID.
        """

        query = """
            SELECT
                id,
                task,
                action,
                reward,
                confidence,
                risk,
                explanation,
                created_at
            FROM history
            WHERE id = ?
        """

        try:
            with self._get_connection() as connection:
                row = connection.execute(
                    query,
                    (int(record_id),)
                ).fetchone()

            if row is None:
                return None

            if as_dict:
                return dict(row)

            return tuple(row)

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to retrieve history record: {error}"
            ) from error

    def search_history(
        self,
        task_query: Optional[str] = None,
        action: Optional[str] = None,
        risk: Optional[str] = None,
        minimum_reward: Optional[float] = None,
        limit: int = 100,
        as_dict: bool = True
    ) -> list:
        """
        Search and filter decision history.
        """

        query = """
            SELECT
                id,
                task,
                action,
                reward,
                confidence,
                risk,
                explanation,
                created_at
            FROM history
            WHERE 1 = 1
        """

        parameters = []

        if task_query:
            query += " AND LOWER(task) LIKE ?"

            parameters.append(
                f"%{task_query.strip().lower()}%"
            )

        if action:
            if action not in self.ALLOWED_ACTIONS:
                raise ValueError(
                    f"Unsupported action filter: {action}"
                )

            query += " AND action = ?"
            parameters.append(action)

        if risk:
            normalized_risk = risk.strip().title()

            if normalized_risk not in self.ALLOWED_RISK_LEVELS:
                raise ValueError(
                    f"Unsupported risk filter: {risk}"
                )

            query += " AND risk = ?"
            parameters.append(normalized_risk)

        if minimum_reward is not None:
            query += " AND reward >= ?"

            parameters.append(
                float(minimum_reward)
            )

        query += " ORDER BY id DESC LIMIT ?"

        parameters.append(
            max(1, int(limit))
        )

        try:
            with self._get_connection() as connection:
                rows = connection.execute(
                    query,
                    parameters
                ).fetchall()

            return self._format_rows(
                rows,
                as_dict
            )

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to search decision history: {error}"
            ) from error

    def get_recent_history(
        self,
        limit: int = 10,
        as_dict: bool = True
    ) -> list:
        """
        Retrieve the most recent decision records.
        """

        return self.get_history(
            limit=limit,
            offset=0,
            as_dict=as_dict
        )

    def count_history(self) -> int:
        """
        Return the total number of stored decisions.
        """

        query = """
            SELECT COUNT(*) AS total
            FROM history
        """

        try:
            with self._get_connection() as connection:
                row = connection.execute(
                    query
                ).fetchone()

            return int(row["total"])

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to count history records: {error}"
            ) from error

    def get_statistics(self) -> dict:
        """
        Calculate database-level dashboard statistics.
        """

        summary_query = """
            SELECT
                COUNT(*) AS total_decisions,
                COALESCE(AVG(reward), 0) AS average_reward,
                COALESCE(MAX(reward), 0) AS maximum_reward,
                COALESCE(MIN(reward), 0) AS minimum_reward,
                COALESCE(AVG(confidence), 0) AS average_confidence
            FROM history
        """

        action_query = """
            SELECT
                action,
                COUNT(*) AS total
            FROM history
            GROUP BY action
        """

        risk_query = """
            SELECT
                risk,
                COUNT(*) AS total
            FROM history
            GROUP BY risk
        """

        try:
            with self._get_connection() as connection:
                summary = connection.execute(
                    summary_query
                ).fetchone()

                action_rows = connection.execute(
                    action_query
                ).fetchall()

                risk_rows = connection.execute(
                    risk_query
                ).fetchall()

            action_distribution = {
                action: 0
                for action in self.ALLOWED_ACTIONS
            }

            for row in action_rows:
                action_distribution[row["action"]] = int(
                    row["total"]
                )

            risk_distribution = {
                risk_level: 0
                for risk_level in self.ALLOWED_RISK_LEVELS
            }

            for row in risk_rows:
                risk_distribution[row["risk"]] = int(
                    row["total"]
                )

            return {
                "total_decisions": int(
                    summary["total_decisions"]
                ),
                "average_reward": round(
                    float(summary["average_reward"]),
                    2
                ),
                "maximum_reward": round(
                    float(summary["maximum_reward"]),
                    2
                ),
                "minimum_reward": round(
                    float(summary["minimum_reward"]),
                    2
                ),
                "average_confidence": round(
                    float(summary["average_confidence"]),
                    2
                ),
                "action_distribution": action_distribution,
                "risk_distribution": risk_distribution
            }

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to calculate database statistics: {error}"
            ) from error

    def delete_task(
        self,
        record_id: int
    ) -> bool:
        """
        Delete a single history record.

        Returns:
            True when a record was deleted.
        """

        query = """
            DELETE FROM history
            WHERE id = ?
        """

        try:
            with self._get_connection() as connection:
                cursor = connection.execute(
                    query,
                    (int(record_id),)
                )

                connection.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to delete history record: {error}"
            ) from error

    def clear_history(self) -> int:
        """
        Delete all history records.

        Returns:
            Number of deleted records.
        """

        query = "DELETE FROM history"

        try:
            with self._get_connection() as connection:
                cursor = connection.execute(query)
                connection.commit()

                return cursor.rowcount

        except sqlite3.Error as error:
            raise RuntimeError(
                f"Unable to clear decision history: {error}"
            ) from error

    @staticmethod
    def _format_rows(
        rows: list,
        as_dict: bool
    ) -> list:
        """
        Convert SQLite rows to dictionaries or tuples.
        """

        if as_dict:
            return [
                dict(row)
                for row in rows
            ]

        return [
            tuple(row)
            for row in rows
        ]

    def _validate_task_data(
        self,
        task: str,
        action: str,
        reward: float,
        confidence: int,
        risk: str,
        explanation: str
    ) -> dict[str, Any]:
        """
        Validate a decision before saving it.
        """

        if not isinstance(task, str) or not task.strip():
            raise ValueError(
                "Task description cannot be empty."
            )

        if action not in self.ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported action: {action}"
            )

        try:
            reward_value = float(reward)

        except (TypeError, ValueError) as error:
            raise ValueError(
                "Reward must be a valid number."
            ) from error

        try:
            confidence_value = int(
                round(float(confidence))
            )

        except (TypeError, ValueError) as error:
            raise ValueError(
                "Confidence must be a valid number."
            ) from error

        if not 0 <= confidence_value <= 100:
            raise ValueError(
                "Confidence must be between 0 and 100."
            )

        normalized_risk = str(risk).strip().title()

        if normalized_risk not in self.ALLOWED_RISK_LEVELS:
            raise ValueError(
                "Risk must be Low, Medium, or High."
            )

        if (
            not isinstance(explanation, str)
            or not explanation.strip()
        ):
            raise ValueError(
                "Explanation cannot be empty."
            )

        return {
            "task": task.strip(),
            "action": action,
            "reward": round(reward_value, 2),
            "confidence": confidence_value,
            "risk": normalized_risk,
            "explanation": explanation.strip()
        }