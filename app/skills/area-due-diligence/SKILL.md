---
name: area-due-diligence
description: Geospatial analysis and neighborhood due diligence protocol for residential area evaluations using Google Maps Grounding Lite MCP tools (compute_routes, search_places, resolve_names).
---

# Area & Neighborhood Due Diligence Skill

This skill provides expert heuristics, evaluation guidelines, and analysis workflows for the `area_researcher` agent to conduct geospatial due diligence on candidate residential neighborhoods using Google Maps Grounding Lite MCP tools.

---

## 1. Google Maps Grounding Lite MCP Tool Protocol

| Tool | Primary Purpose | Evaluation Guidelines |
|---|---|---|
| **`resolve_names`** | Canonical Place ID Resolution | Resolve ambiguous station names, district names, and landmark queries into canonical Google Maps Place IDs before computing routes or searching amenities. |
| **`compute_routes`** | Commute & Transit Analysis | Calculate door-to-door transit travel durations and distances from candidate neighborhood centers/stations to household workplaces or universities. |
| **`search_places`** | Living Amenity Discovery | Search for essential daily living facilities within a walkable radius (~800m / 10 min walk) around candidate stations. |

---

## 2. Commute Equity & Route Evaluation Protocol

When evaluating candidate areas for couples or multi-member households with different daily destinations:

1. **Dual-Commute Fairness Benchmark**:
   - Calculate transit durations to Destination A and Destination B using `compute_routes`.
   - **Fair & Balanced**: Travel time difference $\le 15$ minutes.
   - **Moderate Disparity**: Travel time difference between $16$ and $25$ minutes.
   - **Imbalanced**: Travel time difference $> 25$ minutes (flag for discussion).

2. **Commute Fatigue Factors**:
   - Note transfer counts (0 transfers / direct lines significantly reduce daily fatigue).
   - Check total one-way commute duration (ideal: $\le 35$ mins, acceptable: $\le 50$ mins).

---

## 3. Walkable Living Amenity Checklist

Using `search_places`, query essential neighborhood infrastructure around candidate stations within an 800m radius:

1. **Daily Groceries & Essentials**:
   - Supermarkets (check presence of multiple options, e.g., budget + premium).
   - Drugstores and convenience stores.
2. **Family & Childcare (if applicable)**:
   - Parks and green spaces with playgrounds.
   - Certified daycares, nursery schools, and pediatric clinics.
3. **Medical & Healthcare**:
   - General clinics, internal medicine, and emergency medical access.

---

## 4. Structured Output Guidelines for `area_researcher`

When completing a research task, return a concise and structured report to the coordinating `root_agent`:

```markdown
### 📍 Area Due Diligence Report: [Neighborhood / Station Name]

#### 🚆 Commute Analysis
- **To Destination 1 ([Destination Name])**: ~XX mins (Route details)
- **To Destination 2 ([Destination Name])**: ~YY mins (Route details)
- **Commute Equity**: [Fair & Balanced / Moderate Disparity / Imbalanced] (Diff: ZZ mins)

#### 🛒 Living Environment & Walkable Amenities (~800m)
- **Supermarkets & Groceries**: [Discovered stores & access]
- **Parks & Green Spaces**: [Nearby parks & playground features]
- **Clinics & Healthcare**: [Local medical facilities]

#### 💡 Overall Area Assessment
- **Summary**: Key strengths, lifestyle fit, and trade-offs.
```
