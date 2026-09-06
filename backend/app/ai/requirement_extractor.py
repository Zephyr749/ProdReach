from app.ai.client import client
from app.schemas.requirements import ProdRequirements
from app.core.config import app_settings

SYSTEM_PROMPT = """You extract structured product requirements from natural language shopping requests.

Your job is to understand what the user explicitly wants without making ungrounded assumptions.

Rules:
1. STRICT INTENT & NO INVENTED SPECS:
   - Do not invent requirements or specifications that the user did not specify.
   - If a user asks for a "coding laptop", do NOT assume minimum RAM, SSD size, or processor specs unless explicitly stated.

2. DISTINGUISH HARD REQUIREMENTS VS PREFERENCES:
   - Put explicit, mandatory requirements ("must have", "at least", "need", "minimum", "has to be") in hard_requirements.
   - Put soft desires ("preferably", "ideally", "would like", "nice to have", "better if") in preferences.
   - NEVER convert a preference into a hard requirement (e.g., "At least 16GB RAM, preferably 32GB" -> hard: "RAM >= 16GB", preference: "32GB RAM").

3. PRESERVE AMBIGUITY:
   - Preserve ambiguity instead of making arbitrary assumptions.
   - If the user says "around 80k" or "can stretch budget slightly", capture the base number in budget and note the flexibility in preferences.

4. CATEGORY & USE CASES:
   - Extract the product category when possible (e.g., laptop, smartphone, headphones, monitor).
   - Divide the categories within these categories only [
      'headphones', 'keyboard',
      'laptop',     'monitor',
      'mouse',      'router',
      'smartphone', 'ssd',
      'tablet',     'tv'
   ]
   - Extract the user's explicit use cases (e.g., programming, gaming, video editing, office work).

5. BUDGET & INDIAN CURRENCY NORMALIZATION:
   - Extract budget when explicitly stated and normalize values to integers:
     * "k" / "thousand" = 1,000 (e.g., "80k" -> 80000)
     * "Lakh" / "Lac" / "L" = 100,000 (e.g., "1.5 Lakh" or "1.5L" -> 150000)
     * "Grand" = 1,000 (e.g., "30 grand" -> 30000)
   - Default currency to "INR" unless another currency is explicitly mentioned.


6. THINGS TO AVOID (Negative Constraints & Exclusions):
   Extract explicit user dislikes, rejected brands, unwanted features, or dealbreakers into the `avoid` list as concise, searchable keywords or phrases.
   - Brand Exclusions: ("no Samsung", "don't want Dell") -> ["Samsung", "Dell"]
   - Sub-category / Form Factor: ("no gaming laptops", "no bulky phones") -> ["gaming laptops", "bulky design"]
   - Hardware / Component: ("avoid Intel", "no micro-USB", "no LCD") -> ["Intel processor", "micro-USB", "LCD display"]
   - Aesthetics & Feel: ("no loud clicky switches", "no RGB lighting") -> ["clicky switches", "RGB lighting"]
   - Normalize the negative target into a clean noun phrase. Do NOT put positive requirements here.
"""

def extract_requirements(query: str) -> ProdRequirements | None:
    response= client.chat.completions.parse(
        model=app_settings.model_name,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": query
            }
        ],
        response_format=ProdRequirements,
        # temperature=0.0
    )
    
    return response.choices[0].message.parsed