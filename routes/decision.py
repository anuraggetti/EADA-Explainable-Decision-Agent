"""
E.A.D.A Decision Route
----------------------
Handles task analysis, reinforcement-learning decisions,
task-context interpretation, explanations, confidence,
risk, and database storage.
"""

import traceback

from flask import Blueprint, jsonify, request

from services import services


decision_bp = Blueprint(
    "decision",
    __name__
)


@decision_bp.route(
    "/decision",
    methods=["POST"]
)
def analyze():
    """
    Analyze a task and return the AI recommendation.
    """

    try:

        # =================================================
        # Read request
        # =================================================

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "status": "error",
                "message":
                    "Request body must contain valid JSON."
            }), 400


        required_fields = [
            "task",
            "priority",
            "deadline",
            "complexity",
            "resource",
            "success",
            "failure"
        ]


        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]


        if missing_fields:

            return jsonify({
                "status": "error",
                "message":
                    "Missing required fields: "
                    + ", ".join(
                        missing_fields
                    )
            }), 400


        # =================================================
        # Extract inputs
        # =================================================

        task = str(
            data["task"]
        ).strip()


        if not task:

            return jsonify({
                "status": "error",
                "message":
                    "Task description cannot be empty."
            }), 400


        priority = int(
            data["priority"]
        )


        deadline = int(
            data["deadline"]
        )


        complexity = str(
            data["complexity"]
        )


        resource = str(
            data["resource"]
        )


        success = float(
            data["success"]
        )


        failure = float(
            data["failure"]
        )


        # =================================================
        # Encode task state
        # =================================================

        state = services.encoder.encode(
            priority=priority,
            deadline=deadline,
            complexity=complexity,
            resources=resource,
            success=success,
            failure=failure
        )


        # =================================================
        # Task context analysis
        # =================================================

        explainer = getattr(
            services,
            "explainer",
            None
        )


        if explainer is None:

            explainer = getattr(
                services,
                "explanation",
                None
            )


        if explainer is None:

            raise AttributeError(
                "Explanation service is not configured."
            )


        task_context = (
            explainer.context_analyzer.analyze(
                task
            )
        )


        # =================================================
        # RL decision
        # =================================================

        action = (
            services.agent.choose_action(
                state,
                training=False
            )
        )


        # =================================================
        # Reward
        # =================================================

        reward = (
            services.reward_engine.calculate_reward(
                state,
                action
            )
        )


        # =================================================
        # Q-values
        # =================================================

        q_values = (
            services.agent.get_state_values(
                state
            )
        )


        # =================================================
        # Confidence
        # =================================================

        confidence = (
            services.agent.get_confidence(
                state,
                action
            )
        )


        # =================================================
        # Risk
        # =================================================

        risk = (
            services.reward_engine.calculate_risk(
                state
            )
        )


        # =================================================
        # Human-readable explanation
        # =================================================

        explanation = (
            explainer.generate(
                task=task,
                state=state,
                action=action,
                reward=reward,
                confidence=confidence,
                risk=risk,
                q_values=q_values
            )
        )


        # =================================================
        # Database service
        # =================================================

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


        saved_record = None


        if database_service is not None:

            if hasattr(
                database_service,
                "record_decision"
            ):

                saved_record = (
                    database_service.record_decision(
                        task=task,
                        action=action,
                        reward=reward,
                        confidence=confidence,
                        risk=risk,
                        explanation=explanation
                    )
                )

            elif hasattr(
                database_service,
                "save_task"
            ):

                database_service.save_task(
                    task=task,
                    action=action,
                    reward=reward,
                    confidence=confidence,
                    risk=risk,
                    explanation=explanation
                )


        # =================================================
        # Response
        # =================================================

        response_data = {

            "status":
                "success",

            "message":
                "Task analyzed successfully.",

            "task":
                task,


            # ---------------------------------------------
            # Task context
            # ---------------------------------------------

            "context": {

                "category":
                    task_context.category,

                "criticality":
                    task_context.criticality,

                "observations":
                    task_context.observations
            },


            # ---------------------------------------------
            # Encoded RL state
            # ---------------------------------------------

            "state":
                state,


            # ---------------------------------------------
            # Decision
            # ---------------------------------------------

            "action":
                action,

            "reward":
                round(
                    float(reward),
                    2
                ),

            "confidence":
                int(
                    confidence
                ),

            "risk":
                risk,


            # ---------------------------------------------
            # Learned Q-values
            # ---------------------------------------------

            "q_values": {

                q_action: round(
                    float(q_value),
                    4
                )

                for q_action, q_value
                in q_values.items()
            },


            # ---------------------------------------------
            # Explainable AI output
            # ---------------------------------------------

            "explanation":
                explanation
        }


        # =================================================
        # Database information
        # =================================================

        if isinstance(
            saved_record,
            dict
        ):

            if "id" in saved_record:

                response_data[
                    "decision_id"
                ] = saved_record[
                    "id"
                ]


            if "created_at" in saved_record:

                response_data[
                    "created_at"
                ] = saved_record[
                    "created_at"
                ]


        # =================================================
        # Success
        # =================================================

        return jsonify(
            response_data
        ), 200


    # =====================================================
    # Validation errors
    # =====================================================

    except ValueError as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400


    except TypeError as error:

        return jsonify({
            "status": "error",
            "message":
                "Invalid task input: "
                + str(error)
        }), 400


    # =====================================================
    # Unexpected errors
    # =====================================================

    except Exception as error:

        print(
            "\n========== DECISION ERROR =========="
        )

        traceback.print_exc()

        print(
            "====================================\n"
        )


        return jsonify({

            "status":
                "error",

            "message":
                "Unable to analyze the task.",

            "details":
                str(error)

        }), 500