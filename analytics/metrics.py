"""
E.A.D.A Metrics Module
----------------------
Calculates reinforcement-learning and dashboard statistics.
"""

from collections import Counter
from typing import Iterable


class Metrics:
    """
    Provides reusable statistical calculations for training
    history and decision records.
    """

    @staticmethod
    def average_reward(
        rewards: Iterable[float]
    ) -> float:
        values = list(rewards)

        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            2
        )

    @staticmethod
    def max_reward(
        rewards: Iterable[float]
    ) -> float:
        values = list(rewards)

        if not values:
            return 0.0

        return round(
            max(values),
            2
        )

    @staticmethod
    def min_reward(
        rewards: Iterable[float]
    ) -> float:
        values = list(rewards)

        if not values:
            return 0.0

        return round(
            min(values),
            2
        )

    @staticmethod
    def success_rate(
        success_history: Iterable[float]
    ) -> float:
        """
        Return the latest success rate as a percentage.

        Example:
            0.82 becomes 82.0
        """

        values = list(success_history)

        if not values:
            return 0.0

        latest_value = float(
            values[-1]
        )

        if latest_value <= 1:
            latest_value *= 100

        return round(
            latest_value,
            2
        )

    @staticmethod
    def average_success_rate(
        success_history: Iterable[float]
    ) -> float:
        """
        Return the average success rate as a percentage.
        """

        values = list(success_history)

        if not values:
            return 0.0

        normalized_values = [
            value * 100
            if float(value) <= 1
            else float(value)
            for value in values
        ]

        return round(
            sum(normalized_values)
            / len(normalized_values),
            2
        )

    @staticmethod
    def learning_progress(
        rewards: Iterable[float]
    ) -> float:
        """
        Return the difference between the latest and first reward.
        """

        values = list(rewards)

        if len(values) < 2:
            return 0.0

        return round(
            float(values[-1])
            - float(values[0]),
            2
        )

    @staticmethod
    def reward_trend(
        rewards: Iterable[float],
        window_size: int = 10
    ) -> float:
        """
        Compare the latest reward window with the initial window.
        """

        values = [
            float(value)
            for value in rewards
        ]

        if len(values) < 2:
            return 0.0

        window = max(
            1,
            min(
                int(window_size),
                len(values) // 2
            )
        )

        first_average = (
            sum(values[:window])
            / window
        )

        latest_average = (
            sum(values[-window:])
            / window
        )

        return round(
            latest_average
            - first_average,
            2
        )

    @staticmethod
    def moving_average(
        values: Iterable[float],
        window_size: int = 10
    ) -> list[float]:
        """
        Calculate a moving average for graph smoothing.
        """

        numbers = [
            float(value)
            for value in values
        ]

        if not numbers:
            return []

        window = max(
            1,
            int(window_size)
        )

        averages = []

        for index in range(
            len(numbers)
        ):
            start_index = max(
                0,
                index - window + 1
            )

            current_window = numbers[
                start_index:index + 1
            ]

            averages.append(
                round(
                    sum(current_window)
                    / len(current_window),
                    4
                )
            )

        return averages

    @staticmethod
    def average_confidence(
        confidence_values: Iterable[float]
    ) -> float:
        values = [
            float(value)
            for value in confidence_values
        ]

        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            2
        )

    @staticmethod
    def action_distribution(
        actions: Iterable[str]
    ) -> dict[str, int]:
        """
        Count how frequently each AI action appears.
        """

        expected_actions = {
            "Execute Immediately": 0,
            "Allocate Resources": 0,
            "Split Task": 0,
            "Delay Task": 0
        }

        action_counts = Counter(
            actions
        )

        expected_actions.update({
            action: int(count)
            for action, count
            in action_counts.items()
        })

        return expected_actions

    @staticmethod
    def risk_distribution(
        risks: Iterable[str]
    ) -> dict[str, int]:
        """
        Count Low, Medium, and High risk decisions.
        """

        expected_risks = {
            "Low": 0,
            "Medium": 0,
            "High": 0
        }

        risk_counts = Counter(
            str(risk).title()
            for risk in risks
        )

        expected_risks.update({
            risk: int(count)
            for risk, count
            in risk_counts.items()
        })

        return expected_risks

    def training_summary(
        self,
        rewards: Iterable[float],
        success_history: Iterable[float],
        q_table_size: int = 0
    ) -> dict:
        """
        Return a complete training summary.
        """

        reward_values = list(
            rewards
        )

        success_values = list(
            success_history
        )

        return {
            "episodes": len(
                reward_values
            ),
            "average_reward": self.average_reward(
                reward_values
            ),
            "maximum_reward": self.max_reward(
                reward_values
            ),
            "minimum_reward": self.min_reward(
                reward_values
            ),
            "success_rate": self.success_rate(
                success_values
            ),
            "average_success_rate": (
                self.average_success_rate(
                    success_values
                )
            ),
            "learning_progress": (
                self.learning_progress(
                    reward_values
                )
            ),
            "reward_trend": self.reward_trend(
                reward_values
            ),
            "q_table_states": int(
                q_table_size
            )
        }