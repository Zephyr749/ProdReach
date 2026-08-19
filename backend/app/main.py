import uvicorn
from fastapi import FastAPI
from app.routers import requirements

app= FastAPI(title= "ProdReach")

app.include_router(requirements.router)

@app.get("/")
def get_root():
    return {"message": "Hello World"}


if __name__== "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=4000, reload=True)
