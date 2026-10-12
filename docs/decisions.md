# Architectural Decision Records (ADRs)

## ADR 01: FAISS IndexFlatIP with Exact Cosine NumPy Fallback
- **Context:** We need fast, reliable vector similarity retrieval for document passages without introducing mandatory cloud infrastructure or database overhead during local development.
- **Decision:** Use FAISS `IndexFlatIP` with unit-normalized vectors (which mathematically equals Cosine Similarity). Implement an automatic pure-NumPy cosine similarity fallback in `VectorStore`.
- **Consequences:** Near-zero retrieval latency (< 1 ms), completely local operation, zero external vector DB costs, with 100% reproducibility across environments.

---

## ADR 02: Deterministic Python Math instead of LLM Arithmetic
- **Context:** LLMs frequently hallucinate arithmetic totals, struggle with currency conversions, and make multiplication errors with group sizes.
- **Decision:** All financial and duration computations are handled strictly by `BudgetCalculator` using Python's `Decimal` type.
- **Consequences:** 100% mathematical accuracy on group totals and budget ceilings. The system never relies on generated text for numerical ground truth.

---

## ADR 03: Bounded LangGraph Workflow with Max Revisions
- **Context:** Autonomous agent loops can easily enter infinite cycles if constraints cannot be satisfied.
- **Decision:** Structure the planning workflow as an explicit LangGraph `StateGraph` with a hard ceiling `MAX_AGENT_REVISIONS = 2`.
- **Consequences:** Bounded repair loop: if an itinerary violates budget or duration limits, the agent trims excess activities; if still unresolvable, it returns a schema-valid response accompanied by clear constraint warnings.

---

## ADR 04: Graceful Neo4j Offline Fallback
- **Context:** Users or CI environments may not always have a live Neo4j daemon running on `bolt://localhost:7687`.
- **Decision:** Wrap Neo4j Cypher queries in `TravelGraphQueries` with an in-memory graph fallback.
- **Consequences:** The application is 100% functional out of the box without requiring Neo4j to be started, while still supporting full Cypher querying when connected.
