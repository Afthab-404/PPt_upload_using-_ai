from fastapi import FastAPI
from routes.presentation import router

app = FastAPI(
    title="AI Presentation Builder"
)

app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "AI Presentation Builder API Running"
    }