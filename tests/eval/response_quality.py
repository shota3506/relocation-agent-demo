"""Relocation Agent LLM-as-a-judge for `relocation_concierge_quality` metric."""

import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Ensure corp mTLS fallback doesn't trigger certificate path errors
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"


class _EvaluationVerdict(BaseModel):
    score: int = Field(description="Score from 1 to 5 based on rubric criteria.")
    task_achievement: str = Field(description="Evaluation of user goal fulfillment.")
    geospatial_accuracy: str = Field(
        description="Evaluation of commute equity, area livability, or cost calculations."
    )
    dislikes_enforcement: str = Field(
        description="Whether user dislikes/deal-breakers were strictly respected."
    )
    source_citation: str = Field(
        description="Whether direct source URLs or concrete evidence were provided."
    )
    explanation: str = Field(description="Summary explanation of the overall score.")


def evaluate(instance: dict) -> dict:
    """Evaluates the quality, accuracy, delegation, and constraint compliance of the agent response."""
    prompt_text = str(instance.get("prompt", ""))
    response_text = str(instance.get("response", ""))
    agent_data = str(instance.get("agent_data", ""))
    reference = instance.get("reference")

    eval_rubric = """\
You are an expert Quality Assurance Judge evaluating a specialized AI Relocation Concierge multi-agent system.
Grade the agent's performance on a 1-5 scale according to the following strict criteria:

### Scoring Guidelines:
- **5 (Excellent)**:
  - Completely satisfies the user's inquiry with structured, professional, and empathetic guidance.
  - Appropriately executes specialized tasks (area transit analysis, real property exploration with direct URLs, or itemized move-in cost calculations).
  - Strictly respects all user constraints and dislikes (e.g. 1st floor exclusions, separate bath/toilet).
  - Clear, concrete numbers and transparent reasoning.
- **4 (Good)**:
  - Fulfills the main user request accurately with helpful details.
  - Minor omissions in formatting or extra recommendations, but all critical constraints are met.
- **3 (Acceptable)**:
  - Answers the question reasonably well but lacks depth (e.g. vague transit estimates or generic tips without itemized figures).
- **2 (Poor)**:
  - Fails to respect explicit user constraints (e.g. recommends ground floor when 1st floor was forbidden), or provides inaccurate numbers.
- **1 (Unacceptable)**:
  - Irrelevant, ungrounded, completely unhelpful, or broken response.
"""

    judge_prompt = f"""{eval_rubric}

---
### Input Under Evaluation:
User Prompt:
{prompt_text}

Agent Final Response:
{response_text}

Expected Reference / Criteria:
{reference if reference else "N/A (Open-ended goal fulfillment)"}

Full Agent Trajectory & Trace:
{agent_data}
"""

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=judge_prompt,
        config=types.GenerateContentConfig(
            temperature=0,  # Deterministic grading
            response_mime_type="application/json",
            response_schema=_EvaluationVerdict,
        ),
    )

    verdict = response.parsed
    if verdict is None:
        return {"score": 1, "explanation": response.text or "Model parsing error"}

    score_val = max(1, min(5, verdict.score))
    return {
        "score": score_val,
        "explanation": (
            f"[{score_val}/5] {verdict.explanation} | "
            f"Task: {verdict.task_achievement} | "
            f"Constraint Enforcement: {verdict.dislikes_enforcement} | "
            f"Citations: {verdict.source_citation}"
        ),
    }
