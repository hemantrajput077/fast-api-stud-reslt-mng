import time
from fastapi import FastAPI, Request
from database import engine, Base
from models import *
from app.routers import auth, student
from app.logger import setup_logging, logger

# Setup logging configuration
setup_logging()

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    logger.info(f"Incoming request: {method} {path}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Completed request: {method} {path} - Status: {response.status_code} - Completed in: {process_time:.2f}ms"
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"Failed request: {method} {path} - Error: {str(e)} - Completed in: {process_time:.2f}ms"
        )
        raise e

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(student.router, prefix="/student", tags=["Student"])