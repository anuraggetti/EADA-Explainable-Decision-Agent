"""
E.A.D.A Analytics Route
-----------------------
Provides dashboard analytics and learning statistics.
"""

import traceback

from flask import Blueprint, jsonify

from services import services


analytics_bp = Blueprint(
    "analytics",
    __name__
)


@analytics_bp.route(
    "/analytics",
    methods=["GET"]
)
def analytics():
    """
    Return analytics for the dashboard.
    """

    try:

        trainer = services.trainer

        # ---------------------------------------------
        # Training histories
        # ---------------------------------------------

        rewards = list(
            getattr(
                trainer,
                "reward_history",
                []
            )
        )

        success_history = list(
            getattr(
                trainer,
                "success_history",
                []
            )
        )


        # ---------------------------------------------
        # Database service
        # ---------------------------------------------

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


        database_statistics = {
            "total_decisions": 0
        }

        if (
            database_service is not None
            and hasattr(
                database_service,
                "get_statistics"
            )
        ):
            database_statistics = (
                database_service.get_statistics()
            )


        # ---------------------------------------------
        # Training summary
        # ---------------------------------------------

        if hasattr(
            trainer,
            "get_training_summary"
        ):
            training_summary = (
                trainer.get_training_summary()
            )
        else:
            training_summary = {}


        # ---------------------------------------------
        # Metrics
        # ---------------------------------------------

        average_reward = (
            services.metrics.average_reward(
                rewards
            )
        )

        maximum_reward = (
            services.metrics.max_reward(
                rewards
            )
        )

        minimum_reward = (
            services.metrics.min_reward(
                rewards
            )
        )

        success_rate = (
            services.metrics.success_rate(
                success_history
            )
        )

        learning_progress = (
            services.metrics.learning_progress(
                rewards
            )
        )


        # ---------------------------------------------
        # Response
        # ---------------------------------------------

        return jsonify({

            "status": "success",

            "database":
                database_statistics,

            "training":
                training_summary,

            "metrics": {

                "average_reward":
                    average_reward,

                "maximum_reward":
                    maximum_reward,

                "minimum_reward":
                    minimum_reward,

                "success_rate":
                    success_rate,

                "learning_progress":
                    learning_progress
            },

            "reward_history":
                rewards,

            "success_history":
                success_history,

            "q_table_states":
                services.agent.get_q_table_size()

        }), 200


    except Exception as error:

        print(
            "\n========== ANALYTICS ERROR =========="
        )

        traceback.print_exc()

        print(
            "=====================================\n"
        )

        return jsonify({

            "status": "error",

            "message":
                "Unable to load analytics.",

            "details":
                str(error)

        }), 500