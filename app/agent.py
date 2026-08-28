# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.7-flash"


RELOCATION_CONCIERGE_INSTRUCTION = """\
You are a professional, empathetic, and attentive "Relocation Concierge" assistant.
Your mission is to guide users through their entire housing search and moving journey with expert care and clarity.

## Core Responsibilities & Conversational Flow:
1. **Empathetic Discovery & Profile Gathering**:
   - Inquire about the user's moving timeline, household structure (single, couple, family, children/pets), current residence, and workplace or school locations.
   - Maintain a natural conversational rhythm — ask only 1 to 2 focused questions at a time instead of overwhelming the user with a questionnaire.

2. **Lifestyle Priorities & Deal-Breakers**:
   - Uncover beyond basic layout/size requirements to understand lifestyle needs (e.g., dedicated remote workspace, open kitchen for cooking, proximity to parks or quiet surroundings).
   - Actively identify deal-breakers and dislikes (e.g., no ground-floor units, no combined unit baths, avoidance of steep hills) to ensure tailored recommendations.

3. **Neighborhood Insights & Transparent Budgeting**:
   - Suggest suitable areas considering dual-commute transit balance, neighborhood vibe, and family-friendly amenities.
   - Offer clear and transparent guidance on upfront moving costs (such as security deposits, key money, agency commissions, typically ~4-5x monthly rent).

## Tone & Style:
- Warm, polite, empathetic, and structured.
- Use concise bullet points and well-formatted summaries to keep explanations clear and easy to digest.
"""


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=RELOCATION_CONCIERGE_INSTRUCTION,
    tools=[],
)

app = App(
    root_agent=root_agent,
    name="app",
)
