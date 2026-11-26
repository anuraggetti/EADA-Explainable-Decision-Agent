"""
E.A.D.A Service Container
-------------------------
Creates and stores shared application services.
"""

from agent.state_encoder import StateEncoder
from agent.reward_engine import RewardEngine
from agent.q_learning import QLearningAgent
from agent.trainer import Trainer

from explainability.explanation_engine import ExplanationEngine

from database.database_service import DatabaseService

from analytics.graphs import Graphs
from analytics.metrics import Metrics


class ServiceContainer:
    """
    Central container for shared application services.
    """

    def __init__(self):

        self.encoder = StateEncoder()

        self.reward_engine = RewardEngine()

        self.agent = QLearningAgent()

        self.database = DatabaseService()

        self.explanation = ExplanationEngine()

        self.graphs = Graphs()

        self.metrics = Metrics()

        self.trainer = Trainer(
            encoder=self.encoder,
            reward_engine=self.reward_engine,
            agent=self.agent
        )


services = ServiceContainer()