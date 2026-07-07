from fastapi import FastAPI
from src.api.routes import router
from src.config import get_settings
from src.logger import setup_logger
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()
logger = setup_logger("main")

app = FastAPI(
    title="AI Voice Calling Agent - Phase 1",
    description="Basic outbound calling with Vonage Voice API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    logger.info(f"Server configured for {settings.host}:{settings.port}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
