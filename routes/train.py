"""
E.A.D.A Training Route
----------------------
Trains the Reinforcement Learning agent and
updates analytics graphs.
"""

import traceback

from flask import Blueprint, jsonify

from config import Config
from services import services


train_bp = Blueprint(
    "train",
    __name__
)


@train_bp.route(
    "/train",
    methods=["POST"]
)
def train():
    """
    Train the Reinforcement Learning agent.
    """

    try:

        result = services.trainer.train(
            csv_path=Config.TRAINING_DATASET_PATH,
            episodes=Config.TRAINING_EPISODES
        )

        graph_paths = (
            services.graphs.generate_training_graphs(
                result["reward_history"],
                result["success_history"]
            )
        )

        database_service = getattr(
            services,
            "database_service",
            None
        )

        if database_service is None:
            database_service = getattr(
                services,
                "database",
                None
            )

        statistics = {
            "total_decisions": 0
        }

        if database_service is not None:

            if hasattr(
                database_service,
                "get_statistics"
            ):
                statistics = (
                    database_service.get_statistics()
                )

        return jsonify({

            "status": "success",

            "message":
                "Training completed successfully.",

            "episodes":
                result["episodes"],

            "dataset_size":
                result["dataset_size"],

            "q_states":
                result["agent"].get_q_table_size(),

            "average_reward":
                services.metrics.average_reward(
                    result["reward_history"]
                ),

            "maximum_reward":
                services.metrics.max_reward(
                    result["reward_history"]
                ),

            "minimum_reward":
                services.metrics.min_reward(
                    result["reward_history"]
                ),

            "success_rate":
                services.metrics.success_rate(
                    result["success_history"]
                ),

            "learning_progress":
                services.metrics.learning_progress(
                    result["reward_history"]
                ),

            "database_records":
                statistics.get(
                    "total_decisions",
                    0
                ),

            "graphs":
                graph_paths

        }), 200

    except Exception as error:

        print(
            "\n========== TRAINING ERROR =========="
        )

        traceback.print_exc()

        print(
            "====================================\n"
        )

        return jsonify({

            "status": "error",

            "message":
                "Training failed.",

            "details":
                str(error)

        }), 500