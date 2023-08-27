from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

from src.config import Config
from src.logging_setup import setup_logger
from src.v1.endpoints import router as v1_router
from src.v2.endpoints import router as v2_router

config = Config()
logger = setup_logger()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    with open("specs/openapi_v1.json", "r") as file:
        openapi_schema = json.load(file)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

DISABLE_SWAGGER = config.get("DISABLE_SWAGGER", "false").lower() == "true"

app = FastAPI(docs_url=None if DISABLE_SWAGGER else "/docs")

app.include_router(v1_router, prefix="/v1")
app.include_router(v2_router, prefix="/v2")

if not DISABLE_SWAGGER:
    app.openapi = custom_openapi

cors_origins = config.get("CORS_ORIGINS", "UNDEFINED")
origins = [origin.strip() for origin in cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.exception_handler(Exception)
def handle_exception(request, exc):
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(status_code=500, content={"message": "An internal error occurred"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", debug=True)
