---
name: live-property-search
description: Real web search strategies, listing page verification via load_web_page, and direct property permalink URL extraction heuristics.
---

# Live Rental Property Search Skill

This skill provides expert heuristics for searching active rental listings across open web sources, verifying individual property vacancy pages using `load_web_page`, filtering out deal-breakers, and citing authentic direct property permalink URLs.

---

## 1. Search Query Formulation for Specific Property Listings

1. **Target Specific Listing Pages**:
   - Scope queries to target portals and include specific vacancy signals:
     - Japan: `'site:suumo.jp/chintai/ "Station Name" "1LDK" "Rent"'`
     - Global: `'site:zillow.com/homedetails/ OR site:rightmove.co.uk/properties/ "Neighborhood" "rent"'`
2. **Avoid General Landing Pages**:
   - Filter out prefecture/city-level landing pages by requiring specific building terms (`"unit"`, `"floor"`, `"apt"`, `"room"`).

---

## 2. Listing Verification via `load_web_page`

**Every promising search result must be checked using `load_web_page` before recommendation:**
1. **Verify Vacancy**: Confirm the page represents an active listing with defined rent, floor number, and availability.
2. **Enforce Dislikes**:
   - Exclude 3-point unit baths (`unit_bath`).
   - Exclude ground-floor units (`first_floor`).
   - Exclude wooden/light-gauge steel structures (`wood_structure`).

---

## 3. Strict Direct Permalink URL Rules

- **Permitted**: Specific, individual property permalink URLs (e.g. `https://suumo.jp/chintai/jnc_000012345/`, `https://www.homes.co.jp/chintai/b-123456/`, `https://www.zillow.com/homedetails/123-Main-St/12345_zpid/`).
- **PROHIBITED**:
  - Top-level domain homepages (e.g. `https://suumo.jp/`, `https://zillow.com/`).
  - General search engine URLs (e.g. `https://www.google.com/search?...`).
  - Fabricated or placeholder URLs.
