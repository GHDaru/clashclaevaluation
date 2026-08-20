"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.adapter.primary.fastapi_routes import router

app = FastAPI(
    title="ClashClanEvaluation",
    description="Clash Royale Clan Evaluation System",
    version="0.1.0",
)

# CORS: allow localhost (dev) + any configured production origins
_cors_origins = ["http://localhost:5173", "http://localhost:3000"]
_extra = os.environ.get("CORS_ORIGINS", "")
if _extra:
    _cors_origins.extend(o.strip() for o in _extra.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"name": "ClashClanEvaluation", "version": "0.1.0"}
