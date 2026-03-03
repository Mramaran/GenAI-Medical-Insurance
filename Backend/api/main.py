"""ClaimChain API — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.claims import router as claims_router
from routes.review import router as review_router

app = FastAPI(
    title="ClaimChain API",
    description="GenAI-powered medical insurance claims with on-chain proof",
    version="1.0.0",
)

# CORS — allow React dev server and common deployment origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims_router)
app.include_router(review_router)


@app.get("/")
async def root():
    return {"message": "ClaimChain API is running", "version": "1.0.0"}


@app.on_event("startup")
async def startup():
    print("ClaimChain API running on http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
