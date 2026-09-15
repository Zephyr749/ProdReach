from pydantic import BaseModel, Field


class Budget(BaseModel):
    max: float | None= None
    min: float | None= None
    currency: str= "INR"
    
class ProdRequirements(BaseModel):
    category: str | None= None
    budget: Budget | None= None
    
    hard_requirements: list[str]= Field(default_factory=list)
    preferences: list[str]= Field(default_factory=list)
    use_cases: list[str]= Field(default_factory=list)
    avoid: list[str]= Field(default_factory=list)
    
    