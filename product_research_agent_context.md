# Product Research Agent — Project Context

## Goal

The user is already an experienced full-stack developer. This project is specifically to learn AI application engineering:

- LLM APIs
- structured outputs
- prompt engineering
- embeddings
- RAG
- vector search/retrieval
- tool/function calling
- agents and agent loops
- LangChain
- LangGraph
- evaluation
- AI application architecture

The user wants to build it **traditionally, without AI coding tools**. They will use official documentation and write/debug the code themselves.

Do not spend time teaching basic backend/frontend concepts unless asked.

---

# Chosen POC: Product Research Agent

Build a product research/recommendation system for the Indian marketplace context.

Example input:

> I need a laptop under ₹80k for programming. At least 16GB RAM, preferably 32GB, good battery life and USB-C charging.

Eventually the system should:

1. Understand natural-language shopping requirements.
2. Convert them into structured requirements.
3. Distinguish hard requirements from preferences.
4. Deterministically filter products.
5. Retrieve product/review information.
6. Use RAG.
7. Compare candidates.
8. Use tools/function calling.
9. Become an agent that decides what research/actions are needed.
10. Produce evidence-backed recommendations/citations.
11. Eventually support live web/product research.

This is an AI-learning POC, not a production e-commerce application.

---

# Scope: Core AI only

For now, DO NOT build:

- authentication
- user accounts
- profiles
- admin UI
- product CRUD
- payments
- cart
- favorites
- notifications
- deployment
- mobile app
- polished frontend
- live marketplace scraping

A CLI and a few FastAPI endpoints are enough.

The user can add traditional application functionality later.

---

# Stack

The user already knows Node.js/TypeScript and FastAPI.

Chosen stack:

- Python
- FastAPI
- Pydantic
- OpenAI Python SDK
- Microsoft Foundry / OpenAI-compatible API
- MongoDB later
- embeddings/vector DB later
- LangChain later
- LangGraph later

Python was chosen because the user already knows FastAPI and the AI ecosystem is strong in Python.

---

# Core development philosophy

Do NOT start with LangChain or agents.

Build the underlying concepts manually first:

```text
Raw LLM API
    ↓
Structured output
    ↓
Requirement extraction
    ↓
Deterministic filtering
    ↓
LLM comparison
    ↓
Embeddings
    ↓
Vector search
    ↓
Manual RAG
    ↓
Grounded answers/citations
    ↓
LangChain
    ↓
Tool calling
    ↓
Manual agent loop
    ↓
LangGraph
    ↓
Agentic research workflow
    ↓
Evaluation/observability
    ↓
Live web research
```

The point is to understand what frameworks abstract rather than merely learn framework syntax.

---

# Synthetic product dataset

A JSON file containing exactly 100 synthetic products was created for development:

`product_research_products_100.json`

Categories:

- 10 smartphones
- 10 laptops
- 10 headphones/earbuds
- 10 monitors
- 10 keyboards
- 10 mice
- 10 SSDs
- 10 Wi-Fi routers
- 10 TVs
- 10 tablets

Each product roughly contains:

```text
_id
category
brand
name
price_inr
availability
market
description
specifications
reviews[]
seller
```

The data is intentionally synthetic and modeled around Indian-market products. It is NOT verified live marketplace data.

The user intends to insert it into MongoDB later.

Important: do not start with scraping Amazon/Flipkart/etc. The goal is AI learning, not scraping infrastructure.

---

# Eventual architecture

```text
User
  ↓
Requirement parser
  ↓
Structured intent
  ↓
Deterministic hard filtering
  ↓
Candidate products
  ├── MongoDB/product data
  └── RAG over reviews/docs
          ↓
       Agent/research
          ├── search_products()
          ├── get_product_details()
          ├── search_reviews()
          ├── retrieve_evidence()
          └── compare_products()
          ↓
       Evidence evaluation
          ↓
       Recommendation + citations
```

---

# Phase 1 — Current phase

The ONLY goal right now:

```text
Natural language shopping request
        ↓
LLM
        ↓
Structured requirement object
        ↓
Pydantic validation
```

Do not use MongoDB, RAG, embeddings, LangChain, LangGraph, agents, or web search yet.

---

# Phase 1 example

Input:

> I need a laptop under ₹80k for programming. At least 16GB RAM, preferably 32GB, good battery life and USB-C charging. I don't care about gaming performance.

Desired conceptual output:

```json
{
  "category": "laptop",
  "budget": {
    "max": 80000,
    "currency": "INR"
  },
  "hard_requirements": [
    "RAM >= 16GB",
    "USB-C charging"
  ],
  "preferences": [
    "32GB RAM",
    "good battery life"
  ],
  "use_cases": [
    "programming"
  ],
  "avoid": [
    "gaming-focused hardware"
  ]
}
```

Exact representation can evolve.

---

# Critical rule: hard vs soft

Example:

> At least 16GB RAM, preferably 32GB.

Should become:

```text
Hard: RAM >= 16GB
Preference: RAM = 32GB
```

Do NOT turn the preference into a hard requirement.

Likewise:

> I can stretch my budget a little if there is a significant improvement.

Should preserve ambiguity instead of silently changing the budget.

---

# Critical rule: do not invent requirements

If the user says:

> I want a good laptop under ₹80k for programming.

Do NOT invent:

```text
RAM >= 16GB
SSD >= 512GB
USB-C charging
```

just because those are reasonable assumptions.

The first step is extraction of explicit user intent.

Important principle:

> The LLM interprets; application code decides and executes.

---

# Initial Pydantic schema

Initially use a simple schema:

```python
from pydantic import BaseModel, Field


class Budget(BaseModel):
    min: int | None = None
    max: int | None = None
    currency: str = "INR"


class ProductRequirements(BaseModel):
    category: str | None = None
    budget: Budget | None = None

    hard_requirements: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
```

Do NOT use:

```python
dict[str, Any]
```

for strict structured output. An earlier attempt caused an OpenAI schema error because unrestricted object properties are incompatible with strict structured-output requirements.

Eventually requirements can become more machine-readable, for example:

```json
{
  "hard_requirements": [
    {
      "attribute": "ram_gb",
      "operator": "gte",
      "value": 16
    }
  ]
}
```

But do that later. First learn the basic pipeline.

---

# Initial system prompt

Start simple:

```text
You extract product requirements from natural language shopping requests.

Your job is to understand what the user explicitly wants.

Rules:

1. Do not invent requirements that the user did not specify.
2. Distinguish hard requirements from preferences.
3. Preserve ambiguity instead of making assumptions.
4. Extract the product category when possible.
5. Extract the budget when explicitly stated.
6. Extract the user's use cases.
7. Extract things the user explicitly wants to avoid.
8. Put explicit mandatory requirements in hard_requirements.
9. Put preferences such as "preferably", "ideally", or "would like"
   in preferences.
10. Do not convert preferences into hard requirements.
```

Do not blindly optimize the prompt before testing. Run cases, observe failures, then improve it.

---

# Suggested project structure

```text
backend/
├── .env
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   ├── ai/
│   │   ├── client.py
│   │   └── requirement_extractor.py
│   ├── schemas/
│   │   └── requirements.py
│   └── routes/
│       └── requirements.py
├── .venv/
└── ...
```

The user has already started the FastAPI server.

---

# Current Microsoft Foundry configuration

The user is using Microsoft Foundry with the OpenAI-compatible API.

Current environment variables are conceptually:

```env
OPENAI_API_KEY=KEY
MODEL_NAME=gpt-5.6-luna
OPENAI_API_BASE_URL=https://PROJECTNAME-resource.services.ai.azure.com/api/projects/projectNAME/openai/v1
```

The `/openai/v1` suffix is important.

The user originally had:

```text
https://PROJECTNAME-resource.services.ai.azure.com/api/projects/projectNAME
```

and received:

```text
Missing required query parameter: api-version
```

The `/openai/v1` endpoint is the OpenAI-compatible Foundry endpoint and avoids that `api-version` requirement.

The model name must match the actual model/deployment available in the user's Foundry project. Do not assume a model/deployment exists just because a generic model name is mentioned.

---

# Current model

The user wants a low-cost model for the POC and selected:

`gpt-5.6-luna`

Use the user's actual Foundry deployment/model identifier if it differs.

Do not switch providers unless the user asks.

---

# Current SDK approach

The user is using the OpenAI Python SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base_url,
)
```

The current debugging problem is with the Responses API request format.

An earlier request used:

```python
input=[
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": query,
    },
]
```

This produced:

```text
openai.BadRequestError: Error code: 400

Invalid value: ''. Supported values are:
'additional_tools',
'agent_message',
'apply_patch_call',
'apply_patch_call_output',
...
'message',
...
'web_search_call'

param: input[1]
code: invalid_value
```

The immediate debugging strategy is to temporarily remove structured output and test a plain Responses API request:

```python
response = client.responses.create(
    model=settings.base_model_name,
    instructions=SYSTEM_PROMPT,
    input=query,
)

return response.output_text
```

First establish:

```text
FastAPI
  ↓
Microsoft Foundry
  ↓
GPT-5.6 Luna
  ↓
plain text response
```

Then restore structured Pydantic output.

Do not debug endpoint + model + input format + schema simultaneously.

---

# Phase 1 test cases

Create about 30 test queries eventually. Start with:

1. `Laptop under 70k, 16GB RAM, 512GB SSD.`

2. `I need something around 80k for coding. Battery life matters more than gaming.`

3. `I want a phone below 30 grand with a good camera and at least 256 gigs.`

4. `Give me the cheapest decent headphones for flying. ANC is essential and I don't want anything heavy.`

5. `I need a laptop for programming. Don't recommend gaming laptops.`

6. `I can stretch my budget a little if there's a significant improvement.`

7. `I want a laptop around 80k.`

8. `I want the best laptop.`

Pay particular attention to ambiguity and hallucinated requirements.

Evaluate:

```text
Category correct?
Budget correct?
Hard requirements correct?
Preferences correct?
Use case correct?
Avoid correct?
Ambiguity preserved?
No invented attributes?
```

This is the first introduction to LLM evaluation.

---

# Later phases

## Phase 2 — Deterministic filtering

Use MongoDB and the 100 products.

```text
Structured requirements
        ↓
Normal Python
        ↓
Hard requirement filtering
        ↓
Candidate products
```

Example:

```text
price <= 15000
wifi == true
ram_slots >= 4
m2_slots >= 2
optical_audio == true
```

Never use an LLM for deterministic arithmetic/filtering.

---

## Phase 3 — LLM comparison

Give the LLM candidates and soft preferences.

Normal code:
- hard constraints

LLM:
- subjective comparison/ranking

---

## Phase 4 — Embeddings + RAG

Index:
- product descriptions
- reviews
- later manufacturer documentation

Manual pipeline:

```text
Question
  ↓
Embedding
  ↓
Vector search
  ↓
Relevant review chunks
  ↓
LLM
  ↓
Answer
```

Do this without LangChain first.

---

## Phase 5 — Grounded answers/citations

Produce claims with evidence:

```text
Claim
  ↓
Supporting review/specification
```

Example:

```text
Evidence:
[1] Review #17
[2] Review #31
[3] Manufacturer specification
```

---

## Phase 6 — LangChain

Reimplement pieces one at a time:

```text
Manual embeddings → LangChain embeddings
Manual retrieval → LangChain retriever
Manual RAG → LangChain RAG
```

Understand what each abstraction provides.

---

## Phase 7 — Tool calling

Tools:

```text
search_products()
get_product_details()
search_reviews()
compare_products()
retrieve_evidence()
```

---

## Phase 8 — Manual agent

Implement the fundamental loop:

```text
User
 ↓
LLM
 ↓
Need tool?
 ├── No → answer
 └── Yes
       ↓
     Tool
       ↓
     Result
       ↓
      LLM
       ↓
    repeat/answer
```

Only after understanding this should LangGraph be introduced.

---

## Phase 9 — LangGraph

Use LangGraph for:

- state
- planning
- branching
- retries
- loops
- tool execution
- stopping conditions

---

## Phase 10 — Agentic research

Eventually:

```text
User request
  ↓
Plan research
  ↓
Search products
  ↓
Extract specs
  ↓
Filter candidates
  ↓
Search reviews
  ↓
Evaluate evidence
  ↓
Research again if evidence is weak
  ↓
Rank candidates
  ↓
Recommendation + citations
```

---

# Key principles

1. LLM interprets; normal code executes deterministic logic.
2. Hard requirements and preferences must be separated.
3. Never invent requirements.
4. Preserve ambiguity.
5. Ground recommendations in evidence.
6. Evaluate models systematically rather than by intuition.
7. Learn underlying mechanics before adopting frameworks.
8. Keep the UI/backend infrastructure minimal.
9. Do not start live scraping.
10. Do not use AI coding tools for this POC.

---

# Immediate next step

The user is currently at Phase 1.

Get this endpoint working:

```text
POST /requirements/extract
```

Input:

```json
{
  "query": "I need a laptop under ₹80,000 with at least 16GB RAM, preferably 32GB, good battery life and USB-C charging. It's mainly for programming."
}
```

First make the plain-text Foundry Responses API call work.

Then add structured Pydantic output.

Then test 10–30 deliberately difficult shopping requests.

Do not move to MongoDB/RAG/agents until the requirement extraction behavior is understood.
