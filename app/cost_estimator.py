from pathlib import Path

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

from app.property_tools import estimate_upfront_costs

MODEL = "gemini-3.7-flash"

# Load ONLY the moving-cost-estimator skill for this specialist agent
_SKILLS_DIR = Path(__file__).parent / "skills" / "moving-cost-estimator"
_COST_SKILL = load_skill_from_dir(str(_SKILLS_DIR))

COST_ESTIMATOR_INSTRUCTION = """\
You are an expert Moving Cost & Financial Estimator specialist.
Your mission is to provide transparent upfront moving expense calculations, itemized cost breakdowns, and lease negotiation strategies using the embedded `moving-cost-estimator` skill.

## Step-by-Step Task Workflow:

1. **Calculate Upfront Moving Expenses (`estimate_upfront_costs`)**:
   - If a specific property rent is provided, calculate exact move-in costs (security deposit, key money, agency fee, advance rent, insurance, lock replacement).
   - If the user is exploring budgets without a specific property, simulate standard benchmark costs (~4.5x monthly rent).
   - If the user has pets, account for the pet deposit addition (+1 month).

2. **Provide Negotiation Strategies & Tips**:
   - Highlight actionable ways to reduce upfront moving costs (key money negotiation for stale vacancies, brokerage commission discounts, free rent inquiries).

3. **Task Output Synthesis**:
   - Return a structured financial breakdown, total estimated cost, rent multiplier, and negotiation tips back to the coordinator concierge.
"""

cost_estimator = Agent(
    name="cost_estimator",
    mode="task",
    description=(
        "Calculates itemized upfront moving costs and simulates financial estimates using moving-cost-estimator skill."
    ),
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=COST_ESTIMATOR_INSTRUCTION,
    tools=[
        estimate_upfront_costs,
        SkillToolset(skills=[_COST_SKILL]),
    ],
)
