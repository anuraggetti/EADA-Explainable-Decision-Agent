"""
E.A.D.A Policy Engine
---------------------
Provides a sensible fallback decision when the agent
has not yet learned enough about a task state.
"""


class Policy:
    """
    Rule-based fallback policy.
    """

    ACTION_EXECUTE = "Execute Immediately"
    ACTION_ALLOCATE = "Allocate Resources"
    ACTION_SPLIT = "Split Task"
    ACTION_DELAY = "Delay Task"

    def decide(self, state: dict) -> str:
        """
        Select an initial action using interpretable rules.

        Args:
            state:
                Encoded task state.

        Returns:
            Recommended action.
        """

        priority = state["priority"]
        deadline = state["deadline"]
        complexity = state["complexity"]
        resource = state["resource"]
        success = state["success"]
        failure = state["failure"]

        urgent = deadline <= 6
        limited_resources = resource == 0
        complex_task = complexity == 2
        strong_history = success >= 70 and failure <= 30

        if priority >= 8 and urgent:
            return self.ACTION_EXECUTE

        if (
            priority >= 7
            and (
                limited_resources
                or complex_task
            )
        ):
            return self.ACTION_ALLOCATE

        if (
            complexity == 2
            and priority >= 4
        ):
            return self.ACTION_SPLIT

        if (
            priority >= 6
            or strong_history
        ):
            return self.ACTION_ALLOCATE

        if priority >= 4:
            return self.ACTION_SPLIT

        return self.ACTION_DELAY