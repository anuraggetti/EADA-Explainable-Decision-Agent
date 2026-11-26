"""
E.A.D.A Q-Learning Agent
------------------------
Learns action values for generalized task states and
generalizes recommendations to similar unseen states.
"""

import random
from typing import Optional

from agent.model_manager import ModelManager
from agent.policy import Policy
from config import Config


class QLearningAgent:
    """
    Q-Learning agent for intelligent task decisions.

    Exact learned states are preferred.

    When an unseen state is provided during analysis,
    the agent searches for the nearest learned state
    instead of returning four zero Q-values.
    """

    ACTIONS = (
        "Execute Immediately",
        "Allocate Resources",
        "Split Task",
        "Delay Task"
    )

    def __init__(
        self,
        learning_rate: Optional[float] = None,
        discount_factor: Optional[float] = None,
        epsilon: Optional[float] = None
    ):

        self.learning_rate = (
            Config.LEARNING_RATE
            if learning_rate is None
            else float(learning_rate)
        )

        self.discount_factor = (
            Config.DISCOUNT_FACTOR
            if discount_factor is None
            else float(discount_factor)
        )

        self.initial_epsilon = (
            Config.EPSILON
            if epsilon is None
            else float(epsilon)
        )

        self.epsilon = self.initial_epsilon

        self.minimum_epsilon = 0.02
        self.epsilon_decay = 0.985

        self.actions = list(
            self.ACTIONS
        )

        self.policy = Policy()

        loaded_table = (
            ModelManager.load_q_table()
        )

        self.q_table = (
            self._normalize_q_table(
                loaded_table
            )
        )


    # =====================================================
    # STATE REPRESENTATION
    # =====================================================

    @staticmethod
    def state_to_key(
        state: dict
    ) -> tuple:
        """
        Convert encoded task state into generalized
        Q-table representation.
        """

        return (
            int(state["priority_band"]),
            int(state["deadline_band"]),
            int(state["complexity"]),
            int(state["resource"]),
            int(state["success_band"]),
            int(state["failure_band"])
        )


    # =====================================================
    # ACTION SELECTION
    # =====================================================

    def choose_action(
        self,
        state: dict,
        training: bool = False
    ) -> str:
        """
        Select an action.

        Training:
            Uses the exact generalized state and
            epsilon-greedy exploration.

        Analysis:
            Uses the exact learned state when possible.
            Otherwise uses the nearest learned state.
        """

        requested_key = self.state_to_key(
            state
        )

        # -------------------------------------------------
        # Training mode
        # -------------------------------------------------

        if training:

            self._ensure_state(
                requested_key
            )

            if random.random() < self.epsilon:

                return random.choice(
                    self.actions
                )

            q_values = self.q_table[
                requested_key
            ]

            if self._all_zero(
                q_values
            ):

                return self.policy.decide(
                    state
                )

            return self._best_action(
                state,
                q_values
            )


        # -------------------------------------------------
        # Analysis mode
        # -------------------------------------------------

        matched_key, _, exact_match = (
            self._find_best_learned_state(
                requested_key
            )
        )


        # No useful learned states exist.
        if matched_key is None:

            return self.policy.decide(
                state
            )


        q_values = self.q_table[
            matched_key
        ]


        # Exact or similar state now uses learned values.
        return self._best_action(
            state,
            q_values
        )


    # =====================================================
    # BEST ACTION
    # =====================================================

    def _best_action(
        self,
        state: dict,
        q_values: dict
    ) -> str:
        """
        Select action having the highest Q-value.

        Policy is used only as deterministic tie breaker.
        """

        maximum_q = max(
            q_values.values()
        )

        best_actions = [
            action
            for action, value
            in q_values.items()
            if value == maximum_q
        ]

        policy_action = (
            self.policy.decide(
                state
            )
        )

        if policy_action in best_actions:

            return policy_action

        return best_actions[0]


    # =====================================================
    # Q-LEARNING UPDATE
    # =====================================================

    def update_q_value(
        self,
        state: dict,
        action: str,
        reward: float,
        next_state: Optional[dict] = None,
        terminal: bool = True
    ) -> float:
        """
        Update Q-value for a training state.
        """

        if action not in self.actions:

            raise ValueError(
                f"Unsupported action: {action}"
            )


        current_key = self.state_to_key(
            state
        )

        self._ensure_state(
            current_key
        )


        old_q = (
            self.q_table[
                current_key
            ][
                action
            ]
        )


        if terminal or next_state is None:

            target = float(
                reward
            )

        else:

            next_key = self.state_to_key(
                next_state
            )

            self._ensure_state(
                next_key
            )

            next_max = max(
                self.q_table[
                    next_key
                ].values()
            )

            target = (
                float(reward)
                + self.discount_factor
                * next_max
            )


        new_q = (
            old_q
            + self.learning_rate
            * (
                target - old_q
            )
        )


        updated_value = round(
            new_q,
            4
        )


        self.q_table[
            current_key
        ][
            action
        ] = updated_value


        return updated_value


    # =====================================================
    # CONFIDENCE
    # =====================================================

    def get_confidence(
        self,
        state: dict,
        action: Optional[str] = None
    ) -> int:
        """
        Calculate dynamic decision confidence.

        Confidence depends on:

        - Learned Q-value strength
        - Difference from second-best action
        - Exact vs nearest-state matching
        - Similarity to the learned state
        - Agreement with fallback policy
        """

        requested_key = self.state_to_key(
            state
        )


        matched_key, distance, exact_match = (
            self._find_best_learned_state(
                requested_key
            )
        )


        # No trained information exists.
        if matched_key is None:

            return 50


        q_values = self.q_table[
            matched_key
        ]


        if action is None:

            action = self.choose_action(
                state,
                training=False
            )


        selected_value = float(
            q_values.get(
                action,
                0.0
            )
        )


        sorted_values = sorted(
            [
                float(value)
                for value
                in q_values.values()
            ],
            reverse=True
        )


        if not sorted_values:

            return 50


        best_value = (
            sorted_values[0]
        )

        second_best = (
            sorted_values[1]
            if len(sorted_values) > 1
            else 0.0
        )


        # -------------------------------------------------
        # Strength of selected action
        # -------------------------------------------------

        q_strength = max(
            0.0,
            min(
                1.0,
                selected_value / 100.0
            )
        )


        # -------------------------------------------------
        # Separation from alternatives
        # -------------------------------------------------

        margin = max(
            0.0,
            best_value - second_best
        )

        margin_strength = max(
            0.0,
            min(
                1.0,
                margin / 40.0
            )
        )


        # -------------------------------------------------
        # State similarity
        # -------------------------------------------------

        if exact_match:

            similarity = 1.0

        else:

            similarity = max(
                0.0,
                1.0 - (
                    distance / 12.0
                )
            )


        # -------------------------------------------------
        # Policy agreement
        # -------------------------------------------------

        policy_action = (
            self.policy.decide(
                state
            )
        )

        policy_agreement = (
            1.0
            if policy_action == action
            else 0.0
        )


        # -------------------------------------------------
        # Weighted confidence
        # -------------------------------------------------

        confidence = (

            40

            + q_strength * 25

            + margin_strength * 18

            + similarity * 12

            + policy_agreement * 5
        )


        # Nearest-state decisions should never claim
        # extreme certainty.

        maximum_confidence = (
            98
            if exact_match
            else 90
        )


        return int(
            round(
                max(
                    50,
                    min(
                        maximum_confidence,
                        confidence
                    )
                )
            )
        )


    # =====================================================
    # GET Q-VALUES
    # =====================================================

    def get_state_values(
        self,
        state: dict
    ) -> dict[str, float]:
        """
        Return learned Q-values.

        When the exact state is not learned, return values
        from the nearest trained state instead of returning
        four zeros.
        """

        requested_key = (
            self.state_to_key(
                state
            )
        )


        matched_key, _, _ = (
            self._find_best_learned_state(
                requested_key
            )
        )


        if matched_key is None:

            return {
                action: 0.0
                for action
                in self.actions
            }


        return dict(
            self.q_table[
                matched_key
            ]
        )


    # =====================================================
    # NEAREST-STATE GENERALIZATION
    # =====================================================

    def _find_best_learned_state(
        self,
        requested_key: tuple
    ) -> tuple[
        Optional[tuple],
        float,
        bool
    ]:
        """
        Find the closest learned Q-table state.

        Returns:
            matched state key
            distance
            exact-match flag
        """

        # -------------------------------------------------
        # Exact learned state
        # -------------------------------------------------

        if (
            requested_key in self.q_table
            and not self._all_zero(
                self.q_table[
                    requested_key
                ]
            )
        ):

            return (
                requested_key,
                0.0,
                True
            )


        best_key = None
        best_distance = float(
            "inf"
        )


        # -------------------------------------------------
        # Search only genuinely learned states
        # -------------------------------------------------

        for candidate_key, q_values in (
            self.q_table.items()
        ):

            if self._all_zero(
                q_values
            ):
                continue


            distance = (
                self._state_distance(
                    requested_key,
                    candidate_key
                )
            )


            if distance < best_distance:

                best_distance = distance

                best_key = (
                    candidate_key
                )


        if best_key is None:

            return (
                None,
                float("inf"),
                False
            )


        return (
            best_key,
            best_distance,
            False
        )


    # =====================================================
    # STATE DISTANCE
    # =====================================================

    @staticmethod
    def _state_distance(
        state_a: tuple,
        state_b: tuple
    ) -> float:
        """
        Calculate weighted distance between generalized states.

        Tuple order:

        0 priority band
        1 deadline band
        2 complexity
        3 resources
        4 success band
        5 failure band
        """

        weights = (
            2.0,   # priority
            2.0,   # deadline
            1.5,   # complexity
            1.5,   # resources
            1.0,   # success
            1.0    # failure
        )


        distance = 0.0


        for index, weight in enumerate(
            weights
        ):

            distance += (
                abs(
                    state_a[index]
                    - state_b[index]
                )
                * weight
            )


        return distance


    # =====================================================
    # ZERO STATE CHECK
    # =====================================================

    @staticmethod
    def _all_zero(
        q_values: dict
    ) -> bool:
        """
        Return True when no action has learned value.
        """

        return all(
            abs(
                float(value)
            ) < 0.000001

            for value
            in q_values.values()
        )


    # =====================================================
    # EXPLORATION
    # =====================================================

    def decay_exploration(
        self
    ) -> None:

        self.epsilon = max(
            self.minimum_epsilon,
            self.epsilon
            * self.epsilon_decay
        )


    def reset_exploration(
        self
    ) -> None:

        self.epsilon = (
            self.initial_epsilon
        )


    # =====================================================
    # SAVE MODEL
    # =====================================================

    def save(
        self
    ) -> None:

        ModelManager.save_q_table(
            self.q_table
        )


    # =====================================================
    # TABLE INFORMATION
    # =====================================================

    def get_q_table_size(
        self
    ) -> int:

        return len(
            self.q_table
        )


    # =====================================================
    # INITIALIZE STATE
    # =====================================================

    def _ensure_state(
        self,
        key: tuple
    ) -> None:

        if key not in self.q_table:

            self.q_table[
                key
            ] = {

                action: 0.0

                for action
                in self.actions
            }


    # =====================================================
    # NORMALIZE LOADED TABLE
    # =====================================================

    def _normalize_q_table(
        self,
        q_table: dict
    ) -> dict:

        normalized_table = {}


        for state, stored_actions in (
            q_table.items()
        ):

            if not isinstance(
                state,
                tuple
            ):
                continue


            if len(state) != 6:
                continue


            normalized_table[
                state
            ] = {

                action: float(
                    stored_actions.get(
                        action,
                        0.0
                    )
                )

                for action
                in self.actions
            }


        return normalized_table