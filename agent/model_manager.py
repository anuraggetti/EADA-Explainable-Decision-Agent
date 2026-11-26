"""
E.A.D.A Model Manager
---------------------
Safely saves and loads the Q-table used by the
Q-Learning agent.
"""

import ast
import json
from pathlib import Path
from typing import Any

from config import Config


class ModelManager:
    """
    Handles persistent storage of the Q-table.
    """

    MODEL_PATH = Path(Config.MODEL_PATH)

    @classmethod
    def save_q_table(
        cls,
        q_table: dict[tuple, dict[str, float]]
    ) -> None:
        """
        Save the Q-table using a safe JSON representation.

        Args:
            q_table:
                Dictionary containing state-action Q-values.
        """

        cls.MODEL_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        serialized_states = []

        for state, actions in q_table.items():
            serialized_states.append({
                "state": list(state),
                "actions": {
                    str(action): round(
                        float(value),
                        4
                    )
                    for action, value in actions.items()
                }
            })

        model_data = {
            "version": 2,
            "states": serialized_states
        }

        temporary_path = cls.MODEL_PATH.with_suffix(
            ".tmp"
        )

        try:
            with temporary_path.open(
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    model_data,
                    file,
                    indent=4
                )

            temporary_path.replace(
                cls.MODEL_PATH
            )

        except (OSError, TypeError, ValueError) as error:
            if temporary_path.exists():
                temporary_path.unlink()

            raise RuntimeError(
                f"Unable to save Q-table: {error}"
            ) from error

    @classmethod
    def load_q_table(
        cls
    ) -> dict[tuple, dict[str, float]]:
        """
        Load the Q-table.

        Supports both the new safe JSON format and the
        older tuple-string format used by previous versions.

        Returns:
            Loaded Q-table, or an empty dictionary when no
            valid model exists.
        """

        if not cls.MODEL_PATH.exists():
            return {}

        try:
            with cls.MODEL_PATH.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if cls._is_new_format(data):
                return cls._load_new_format(data)

            return cls._load_legacy_format(data)

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
            SyntaxError
        ):
            return {}

    @staticmethod
    def _is_new_format(data: Any) -> bool:
        """
        Check whether model data uses the version-2 format.
        """

        return (
            isinstance(data, dict)
            and data.get("version") == 2
            and isinstance(data.get("states"), list)
        )

    @staticmethod
    def _load_new_format(
        data: dict
    ) -> dict[tuple, dict[str, float]]:
        """
        Load the version-2 model format.
        """

        q_table = {}

        for record in data["states"]:
            if not isinstance(record, dict):
                continue

            state = record.get("state")
            actions = record.get("actions")

            if (
                not isinstance(state, list)
                or not isinstance(actions, dict)
            ):
                continue

            state_key = tuple(state)

            q_table[state_key] = {
                str(action): float(value)
                for action, value in actions.items()
            }

        return q_table

    @staticmethod
    def _load_legacy_format(
        data: Any
    ) -> dict[tuple, dict[str, float]]:
        """
        Safely load the older format where state tuples were
        stored as dictionary keys.

        ast.literal_eval is used instead of unsafe eval().
        """

        if not isinstance(data, dict):
            return {}

        q_table = {}

        for state_text, actions in data.items():
            if not isinstance(actions, dict):
                continue

            parsed_state = ast.literal_eval(
                state_text
            )

            if not isinstance(parsed_state, tuple):
                continue

            q_table[parsed_state] = {
                str(action): float(value)
                for action, value in actions.items()
            }

        return q_table