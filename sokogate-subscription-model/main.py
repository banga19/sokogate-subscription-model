from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

from api.subscription_api import router as subscription_router
from services.subscription_service import SubscriptionService
from database.init_db import create_database, seed_subscription_plans
from config.settings import settings

# Background task for billing cycle processing
async def billing_cycle_task():
    """Background task to process billing cycles"""
    while True:
        try:
            from database import get_db
            db = next(get_db())
            service = SubscriptionService(db)
            await service.process_billing_cycle()
            print(f"Billing cycle processed at {datetime.utcnow()}")
        except Exception as e:
            print(f"Error in billing cycle: {e}")
        
        # Run every 24 hours
        await asyncio.sleep(86400)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Sokogate Subscription Service...")
    
    # Initialize database
    engine = create_database()
    seed_subscription_plans(engine)
    
    # Start background tasks
    billing_task = asyncio.create_task(billing_cycle_task())
    
    yield
    
    # Shutdown
    print("Shutting down Sokogate Subscription Service...")
    billing_task.cancel()

# Create FastAPI application
app = FastAPI(
    title="Sokogate Subscription & Pre-Order API",
    description="B2B E-commerce Subscription Platform with Pre-Order Capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(subscription_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "sokogate-subscription-service",
        "version": "1.0.0"
    }

# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Sokogate Subscription & Pre-Order API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "features": [
            "Subscription Management",
            "Pre-Order System",
            "Tiered Pricing Plans",
            "Usage Analytics",
            "Automated Billing",
            "Customer Management"
        ],
        "subscription_tiers": [
            {
                "name": "Basic",
                "monthly_price": "$29.99",
                "features": ["10 pre-orders/month", "$5K monthly limit", "3-day early access"]
            },
            {
                "name": "Premium", 
                "monthly_price": "$79.99",
                "features": ["50 pre-orders/month", "$25K monthly limit", "7-day early access", "Priority support"]
            },
            {
                "name": "Enterprise",
                "monthly_price": "$199.99", 
                "features": ["Unlimited pre-orders", "Unlimited value", "14-day early access", "Dedicated account manager"]
            }
        ]
    }

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "validation_error"}
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "type": "not_found_error"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
