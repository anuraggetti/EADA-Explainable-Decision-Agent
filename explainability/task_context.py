"""
E.A.D.A Task Context Analyzer
-----------------------------
Classifies a task description into a broad operational category
and produces context-aware observations for explainable decisions.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TaskContext:
    """
    Represents the interpreted context of a task.
    """

    category: str
    criticality: str
    observations: List[str]


class TaskContextAnalyzer:
    """
    Lightweight rule-based task context classifier.

    This keeps the system:
    - Explainable
    - Deterministic
    - Fast
    - Fully offline
    """

    CATEGORY_KEYWORDS = {

        "Medical Critical": [
            "surgery",
            "patient",
            "hospital",
            "medical",
            "doctor",
            "nurse",
            "operation",
            "emergency room",
            "injury",
            "treatment",
            "health",
            "icu",
            "therapy",
            "diagnosis"
        ],

        "Security Investigation": [
            "crime",
            "crime scene",
            "investigate",
            "investigation",
            "forensic",
            "forensics",
            "evidence",
            "breach",
            "security breach",
            "cyber attack",
            "cyberattack",
            "attack",
            "incident",
            "malware",
            "ransomware",
            "intrusion",
            "hack",
            "hacking",
            "cybersecurity",
            "security incident",
            "digital evidence",
            "threat"
        ],

        "Emergency Response": [
            "fire",
            "accident",
            "disaster",
            "rescue",
            "emergency",
            "evacuation",
            "flood",
            "earthquake",
            "explosion",
            "ambulance",
            "hazard",
            "crisis"
        ],

        "Academic": [
            "homework",
            "home work",
            "assignment",
            "exam",
            "study",
            "project report",
            "college project",
            "final year project",
            "mini project",
            "academic project",
            "research project",
            "college",
            "class",
            "presentation",
            "seminar",
            "research paper",
            "lab record",
            "viva",
            "thesis"
        ],

        "Software / IT": [
            "project build",
            "build project",
            "software project",
            "application project",
            "web project",
            "app project",
            "develop project",
            "develop application",
            "develop app",
            "build application",
            "build app",
            "project development",
            "implementation",
            "prototype",
            "server",
            "software",
            "application",
            "website",
            "database",
            "bug",
            "deployment",
            "code",
            "coding",
            "program",
            "programming",
            "network",
            "patch",
            "system",
            "maintenance",
            "api",
            "backend",
            "frontend",
            "full stack",
            "machine learning",
            "ai model"
        ],

        "Business / Management": [
            "meeting",
            "client",
            "business",
            "management",
            "budget",
            "report",
            "sales",
            "marketing",
            "presentation",
            "deadline",
            "proposal",
            "finance",
            "strategy",
            "stakeholder"
        ],

        "Personal / Routine": [
            "laundry",
            "shopping",
            "cleaning",
            "exercise",
            "gym",
            "cook",
            "cooking",
            "travel",
            "groceries",
            "household",
            "clean room",
            "buy groceries"
        ]
    }

    CATEGORY_PRIORITY = {
        "Medical Critical": 7,
        "Emergency Response": 6,
        "Security Investigation": 5,
        "Software / IT": 4,
        "Academic": 3,
        "Business / Management": 2,
        "Personal / Routine": 1
    }

    def analyze(
        self,
        task: str
    ) -> TaskContext:
        """
        Analyze task description and return contextual information.
        """

        normalized_task = (
            str(task)
            .strip()
            .lower()
        )

        category = self._detect_category(
            normalized_task
        )

        criticality = self._detect_criticality(
            category,
            normalized_task
        )

        observations = self._build_observations(
            category,
            criticality,
            normalized_task
        )

        return TaskContext(
            category=category,
            criticality=criticality,
            observations=observations
        )

    def _detect_category(
        self,
        task: str
    ) -> str:
        """
        Find the best matching category using weighted keyword matches.
        """

        best_category = "General Task"
        best_score = 0
        best_priority = 0

        for category, keywords in (
            self.CATEGORY_KEYWORDS.items()
        ):

            score = 0

            for keyword in keywords:

                if keyword in task:

                    # Multi-word phrases receive slightly more weight.
                    if " " in keyword:
                        score += 2

                    else:
                        score += 1

            category_priority = (
                self.CATEGORY_PRIORITY.get(
                    category,
                    0
                )
            )

            if (
                score > best_score
                or (
                    score == best_score
                    and score > 0
                    and category_priority > best_priority
                )
            ):

                best_score = score
                best_priority = category_priority
                best_category = category

        # -------------------------------------------------
        # Additional fallback logic
        # -------------------------------------------------

        if best_category == "General Task":

            if (
                "project" in task
                and any(
                    term in task
                    for term in [
                        "build",
                        "develop",
                        "development",
                        "implementation",
                        "software",
                        "app",
                        "application",
                        "website",
                        "system"
                    ]
                )
            ):

                return "Software / IT"

            if "project" in task:

                return "Academic"

        return best_category

    @staticmethod
    def _detect_criticality(
        category: str,
        task: str
    ) -> str:
        """
        Estimate contextual criticality.
        """

        if category in {
            "Medical Critical",
            "Emergency Response"
        }:
            return "Critical"

        if category == "Security Investigation":

            severe_terms = [
                "breach",
                "attack",
                "crime scene",
                "malware",
                "ransomware",
                "intrusion",
                "forensic",
                "evidence",
                "threat"
            ]

            if any(
                term in task
                for term in severe_terms
            ):
                return "High"

            return "Moderate"

        if category == "Software / IT":

            high_impact_terms = [
                "production",
                "critical server",
                "security patch",
                "database failure",
                "system outage",
                "deployment failure",
                "major bug",
                "network failure"
            ]

            if any(
                term in task
                for term in high_impact_terms
            ):
                return "High"

            return "Moderate"

        if category == "Business / Management":
            return "Moderate"

        if category in {
            "Academic",
            "Personal / Routine"
        }:
            return "Low"

        return "Moderate"

    @staticmethod
    def _build_observations(
        category: str,
        criticality: str,
        task: str
    ) -> List[str]:
        """
        Generate task-specific contextual observations.
        """

        observations = []

        if category == "Medical Critical":

            observations.append(
                "This is a medical task where delay, insufficient "
                "resources, or execution errors may affect patient safety."
            )

            observations.append(
                "Qualified personnel, equipment availability, and "
                "careful coordination are especially important."
            )

        elif category == "Security Investigation":

            observations.append(
                "This task involves investigation or security handling, "
                "so evidence integrity, specialist expertise, and timely "
                "response may be important."
            )

            observations.append(
                "Poor coordination or delayed action could increase "
                "operational, security, or investigative impact."
            )

        elif category == "Emergency Response":

            observations.append(
                "This is an emergency-response task where delay may "
                "increase consequences and immediate coordination is important."
            )

            observations.append(
                "Personnel, equipment, communication, and response speed "
                "are key execution factors."
            )

        elif category == "Academic":

            observations.append(
                "This is an academic task where scheduling, workload "
                "management, milestone planning, and deadline control "
                "are the main concerns."
            )

            observations.append(
                "The task can often be improved by dividing the work "
                "into smaller deliverables and prioritizing important sections."
            )

        elif category == "Software / IT":

            observations.append(
                "This is a software or technical development task where "
                "design effort, implementation complexity, dependencies, "
                "testing, and resource availability may affect execution."
            )

            observations.append(
                "A structured development plan with clear modules, "
                "testing checkpoints, and technical resource allocation "
                "can improve completion quality."
            )

        elif category == "Business / Management":

            observations.append(
                "This is a business or management task where coordination, "
                "timelines, stakeholder availability, and resource planning "
                "are important."
            )

            observations.append(
                "Execution sequencing and communication quality may "
                "significantly influence the final outcome."
            )

        elif category == "Personal / Routine":

            observations.append(
                "This is a routine personal task with relatively low "
                "operational consequence."
            )

            observations.append(
                "Scheduling convenience and available time are likely "
                "more important than urgent resource allocation."
            )

        else:

            observations.append(
                "This task does not strongly match a predefined domain, "
                "so the recommendation primarily depends on its priority, "
                "deadline, complexity, resources, and historical performance."
            )

        observations.append(
            f"Detected task context: {category} "
            f"with {criticality.lower()} contextual criticality."
        )

        return observations