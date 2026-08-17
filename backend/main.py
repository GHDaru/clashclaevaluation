"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.adapter.primary.fastapi_routes import router

app = FastAPI(
    title="ClashClanEvaluation",
    description="Clash Royale Clan Evaluation System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"name": "ClashClanEvaluation", "version": "0.1.0"}
