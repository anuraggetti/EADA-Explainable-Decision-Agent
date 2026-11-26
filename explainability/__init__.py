"""
E.A.D.A Explainability Module
-----------------------------
Generates clear, human-readable explanations for
reinforcement-learning task decisions.
"""

from explainability.explanation_engine import ExplanationEngine
from explainability.templates import ExplanationTemplates

__all__ = [
    "ExplanationEngine",
    "ExplanationTemplates"
]