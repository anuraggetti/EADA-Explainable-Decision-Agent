"""
E.A.D.A Reward Engine
---------------------
Evaluates how suitable a selected action is for a
particular task state and independently estimates task risk.
"""


class RewardEngine:
    """
    Calculates bounded rewards for task decisions
    and evaluates task risk.
    """

    ACTION_EXECUTE = "Execute Immediately"
    ACTION_ALLOCATE = "Allocate Resources"
    ACTION_SPLIT = "Split Task"
    ACTION_DELAY = "Delay Task"

    VALID_ACTIONS = {
        ACTION_EXECUTE,
        ACTION_ALLOCATE,
        ACTION_SPLIT,
        ACTION_DELAY
    }

    def calculate_reward(
        self,
        state: dict,
        action: str
    ) -> float:
        """
        Calculate how suitable the selected action is.

        Higher reward means the selected action is better
        suited to the current task conditions.
        """

        if action not in self.VALID_ACTIONS:
            raise ValueError(
                f"Unsupported action: {action}"
            )

        priority = state["priority"]
        deadline = state["deadline"]
        complexity = state["complexity"]
        resource = state["resource"]
        success = state["success"]
        failure = state["failure"]

        reward = 0.0

        # -------------------------------------------------
        # General task importance
        # -------------------------------------------------

        reward += priority * 2.5

        # -------------------------------------------------
        # Urgency contribution
        # -------------------------------------------------

        if deadline <= 3:
            reward += 20

        elif deadline <= 6:
            reward += 15

        elif deadline <= 12:
            reward += 10

        elif deadline <= 24:
            reward += 5

        else:
            reward -= 2

        # -------------------------------------------------
        # Historical reliability
        # -------------------------------------------------

        reward += success * 0.15
        reward -= failure * 0.20

        # -------------------------------------------------
        # Action suitability
        # -------------------------------------------------

        if action == self.ACTION_EXECUTE:
            reward += self._execute_reward(
                priority,
                deadline,
                complexity,
                resource
            )

        elif action == self.ACTION_ALLOCATE:
            reward += self._allocate_reward(
                priority,
                complexity,
                resource
            )

        elif action == self.ACTION_SPLIT:
            reward += self._split_reward(
                priority,
                complexity,
                resource
            )

        elif action == self.ACTION_DELAY:
            reward += self._delay_reward(
                priority,
                deadline,
                failure
            )

        return round(
            max(
                -100.0,
                min(100.0, reward)
            ),
            2
        )

    @staticmethod
    def _execute_reward(
        priority: int,
        deadline: int,
        complexity: int,
        resource: int
    ) -> float:

        score = 0.0

        if priority >= 8:
            score += 25
        else:
            score -= 12

        if deadline <= 6:
            score += 20
        else:
            score -= 5

        # High complexity + low resources
        if complexity == 2 and resource == 0:
            score -= 18

        elif resource == 2:
            score += 10

        return score

    @staticmethod
    def _allocate_reward(
        priority: int,
        complexity: int,
        resource: int
    ) -> float:

        score = 5.0

        if priority >= 6:
            score += 12

        if complexity == 2:
            score += 15

        if resource == 0:
            score += 18

        elif resource == 2:
            score -= 5

        return score

    @staticmethod
    def _split_reward(
        priority: int,
        complexity: int,
        resource: int
    ) -> float:

        score = 3.0

        if complexity == 2:
            score += 22

        elif complexity == 1:
            score += 10

        else:
            score -= 8

        if resource == 0:
            score += 10

        if priority >= 9:
            score -= 5

        return score

    @staticmethod
    def _delay_reward(
        priority: int,
        deadline: int,
        failure: float
    ) -> float:

        score = 0.0

        if priority <= 3:
            score += 25

        elif priority <= 5:
            score += 8

        else:
            score -= 25

        if deadline > 24:
            score += 15

        elif deadline <= 6:
            score -= 25

        if failure >= 60:
            score += 5

        return score

    @staticmethod
    def calculate_risk(state: dict) -> str:
        """
        Calculate task risk independently from action reward.

        Risk depends on:
        - priority
        - deadline pressure
        - complexity
        - resource availability
        - historical success
        - historical failure
        """

        priority = state["priority"]
        deadline = state["deadline"]
        complexity = state["complexity"]
        resource = state["resource"]
        success = state["success"]
        failure = state["failure"]

        risk_score = 0

        # -------------------------------------------------
        # Priority risk
        # -------------------------------------------------

        if priority >= 8:
            risk_score += 25

        elif priority >= 6:
            risk_score += 15

        elif priority >= 4:
            risk_score += 8

        # -------------------------------------------------
        # Deadline pressure
        # -------------------------------------------------

        if deadline <= 3:
            risk_score += 30

        elif deadline <= 6:
            risk_score += 22

        elif deadline <= 12:
            risk_score += 15

        elif deadline <= 24:
            risk_score += 8

        # -------------------------------------------------
        # Complexity
        #
        # StateEncoder:
        # 0 = Low
        # 1 = Medium
        # 2 = High
        # -------------------------------------------------

        if complexity == 2:
            risk_score += 25

        elif complexity == 1:
            risk_score += 12

        # -------------------------------------------------
        # Resource availability
        #
        # 0 = Low
        # 1 = Medium
        # 2 = High
        # -------------------------------------------------

        if resource == 0:
            risk_score += 25

        elif resource == 1:
            risk_score += 10

        # -------------------------------------------------
        # Historical failure
        # -------------------------------------------------

        if failure >= 70:
            risk_score += 25

        elif failure >= 50:
            risk_score += 18

        elif failure >= 30:
            risk_score += 10

        # -------------------------------------------------
        # Historical success can reduce risk
        # -------------------------------------------------

        if success >= 80:
            risk_score -= 15

        elif success >= 65:
            risk_score -= 8

        # Keep score within sensible range
        risk_score = max(
            0,
            min(100, risk_score)
        )

        # -------------------------------------------------
        # Risk classification
        # -------------------------------------------------

        if risk_score >= 60:
            return "High"

        elif risk_score >= 30:
            return "Medium"

        return "Low"

    @staticmethod
    def reward_to_risk(reward: float) -> str:
        """
        Legacy compatibility method.

        New decisions should use calculate_risk(state)
        instead of deriving risk from reward.
        """

        if reward >= 65:
            return "Low"

        if reward >= 35:
            return "Medium"

        return "High"