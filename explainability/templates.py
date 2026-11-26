"""
E.A.D.A Explanation Templates
-----------------------------
Stores reusable explanation text for each supported
decision action.
"""


class ExplanationTemplates:
    """
    Human-readable action descriptions and recommendations.
    """

    ACTION_DESCRIPTIONS = {
        "Execute Immediately": (
            "The task should begin immediately because its "
            "current urgency and importance make delay risky."
        ),

        "Allocate Resources": (
            "Additional people, tools, time, or computing "
            "resources should be assigned to improve the "
            "probability of successful completion."
        ),

        "Split Task": (
            "The task should be divided into smaller and more "
            "manageable subtasks to reduce execution difficulty."
        ),

        "Delay Task": (
            "The task can be postponed because current conditions "
            "do not justify immediate execution."
        )
    }

    ACTION_GUIDANCE = {
        "Execute Immediately": (
            "Start the task now, monitor progress closely, and "
            "resolve blockers as early as possible."
        ),

        "Allocate Resources": (
            "Identify the missing resources, assign them to the "
            "task, and review the decision after allocation."
        ),

        "Split Task": (
            "Break the task into clear subtasks, assign priorities, "
            "and complete the most urgent part first."
        ),

        "Delay Task": (
            "Schedule the task for a later time and reassess it if "
            "its priority, deadline, or resource availability changes."
        )
    }

    RISK_DESCRIPTIONS = {
        "Low": (
            "The recommendation is well aligned with the current "
            "task conditions."
        ),

        "Medium": (
            "The recommendation is reasonable, but the task should "
            "be monitored for changes."
        ),

        "High": (
            "The recommendation has uncertainty or potential "
            "execution challenges and should be reviewed carefully."
        )
    }

    @classmethod
    def get_action_description(
        cls,
        action: str
    ) -> str:
        """
        Return the explanation associated with an action.
        """

        return cls.ACTION_DESCRIPTIONS.get(
            action,
            "The selected action is based on the current task state."
        )

    @classmethod
    def get_action_guidance(
        cls,
        action: str
    ) -> str:
        """
        Return practical guidance associated with an action.
        """

        return cls.ACTION_GUIDANCE.get(
            action,
            "Review the task conditions before proceeding."
        )

    @classmethod
    def get_risk_description(
        cls,
        risk: str
    ) -> str:
        """
        Return the explanation associated with a risk level.
        """

        return cls.RISK_DESCRIPTIONS.get(
            risk,
            "The risk level should be interpreted with the current "
            "task conditions."
        )