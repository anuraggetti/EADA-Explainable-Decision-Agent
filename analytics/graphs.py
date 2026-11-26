"""
E.A.D.A Graphs Module
--------------------
Creates professional training and decision analytics graphs.
"""

from pathlib import Path
from typing import Iterable, Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from analytics.metrics import Metrics
from config import GRAPH_FOLDER


class Graphs:
    """
    Generates dashboard-ready PNG graphs.
    """

    def __init__(
        self,
        output_folder: Optional[str] = None
    ):
        self.output_folder = Path(
            output_folder or GRAPH_FOLDER
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.metrics = Metrics()

    def reward_graph(
        self,
        rewards: Iterable[float],
        filename: str = "reward_graph.png"
    ) -> str:
        """
        Generate reward-per-episode graph with moving average.
        """

        reward_values = [
            float(value)
            for value in rewards
        ]

        output_path = (
            self.output_folder
            / filename
        )

        figure, axis = plt.subplots(
            figsize=(10, 6)
        )

        if reward_values:
            episodes = range(
                1,
                len(reward_values) + 1
            )

            moving_average = (
                self.metrics.moving_average(
                    reward_values,
                    window_size=10
                )
            )

            axis.plot(
                episodes,
                reward_values,
                linewidth=1.4,
                alpha=0.65,
                label="Episode Reward"
            )

            axis.plot(
                episodes,
                moving_average,
                linewidth=2.5,
                label="Moving Average"
            )

            axis.legend()

        else:
            self._draw_empty_message(
                axis,
                "No reward history available"
            )

        axis.set_title(
            "Reward Progress Across Training Episodes"
        )

        axis.set_xlabel(
            "Episode"
        )

        axis.set_ylabel(
            "Reward"
        )

        axis.grid(
            True,
            alpha=0.3
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

        return str(
            output_path
        )

    def success_graph(
        self,
        success_history: Iterable[float],
        filename: str = "success_graph.png"
    ) -> str:
        """
        Generate success-rate progression graph.
        """

        success_values = [
            float(value)
            for value in success_history
        ]

        success_percentages = [
            value * 100
            if value <= 1
            else value
            for value in success_values
        ]

        output_path = (
            self.output_folder
            / filename
        )

        figure, axis = plt.subplots(
            figsize=(10, 6)
        )

        if success_percentages:
            episodes = range(
                1,
                len(success_percentages) + 1
            )

            moving_average = (
                self.metrics.moving_average(
                    success_percentages,
                    window_size=10
                )
            )

            axis.plot(
                episodes,
                success_percentages,
                linewidth=1.5,
                alpha=0.7,
                label="Episode Success Rate"
            )

            axis.plot(
                episodes,
                moving_average,
                linewidth=2.5,
                label="Moving Average"
            )

            axis.legend()

        else:
            self._draw_empty_message(
                axis,
                "No success history available"
            )

        axis.set_title(
            "Training Success Rate"
        )

        axis.set_xlabel(
            "Episode"
        )

        axis.set_ylabel(
            "Success Rate (%)"
        )

        axis.set_ylim(
            0,
            100
        )

        axis.grid(
            True,
            alpha=0.3
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

        return str(
            output_path
        )

    def learning_progress_graph(
        self,
        rewards: Iterable[float],
        filename: str = "learning_progress.png"
    ) -> str:
        """
        Generate cumulative learning-progress graph.
        """

        reward_values = [
            float(value)
            for value in rewards
        ]

        output_path = (
            self.output_folder
            / filename
        )

        figure, axis = plt.subplots(
            figsize=(10, 6)
        )

        if reward_values:
            cumulative_averages = []

            total_reward = 0.0

            for index, reward in enumerate(
                reward_values,
                start=1
            ):
                total_reward += reward

                cumulative_averages.append(
                    total_reward / index
                )

            episodes = range(
                1,
                len(reward_values) + 1
            )

            axis.plot(
                episodes,
                cumulative_averages,
                linewidth=2.4,
                label="Cumulative Average Reward"
            )

            axis.legend()

        else:
            self._draw_empty_message(
                axis,
                "No learning history available"
            )

        axis.set_title(
            "Reinforcement Learning Progress"
        )

        axis.set_xlabel(
            "Episode"
        )

        axis.set_ylabel(
            "Cumulative Average Reward"
        )

        axis.grid(
            True,
            alpha=0.3
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

        return str(
            output_path
        )

    def action_distribution_graph(
        self,
        action_distribution: dict[str, int],
        filename: str = "action_distribution.png"
    ) -> str:
        """
        Generate action-selection distribution bar chart.
        """

        output_path = (
            self.output_folder
            / filename
        )

        labels = list(
            action_distribution.keys()
        )

        values = [
            int(value)
            for value
            in action_distribution.values()
        ]

        figure, axis = plt.subplots(
            figsize=(11, 6)
        )

        if any(values):
            bars = axis.bar(
                labels,
                values
            )

            axis.bar_label(
                bars,
                padding=3
            )

        else:
            self._draw_empty_message(
                axis,
                "No decision history available"
            )

        axis.set_title(
            "AI Action Distribution"
        )

        axis.set_xlabel(
            "Recommended Action"
        )

        axis.set_ylabel(
            "Number of Decisions"
        )

        axis.tick_params(
            axis="x",
            rotation=18
        )

        axis.grid(
            True,
            axis="y",
            alpha=0.3
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

        return str(
            output_path
        )

    def risk_distribution_graph(
        self,
        risk_distribution: dict[str, int],
        filename: str = "risk_distribution.png"
    ) -> str:
        """
        Generate risk-level distribution pie chart.
        """

        output_path = (
            self.output_folder
            / filename
        )

        filtered_data = {
            label: int(value)
            for label, value
            in risk_distribution.items()
            if int(value) > 0
        }

        figure, axis = plt.subplots(
            figsize=(8, 7)
        )

        if filtered_data:
            axis.pie(
                list(
                    filtered_data.values()
                ),
                labels=list(
                    filtered_data.keys()
                ),
                autopct="%1.1f%%",
                startangle=90
            )

            axis.axis(
                "equal"
            )

        else:
            self._draw_empty_message(
                axis,
                "No risk data available"
            )

        axis.set_title(
            "Decision Risk Distribution"
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

        return str(
            output_path
        )

    def confidence_distribution_graph(
        self,
        confidence_values: Iterable[float],
        filename: str = "confidence_distribution.png"
    ) -> str:
        """
        Generate confidence-score histogram.
        """

        values = [
            max(
                0,
                min(
                    100,
                    float(value)
                )
            )
            for value
            in confidence_values
        ]

        output_path = (
            self.output_folder
            / filename
        )

        figure, axis = plt.subplots(
            figsize=(10, 6)
        )

        if values:
            axis.hist(
                values,
                bins=10,
                edgecolor="black",
                alpha=0.8
            )

        else:
            self._draw_empty_message(
                axis,
                "No confidence data available"
            )

        axis.set_title(
            "Decision Confidence Distribution"
        )

        axis.set_xlabel(
            "Confidence (%)"
        )

        axis.set_ylabel(
            "Frequency"
        )

        axis.set_xlim(
            0,
            100
        )

        axis.grid(
            True,
            axis="y",
            alpha=0.3
        )

        figure.tight_layout()

        figure.savefig(
            output_path,
            dpi=160,
            bbox_inches="tight"
        )

        plt.close(
            figure
        )

        return str(
            output_path
        )

    def generate_training_graphs(
        self,
        rewards: Iterable[float],
        success_history: Iterable[float]
    ) -> dict[str, str]:
        """
        Generate all graphs related to agent training.
        """

        return {
            "reward_graph": self.reward_graph(
                rewards
            ),
            "success_graph": self.success_graph(
                success_history
            ),
            "learning_progress_graph": (
                self.learning_progress_graph(
                    rewards
                )
            )
        }

    def generate_decision_graphs(
        self,
        records: list[dict]
    ) -> dict[str, str]:
        """
        Generate graphs using stored decision-history records.
        """

        actions = [
            record["action"]
            for record in records
        ]

        risks = [
            record["risk"]
            for record in records
        ]

        confidence_values = [
            record["confidence"]
            for record in records
        ]

        action_distribution = (
            self.metrics.action_distribution(
                actions
            )
        )

        risk_distribution = (
            self.metrics.risk_distribution(
                risks
            )
        )

        return {
            "action_distribution_graph": (
                self.action_distribution_graph(
                    action_distribution
                )
            ),
            "risk_distribution_graph": (
                self.risk_distribution_graph(
                    risk_distribution
                )
            ),
            "confidence_distribution_graph": (
                self.confidence_distribution_graph(
                    confidence_values
                )
            )
        }

    @staticmethod
    def _draw_empty_message(
        axis,
        message: str
    ) -> None:
        """
        Display a clear message when graph data is unavailable.
        """

        axis.text(
            0.5,
            0.5,
            message,
            horizontalalignment="center",
            verticalalignment="center",
            transform=axis.transAxes,
            fontsize=12
        )

        axis.set_xticks([])
        axis.set_yticks([])