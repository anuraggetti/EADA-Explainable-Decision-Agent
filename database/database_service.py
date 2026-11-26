"""
E.A.D.A Database Service
------------------------
Provides higher-level operations for task history,
dashboard statistics, filtering, and export preparation.
"""

import csv
from pathlib import Path
from typing import Optional

from config import Config
from database.models import Database


class DatabaseService:
    """
    Service layer built on top of the SQLite repository.
    """

    def __init__(
        self,
        database: Optional[Database] = None
    ):
        self.database = database or Database()

    def record_decision(
        self,
        task: str,
        action: str,
        reward: float,
        confidence: int,
        risk: str,
        explanation: str
    ) -> dict:
        """
        Save an AI decision and return the saved record.
        """

        record_id = self.database.save_task(
            task=task,
            action=action,
            reward=reward,
            confidence=confidence,
            risk=risk,
            explanation=explanation
        )

        return self.database.get_task_by_id(
            record_id=record_id,
            as_dict=True
        )

    def get_history(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> list[dict]:
        """
        Return paginated history records.
        """

        return self.database.get_history(
            limit=limit,
            offset=offset,
            as_dict=True
        )

    def get_recent_decisions(
        self,
        limit: int = 10
    ) -> list[dict]:
        """
        Return the latest saved decisions.
        """

        return self.database.get_recent_history(
            limit=limit,
            as_dict=True
        )

    def find_decisions(
        self,
        task_query: Optional[str] = None,
        action: Optional[str] = None,
        risk: Optional[str] = None,
        minimum_reward: Optional[float] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Search task-decision history.
        """

        return self.database.search_history(
            task_query=task_query,
            action=action,
            risk=risk,
            minimum_reward=minimum_reward,
            limit=limit,
            as_dict=True
        )

    def get_dashboard_statistics(self) -> dict:
        """
        Return database statistics suitable for the dashboard.
        """

        statistics = self.database.get_statistics()

        total_decisions = statistics[
            "total_decisions"
        ]

        risk_distribution = statistics[
            "risk_distribution"
        ]

        high_risk_count = risk_distribution.get(
            "High",
            0
        )

        low_risk_count = risk_distribution.get(
            "Low",
            0
        )

        if total_decisions > 0:
            high_risk_percentage = round(
                high_risk_count
                / total_decisions
                * 100,
                2
            )

            low_risk_percentage = round(
                low_risk_count
                / total_decisions
                * 100,
                2
            )

        else:
            high_risk_percentage = 0.0
            low_risk_percentage = 0.0

        statistics.update({
            "high_risk_percentage": (
                high_risk_percentage
            ),
            "low_risk_percentage": (
                low_risk_percentage
            )
        })

        return statistics

    def delete_decision(
        self,
        record_id: int
    ) -> bool:
        """
        Delete one decision-history record.
        """

        return self.database.delete_task(
            record_id
        )

    def clear_all_history(self) -> int:
        """
        Delete all stored decision history.
        """

        return self.database.clear_history()

    def prepare_csv_export(
        self,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export all decision history to a CSV file.

        Returns:
            Absolute path of the generated CSV file.
        """

        if output_path:
            export_path = Path(output_path)

        else:
            export_folder = (
                Config.BASE_DIR / "exports"
                if hasattr(Config, "BASE_DIR")
                else Path("exports")
            )

            export_path = (
                export_folder
                / "eada_decision_history.csv"
            )

        export_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        records = self.database.get_history(
            as_dict=True
        )

        field_names = [
            "id",
            "task",
            "action",
            "reward",
            "confidence",
            "risk",
            "explanation",
            "created_at"
        ]

        try:
            with export_path.open(
                "w",
                newline="",
                encoding="utf-8"
            ) as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=field_names
                )

                writer.writeheader()

                for record in records:
                    writer.writerow(record)

        except OSError as error:
            raise RuntimeError(
                f"Unable to export decision history: {error}"
            ) from error

        return str(export_path.resolve())