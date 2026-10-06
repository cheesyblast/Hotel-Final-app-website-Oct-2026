"""
Kreation Hotels — Website Backend (Standalone)
Serves public website API: rooms, availability, booking, contact
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from public_routes import public_router

app = FastAPI(title="Kreation Hotels Website API", version="1.0.0")

# CORS
origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount public routes under /api
app.include_router(public_router, prefix="/api")

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "website-backend"}
