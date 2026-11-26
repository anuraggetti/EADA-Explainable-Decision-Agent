"""
E.A.D.A Explanation Engine
--------------------------
Generates transparent, human-readable and context-aware
explanations for reinforcement-learning task decisions.
"""

from typing import Optional

from explainability.templates import ExplanationTemplates
from explainability.task_context import TaskContextAnalyzer


class ExplanationEngine:
    """
    Converts encoded task conditions and AI output into
    an understandable explanation.

    The engine combines:
    - Task-context analysis
    - Reinforcement-learning state information
    - Reward and risk
    - Confidence
    - Learned Q-values
    - Action-specific guidance
    """

    COMPLEXITY_LABELS = {
        0: "Low",
        1: "Medium",
        2: "High"
    }

    RESOURCE_LABELS = {
        0: "Low",
        1: "Medium",
        2: "High"
    }

    VALID_ACTIONS = {
        "Execute Immediately",
        "Allocate Resources",
        "Split Task",
        "Delay Task"
    }

    def __init__(self):
        """
        Initialize task-context analysis.
        """

        self.context_analyzer = TaskContextAnalyzer()


    # =====================================================
    # FULL EXPLANATION
    # =====================================================

    def generate(
        self,
        task: str,
        state: dict,
        action: str,
        reward: float,
        confidence: Optional[int] = None,
        risk: Optional[str] = None,
        q_values: Optional[dict[str, float]] = None
    ) -> str:
        """
        Generate a detailed explanation for an AI decision.
        """

        self._validate_inputs(
            task=task,
            state=state,
            action=action,
            reward=reward
        )

        normalized_task = task.strip()

        # -------------------------------------------------
        # Analyze task meaning/context
        # -------------------------------------------------

        task_context = self.context_analyzer.analyze(
            normalized_task
        )

        # -------------------------------------------------
        # Risk
        # -------------------------------------------------

        detected_risk = (
            risk
            if risk is not None
            else self._calculate_risk(reward)
        )

        # -------------------------------------------------
        # Parameter-based RL reasons
        # -------------------------------------------------

        reasons = self._build_reasons(
            state=state,
            action=action
        )

        # -------------------------------------------------
        # Build explanation
        # -------------------------------------------------

        explanation_lines = [
            f"Task: {normalized_task}",
            "",
            f"Detected Context: {task_context.category}",
            (
                "Context Criticality: "
                f"{task_context.criticality}"
            ),
            "",
            "Task-specific interpretation:"
        ]

        for observation in task_context.observations:
            explanation_lines.append(
                f"- {observation}"
            )

        explanation_lines.extend([
            "",
            f"Recommended Action: {action}",
            "",
            "Why this action was selected:"
        ])

        for index, reason in enumerate(
            reasons,
            start=1
        ):
            explanation_lines.append(
                f"{index}. {reason}"
            )

        # -------------------------------------------------
        # Action interpretation
        # -------------------------------------------------

        explanation_lines.extend([
            "",
            "Decision interpretation:",
            ExplanationTemplates.get_action_description(
                action
            ),
            "",
            f"Expected Reward: {float(reward):.2f}",
            f"Risk Level: {detected_risk}",
            ExplanationTemplates.get_risk_description(
                detected_risk
            )
        ])

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        if confidence is not None:

            explanation_lines.extend([
                "",
                (
                    "Decision Confidence: "
                    f"{self._normalize_confidence(confidence)}%"
                )
            ])

        # -------------------------------------------------
        # Q-values
        # -------------------------------------------------

        if q_values:

            explanation_lines.extend([
                "",
                "Learned action values:"
            ])

            sorted_q_values = sorted(
                q_values.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for q_action, q_value in sorted_q_values:

                selected_marker = (
                    " (selected)"
                    if q_action == action
                    else ""
                )

                explanation_lines.append(
                    f"- {q_action}: "
                    f"{float(q_value):.2f}"
                    f"{selected_marker}"
                )

        # -------------------------------------------------
        # Context-aware next step
        # -------------------------------------------------

        explanation_lines.extend([
            "",
            "Recommended next step:",
            self._contextual_next_step(
                category=task_context.category,
                action=action
            ),
            "",
            (
                "The recommendation was produced using "
                "task context, priority, deadline, complexity, "
                "resource availability, historical performance, "
                "reward evaluation, and learned Q-values."
            )
        ])

        return "\n".join(
            explanation_lines
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    def generate_summary(
        self,
        state: dict,
        action: str,
        reward: float
    ) -> str:
        """
        Generate a compact explanation.
        """

        risk = self._calculate_risk(
            reward
        )

        main_reason = self._build_reasons(
            state=state,
            action=action
        )[0]

        return (
            f"{action} was recommended because "
            f"{main_reason.lower()} "
            f"The expected reward is "
            f"{float(reward):.2f}, resulting "
            f"in a {risk.lower()} risk assessment."
        )


    # =====================================================
    # STRUCTURED EXPLANATION
    # =====================================================

    def generate_structured(
        self,
        task: str,
        state: dict,
        action: str,
        reward: float,
        confidence: Optional[int] = None,
        risk: Optional[str] = None,
        q_values: Optional[dict[str, float]] = None
    ) -> dict:
        """
        Generate structured explanation information.
        """

        self._validate_inputs(
            task=task,
            state=state,
            action=action,
            reward=reward
        )

        task_context = self.context_analyzer.analyze(
            task
        )

        detected_risk = (
            risk
            if risk is not None
            else self._calculate_risk(reward)
        )

        reasons = self._build_reasons(
            state=state,
            action=action
        )

        result = {

            "task":
                task.strip(),

            "context":
                task_context.category,

            "context_criticality":
                task_context.criticality,

            "context_observations":
                task_context.observations,

            "action":
                action,

            "reward":
                round(
                    float(reward),
                    2
                ),

            "risk":
                detected_risk,

            "reasons":
                reasons,

            "action_description":
                ExplanationTemplates.get_action_description(
                    action
                ),

            "recommended_next_step":
                self._contextual_next_step(
                    category=task_context.category,
                    action=action
                ),

            "summary":
                self.generate_summary(
                    state=state,
                    action=action,
                    reward=reward
                )
        }

        if confidence is not None:

            result["confidence"] = (
                self._normalize_confidence(
                    confidence
                )
            )

        if q_values is not None:

            result["q_values"] = {

                q_action: round(
                    float(q_value),
                    4
                )

                for q_action, q_value
                in q_values.items()
            }

        result["full_explanation"] = (
            self.generate(
                task=task,
                state=state,
                action=action,
                reward=reward,
                confidence=confidence,
                risk=detected_risk,
                q_values=q_values
            )
        )

        return result


    # =====================================================
    # RL STATE REASONS
    # =====================================================

    def _build_reasons(
        self,
        state: dict,
        action: str
    ) -> list[str]:
        """
        Build factual reasons from the encoded task state.
        """

        reasons = [

            self._priority_reason(
                state["priority"]
            ),

            self._deadline_reason(
                state["deadline"]
            ),

            self._complexity_reason(
                state["complexity"]
            ),

            self._resource_reason(
                state["resource"]
            ),

            self._history_reason(
                state["success"],
                state["failure"]
            ),

            self._action_specific_reason(
                state=state,
                action=action
            )
        ]

        return reasons


    # =====================================================
    # PRIORITY
    # =====================================================

    @staticmethod
    def _priority_reason(
        priority: int
    ) -> str:

        if priority >= 8:

            return (
                f"The task has very high priority "
                f"({priority}/10), so it requires "
                f"immediate attention."
            )

        if priority >= 5:

            return (
                f"The task has medium priority "
                f"({priority}/10), so it should "
                f"be handled carefully."
            )

        return (
            f"The task has low priority "
            f"({priority}/10), so other urgent "
            f"tasks may come first."
        )


    # =====================================================
    # DEADLINE
    # =====================================================

    @staticmethod
    def _deadline_reason(
        deadline: int
    ) -> str:

        if deadline <= 3:

            return (
                f"Only {deadline} hour(s) remain, "
                f"making the task extremely urgent."
            )

        if deadline <= 6:

            return (
                f"The deadline is within "
                f"{deadline} hours, so delay could "
                f"create significant risk."
            )

        if deadline <= 12:

            return (
                f"The task has a near-term deadline "
                f"of {deadline} hours."
            )

        if deadline <= 24:

            return (
                f"The deadline is moderate at "
                f"{deadline} hours."
            )

        return (
            f"The deadline is {deadline} hours away, "
            f"providing more scheduling flexibility."
        )


    # =====================================================
    # COMPLEXITY
    # =====================================================

    def _complexity_reason(
        self,
        complexity: int
    ) -> str:

        label = self.COMPLEXITY_LABELS.get(
            complexity,
            "Unknown"
        )

        if complexity == 2:

            return (
                f"Task complexity is "
                f"{label.lower()}, which may require "
                f"planning or division into smaller steps."
            )

        if complexity == 1:

            return (
                f"Task complexity is "
                f"{label.lower()}, so a reasonable "
                f"amount of planning is required."
            )

        return (
            f"Task complexity is "
            f"{label.lower()}, making execution "
            f"comparatively straightforward."
        )


    # =====================================================
    # RESOURCES
    # =====================================================

    def _resource_reason(
        self,
        resource: int
    ) -> str:

        label = self.RESOURCE_LABELS.get(
            resource,
            "Unknown"
        )

        if resource == 2:

            return (
                f"Resource availability is "
                f"{label.lower()}, which supports "
                f"effective execution."
            )

        if resource == 1:

            return (
                f"Resource availability is "
                f"{label.lower()}, so the task can "
                f"proceed with some limitations."
            )

        return (
            f"Resource availability is "
            f"{label.lower()}, which may cause delays "
            f"or reduce completion quality."
        )


    # =====================================================
    # HISTORICAL PERFORMANCE
    # =====================================================

    @staticmethod
    def _history_reason(
        success: float,
        failure: float
    ) -> str:

        if success >= 70 and failure <= 30:

            return (
                f"Historical performance is strong, "
                f"with {success:.1f}% success and "
                f"{failure:.1f}% failure."
            )

        if failure >= 60:

            return (
                f"Historical failure is high at "
                f"{failure:.1f}%, so the task "
                f"requires additional caution."
            )

        if success >= failure:

            return (
                f"Historical performance is moderately "
                f"positive, with {success:.1f}% success "
                f"and {failure:.1f}% failure."
            )

        return (
            f"Historical failure ({failure:.1f}%) "
            f"is greater than historical success "
            f"({success:.1f}%), increasing decision risk."
        )


    # =====================================================
    # ACTION-SPECIFIC REASONING
    # =====================================================

    @staticmethod
    def _action_specific_reason(
        state: dict,
        action: str
    ) -> str:

        priority = state[
            "priority"
        ]

        deadline = state[
            "deadline"
        ]

        complexity = state[
            "complexity"
        ]

        resource = state[
            "resource"
        ]


        if action == "Execute Immediately":

            if (
                priority >= 8
                and deadline <= 6
            ):

                return (
                    "Immediate execution matches the "
                    "combination of high priority and "
                    "a short deadline."
                )

            return (
                "Immediate execution was selected because "
                "the learned reward for acting now is "
                "stronger than postponement."
            )


        if action == "Allocate Resources":

            if resource == 0:

                return (
                    "Resource allocation is appropriate "
                    "because the task currently has "
                    "limited available resources."
                )

            if complexity == 2:

                return (
                    "Additional resources can reduce "
                    "the difficulty created by the "
                    "task's high complexity."
                )

            return (
                "Resource allocation provides additional "
                "support for completing this task "
                "successfully."
            )


        if action == "Split Task":

            if complexity == 2:

                return (
                    "Splitting is suitable because the "
                    "task has high complexity and can "
                    "be handled more effectively as "
                    "smaller subtasks."
                )

            return (
                "Breaking the task into smaller steps "
                "can improve control, progress tracking, "
                "and completion quality."
            )


        if (
            priority <= 4
            and deadline > 24
        ):

            return (
                "Delaying is reasonable because the "
                "task has lower priority and sufficient "
                "time before its deadline."
            )

        return (
            "Delay was selected because the current "
            "state provides a lower expected benefit "
            "for immediate execution."
        )


    # =====================================================
    # CONTEXT-AWARE NEXT STEP
    # =====================================================

    @staticmethod
    def _contextual_next_step(
        category: str,
        action: str
    ) -> str:
        """
        Generate task-domain-specific next-step guidance.
        """

        if category == "Medical Critical":

            if action == "Execute Immediately":
                return (
                    "Begin the required medical response "
                    "without unnecessary delay and ensure "
                    "qualified personnel, equipment, and "
                    "support resources are available."
                )

            if action == "Allocate Resources":
                return (
                    "Secure the required medical personnel, "
                    "equipment, facilities, and supporting "
                    "resources before proceeding."
                )

            if action == "Split Task":
                return (
                    "Coordinate the task across appropriate "
                    "medical roles while maintaining clear "
                    "responsibility and communication."
                )

            return (
                "Reassess the medical urgency before delaying "
                "and ensure that postponement does not create "
                "additional safety risk."
            )


        if category == "Security Investigation":

            if action == "Execute Immediately":
                return (
                    "Begin the investigation promptly, preserve "
                    "relevant evidence, document actions, and "
                    "control access to affected resources."
                )

            if action == "Allocate Resources":
                return (
                    "Assign appropriate investigators, forensic "
                    "tools, technical resources, and evidence-"
                    "handling support before continuing."
                )

            if action == "Split Task":
                return (
                    "Divide the investigation into controlled "
                    "activities such as evidence collection, "
                    "analysis, documentation, and reporting."
                )

            return (
                "Before delaying, preserve available evidence "
                "and confirm that postponement will not increase "
                "security or investigative risk."
            )


        if category == "Emergency Response":

            if action == "Execute Immediately":
                return (
                    "Start the emergency response immediately "
                    "and coordinate personnel, communication, "
                    "equipment, and safety procedures."
                )

            if action == "Allocate Resources":
                return (
                    "Mobilize the required personnel, equipment, "
                    "communication channels, and response resources."
                )

            if action == "Split Task":
                return (
                    "Divide response responsibilities among teams "
                    "while maintaining centralized coordination."
                )

            return (
                "Reassess the emergency conditions before any "
                "delay because consequences may increase over time."
            )


        if category == "Academic":

            if action == "Execute Immediately":
                return (
                    "Start the academic task now, prioritize the "
                    "most important requirements, and track progress "
                    "against the submission deadline."
                )

            if action == "Allocate Resources":
                return (
                    "Gather the required notes, references, tools, "
                    "and study time before continuing the task."
                )

            if action == "Split Task":
                return (
                    "Break the academic work into smaller sections "
                    "and complete them according to priority and "
                    "deadline."
                )

            return (
                "Schedule the task for a later time while keeping "
                "enough buffer before the academic deadline."
            )


        if category == "Software / IT":

            if action == "Execute Immediately":
                return (
                    "Begin technical execution while monitoring "
                    "system impact and keeping testing or rollback "
                    "options available."
                )

            if action == "Allocate Resources":
                return (
                    "Assign the required technical personnel, "
                    "computing resources, tools, and system access."
                )

            if action == "Split Task":
                return (
                    "Separate the work into manageable technical "
                    "stages such as diagnosis, implementation, "
                    "testing, and deployment."
                )

            return (
                "Schedule the technical task for later and verify "
                "that the delay will not create additional system "
                "impact."
            )


        if category == "Business / Management":

            if action == "Execute Immediately":
                return (
                    "Begin the task and coordinate the required "
                    "stakeholders, information, and deadlines."
                )

            if action == "Allocate Resources":
                return (
                    "Assign the required people, budget, information, "
                    "or operational resources before proceeding."
                )

            if action == "Split Task":
                return (
                    "Divide the work into clear responsibilities "
                    "and track each part against the overall goal."
                )

            return (
                "Reschedule the task while ensuring important "
                "stakeholder commitments and deadlines remain protected."
            )


        if category == "Personal / Routine":

            if action == "Execute Immediately":
                return (
                    "Start the task now if the required time and "
                    "resources are conveniently available."
                )

            if action == "Allocate Resources":
                return (
                    "Gather the basic resources required to complete "
                    "the routine task efficiently."
                )

            if action == "Split Task":
                return (
                    "Break the routine task into smaller manageable "
                    "steps and complete them progressively."
                )

            return (
                "Schedule the task for a more convenient time because "
                "its immediate operational impact is limited."
            )


        # General fallback

        return (
            ExplanationTemplates.get_action_guidance(
                action
            )
        )


    # =====================================================
    # RISK
    # =====================================================

    @staticmethod
    def _calculate_risk(
        reward: float
    ) -> str:
        """
        Convert reward into a risk label.
        """

        reward_value = float(
            reward
        )

        if reward_value >= 65:
            return "Low"

        if reward_value >= 35:
            return "Medium"

        return "High"


    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def _normalize_confidence(
        confidence: int
    ) -> int:

        return int(
            max(
                0,
                min(
                    100,
                    round(
                        float(confidence)
                    )
                )
            )
        )


    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate_inputs(
        self,
        task: str,
        state: dict,
        action: str,
        reward: float
    ) -> None:

        if (
            not isinstance(
                task,
                str
            )
            or not task.strip()
        ):

            raise ValueError(
                "Task description cannot be empty."
            )


        if not isinstance(
            state,
            dict
        ):

            raise ValueError(
                "State must be a dictionary."
            )


        required_fields = {
            "priority",
            "deadline",
            "complexity",
            "resource",
            "success",
            "failure"
        }


        missing_fields = (
            required_fields
            - set(
                state.keys()
            )
        )


        if missing_fields:

            formatted_fields = ", ".join(
                sorted(
                    missing_fields
                )
            )

            raise ValueError(
                "Explanation state is missing fields: "
                f"{formatted_fields}"
            )


        if action not in self.VALID_ACTIONS:

            raise ValueError(
                f"Unsupported action: {action}"
            )


        try:

            float(
                reward
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                "Reward must be a valid number."
            ) from error