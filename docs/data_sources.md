# TravelPilot AI — Data Sources & Provenance Policy

## 1. Overview & Data Integrity Principle

TravelPilot AI follows an evidence-grounded approach to travel data:
- No synthetic prices are represented as live booking rates.
- All demo records are explicitly marked with `data_status: "demo_data"`.
- If venue costs or opening hours are unknown, the system marks them as `null` / `unknown` rather than defaulting to `0`.

---

## 2. Ingested Reference Documents

| Document ID | Title | File | Status | Retrieval Date | Source Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `demo-goa-guide-01` | Goa Travel & Destination Overview | `data/raw/goa_overview.md` | Demo Data | 2026-03-01 | Goa Tourism Department Reference Data |
| `demo-goa-guide-02` | Goa Heritage, Churches and Forts | `data/raw/goa_heritage_and_culture.md` | Demo Data | 2026-03-01 | Old Goa World Heritage & ASI Monuments |
| `demo-goa-guide-03` | Goa Coastal Guide: North vs South Beaches | `data/raw/goa_beaches_and_watersports.md` | Demo Data | 2026-03-01 | Goa Coastal Management & Drishti Marine Guidelines |
| `demo-goa-guide-04` | Goan Gastronomy, Spice Farms, and Food Guide | `data/raw/goa_food_and_dining.md` | Demo Data | 2026-03-01 | Goan Culinary Heritage & Agro-Tourism Plantation Records |

---

## 3. Seed Attraction Records

Structured attraction records reside in `data/demo/goa_attractions.json`:
- **Fort Aguada & Lighthouse:** History • 120 mins • Sourced Estimate ₹50/person
- **Basilica of Bom Jesus:** History • 90 mins • Free entry (₹0)
- **Fontainhas Latin Quarter Walking Tour:** History • 120 mins • Sourced Estimate ₹300/person
- **Anjuna Beach & Flea Market:** Beaches • 150 mins • Free entry (₹0)
- **Palolem Beach & Silent Valley:** Beaches • 180 mins • Sourced Estimate ₹200/person
- **Sahakari Spice Farm Tour & Buffet Lunch:** Local Food • 180 mins • Sourced Estimate ₹500/person
- **Panaji River Mandovi Cruise:** Local Food / Entertainment • 120 mins • Sourced Estimate ₹650/person
- **Dr. Salim Ali Bird Sanctuary:** Nature • 150 mins • Sourced Estimate ₹100/person
- **Dudhsagar Waterfalls Viewpoint Trek:** Nature • 300 mins • Sourced Estimate ₹800/person
- **Tito's Lane Nightlife Experience:** Nightlife • 180 mins • Sourced Estimate ₹1,500/person
