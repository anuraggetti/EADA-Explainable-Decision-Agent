"""
E.A.D.A Training Service
------------------------
Trains the Q-Learning agent using task records stored
in a CSV dataset.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from agent.q_learning import QLearningAgent
from agent.reward_engine import RewardEngine
from agent.state_encoder import StateEncoder
from config import Config


class Trainer:
    """
    Coordinates dataset loading, state encoding,
    reward calculation, and Q-value updates.
    """

    REQUIRED_COLUMNS = {
        "Priority",
        "Deadline",
        "Complexity",
        "Resources",
        "Success",
        "Failure"
    }

    def __init__(
        self,
        encoder: Optional[StateEncoder] = None,
        reward_engine: Optional[RewardEngine] = None,
        agent: Optional[QLearningAgent] = None
    ):
        self.encoder = encoder or StateEncoder()
        self.reward_engine = (
            reward_engine or RewardEngine()
        )
        self.agent = agent or QLearningAgent()

        self.reward_history: list[float] = []
        self.success_history: list[float] = []

        self.completed_episodes = 0
        self.last_dataset_size = 0

    def train(
        self,
        csv_path,
        episodes: Optional[int] = None
    ) -> dict:
        """
        Train the agent using a CSV dataset.

        Args:
            csv_path:
                Path to the training CSV file.

            episodes:
                Number of training episodes.

        Returns:
            Training history and trained agent.

        Raises:
            FileNotFoundError:
                When the dataset does not exist.

            ValueError:
                When the dataset is empty or invalid.
        """

        dataset_path = Path(csv_path)

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Training dataset not found: "
                f"{dataset_path}"
            )

        episode_count = (
            Config.TRAINING_EPISODES
            if episodes is None
            else int(episodes)
        )

        if episode_count <= 0:
            raise ValueError(
                "Training episodes must be greater than 0."
            )

        data = pd.read_csv(dataset_path)

        self._validate_dataset(data)

        self.reward_history = []
        self.success_history = []
        self.completed_episodes = 0
        self.last_dataset_size = len(data)

        self.agent.reset_exploration()

        for episode_index in range(
            episode_count
        ):
            total_reward = 0.0
            successful_decisions = 0

            shuffled_data = data.sample(
                frac=1.0,
                random_state=episode_index
            ).reset_index(drop=True)

            for _, row in shuffled_data.iterrows():
                state = self.encoder.encode(
                    row["Priority"],
                    row["Deadline"],
                    row["Complexity"],
                    row["Resources"],
                    row["Success"],
                    row["Failure"]
                )

                action = self.agent.choose_action(
                    state,
                    training=True
                )

                reward = (
                    self.reward_engine.calculate_reward(
                        state,
                        action
                    )
                )

                self.agent.update_q_value(
                    state=state,
                    action=action,
                    reward=reward,
                    next_state=None,
                    terminal=True
                )

                total_reward += reward

                if reward >= 35:
                    successful_decisions += 1

            average_reward = (
                total_reward / len(shuffled_data)
            )

            success_rate = (
                successful_decisions
                / len(shuffled_data)
            )

            self.reward_history.append(
                round(average_reward, 2)
            )

            self.success_history.append(
                round(success_rate, 4)
            )

            self.completed_episodes = (
                episode_index + 1
            )

            self.agent.decay_exploration()

            print(
                f"Episode "
                f"{self.completed_episodes}/"
                f"{episode_count} | "
                f"Average Reward: "
                f"{average_reward:.2f} | "
                f"Success Rate: "
                f"{success_rate:.2%} | "
                f"Epsilon: "
                f"{self.agent.epsilon:.4f}"
            )

        self.agent.save()

        return {
            "reward_history": list(
                self.reward_history
            ),
            "success_history": list(
                self.success_history
            ),
            "agent": self.agent,
            "episodes": self.completed_episodes,
            "dataset_size": self.last_dataset_size
        }

    def get_training_summary(self) -> dict:
        """
        Return summary information from the latest
        training run.
        """

        if not self.reward_history:
            return {
                "episodes": 0,
                "dataset_size": 0,
                "average_reward": 0,
                "latest_reward": 0,
                "success_rate": 0,
                "states": self.agent.get_q_table_size()
            }

        return {
            "episodes": self.completed_episodes,
            "dataset_size": self.last_dataset_size,
            "average_reward": round(
                sum(self.reward_history)
                / len(self.reward_history),
                2
            ),
            "latest_reward": round(
                self.reward_history[-1],
                2
            ),
            "success_rate": round(
                self.success_history[-1] * 100,
                2
            ),
            "states": self.agent.get_q_table_size()
        }

    def _validate_dataset(
        self,
        data: pd.DataFrame
    ) -> None:
        """
        Validate required dataset columns and values.
        """

        if data.empty:
            raise ValueError(
                "Training dataset is empty."
            )

        missing_columns = (
            self.REQUIRED_COLUMNS
            - set(data.columns)
        )

        if missing_columns:
            formatted_columns = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "Training dataset is missing columns: "
                f"{formatted_columns}"
            )

        if data[list(self.REQUIRED_COLUMNS)].isnull().any().any():
            raise ValueError(
                "Training dataset contains empty values."
            )

        # Validate every row before starting training.
        for row_number, row in data.iterrows():
            try:
                self.encoder.encode(
                    row["Priority"],
                    row["Deadline"],
                    row["Complexity"],
                    row["Resources"],
                    row["Success"],
                    row["Failure"]
                )

            except ValueError as error:
                raise ValueError(
                    "Invalid training data at CSV row "
                    f"{row_number + 2}: {error}"
                ) from error