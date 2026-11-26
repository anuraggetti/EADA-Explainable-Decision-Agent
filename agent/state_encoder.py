"""
E.A.D.A State Encoder
---------------------
Validates and converts raw task information into a
numerical state understood by the Q-Learning agent.

The encoder preserves exact values for explanation,
reward, and risk calculations while also generating
generalized state bands for reinforcement learning.
"""

from typing import Any


class StateEncoder:
    """
    Converts user and dataset input into a consistent state.

    Raw values are preserved for:
    - Reward calculation
    - Risk calculation
    - Explanation generation

    Generalized bands are created for:
    - Q-table state matching
    - Better learning generalization
    - Reducing unseen-state problems
    """

    COMPLEXITY_MAP = {
        "low": 0,
        "medium": 1,
        "high": 2
    }

    RESOURCE_MAP = {
        "low": 0,
        "medium": 1,
        "high": 2
    }


    def encode(
        self,
        priority: Any,
        deadline: Any,
        complexity: Any,
        resources: Any,
        success: Any,
        failure: Any
    ) -> dict:
        """
        Validate and encode task parameters.

        Returns:
            Dictionary containing both exact task
            values and generalized RL state bands.

        Raises:
            ValueError:
                When one or more values are invalid.
        """

        # =================================================
        # Convert numerical inputs
        # =================================================

        priority_value = self._to_integer(
            priority,
            "Priority"
        )

        deadline_value = self._to_integer(
            deadline,
            "Deadline"
        )

        success_value = self._to_float(
            success,
            "Historical success"
        )

        failure_value = self._to_float(
            failure,
            "Historical failure"
        )


        # =================================================
        # Validate numerical inputs
        # =================================================

        if not 1 <= priority_value <= 10:

            raise ValueError(
                "Priority must be between 1 and 10."
            )


        if deadline_value <= 0:

            raise ValueError(
                "Deadline must be greater than 0 hours."
            )


        if not 0 <= success_value <= 100:

            raise ValueError(
                "Historical success must be between "
                "0 and 100."
            )


        if not 0 <= failure_value <= 100:

            raise ValueError(
                "Historical failure must be between "
                "0 and 100."
            )


        # =================================================
        # Encode categorical inputs
        # =================================================

        complexity_value = self._encode_category(
            complexity,
            self.COMPLEXITY_MAP,
            "Complexity"
        )

        resource_value = self._encode_category(
            resources,
            self.RESOURCE_MAP,
            "Resource availability"
        )


        # =================================================
        # Create generalized RL bands
        # =================================================

        priority_band = self._priority_band(
            priority_value
        )

        deadline_band = self._deadline_band(
            deadline_value
        )

        success_band = self._success_band(
            success_value
        )

        failure_band = self._failure_band(
            failure_value
        )


        # =================================================
        # Return complete state
        # =================================================

        return {

            # ---------------------------------------------
            # Exact values
            #
            # Used by reward, risk and explanation engines.
            # ---------------------------------------------

            "priority":
                priority_value,

            "deadline":
                deadline_value,

            "complexity":
                complexity_value,

            "resource":
                resource_value,

            "success":
                round(
                    success_value,
                    2
                ),

            "failure":
                round(
                    failure_value,
                    2
                ),


            # ---------------------------------------------
            # Generalized RL values
            #
            # These will be used when generating
            # Q-table state keys.
            # ---------------------------------------------

            "priority_band":
                priority_band,

            "deadline_band":
                deadline_band,

            "success_band":
                success_band,

            "failure_band":
                failure_band
        }


    # =====================================================
    # Priority Band
    # =====================================================

    @staticmethod
    def _priority_band(
        priority: int
    ) -> int:
        """
        Convert priority 1-10 into four generalized groups.

        0 = Low
        1 = Medium
        2 = High
        3 = Critical
        """

        if priority <= 3:
            return 0

        if priority <= 5:
            return 1

        if priority <= 7:
            return 2

        return 3


    # =====================================================
    # Deadline Band
    # =====================================================

    @staticmethod
    def _deadline_band(
        deadline: int
    ) -> int:
        """
        Group deadline hours into generalized urgency bands.

        0 = Critical       (1-3 hours)
        1 = Urgent         (4-12 hours)
        2 = Near-term      (13-24 hours)
        3 = Flexible       (25-72 hours)
        4 = Long-term      (73+ hours)
        """

        if deadline <= 3:
            return 0

        if deadline <= 12:
            return 1

        if deadline <= 24:
            return 2

        if deadline <= 72:
            return 3

        return 4


    # =====================================================
    # Success Band
    # =====================================================

    @staticmethod
    def _success_band(
        success: float
    ) -> int:
        """
        Generalize historical success percentage.

        0 = Low
        1 = Moderate
        2 = High
        3 = Very High
        """

        if success < 40:
            return 0

        if success < 70:
            return 1

        if success < 85:
            return 2

        return 3


    # =====================================================
    # Failure Band
    # =====================================================

    @staticmethod
    def _failure_band(
        failure: float
    ) -> int:
        """
        Generalize historical failure percentage.

        0 = Low
        1 = Moderate
        2 = High
        3 = Very High
        """

        if failure <= 15:
            return 0

        if failure <= 35:
            return 1

        if failure <= 60:
            return 2

        return 3


    # =====================================================
    # Number Conversion
    # =====================================================

    @staticmethod
    def _to_integer(
        value: Any,
        field_name: str
    ) -> int:
        """
        Convert a value to an integer.
        """

        try:

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                f"{field_name} must be a valid number."
            ) from error


    @staticmethod
    def _to_float(
        value: Any,
        field_name: str
    ) -> float:
        """
        Convert a value to a floating-point number.
        """

        try:

            return float(value)

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                f"{field_name} must be a valid number."
            ) from error


    # =====================================================
    # Category Encoding
    # =====================================================

    @staticmethod
    def _encode_category(
        value: Any,
        category_map: dict[str, int],
        field_name: str
    ) -> int:
        """
        Convert a text category into its numerical value.
        """

        normalized_value = (
            str(value)
            .strip()
            .lower()
        )


        if normalized_value not in category_map:

            allowed_values = ", ".join(
                item.title()
                for item in category_map
            )

            raise ValueError(
                f"{field_name} must be one of: "
                f"{allowed_values}."
            )


        return category_map[
            normalized_value
        ]