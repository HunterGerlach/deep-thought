"""Deep Thought Application"""

import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from src.config import Config
from src.logging_setup import setup_logger
from src.v1.endpoints import router as v1_router
from src.v2.endpoints import router as v2_router

config = Config()
logger = setup_logger()

def custom_openapi():
    """Custom function to load OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    with open("specs/openapi-v1.json", "r", encoding='utf-8') as file:
        openapi_schema = json.load(file)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

DISABLE_SWAGGER = config.get("DISABLE_SWAGGER", "false").lower() == "true"

# Note: Include a FastAPI app for each version currently supported and mount accordingly...

## Create a FastAPI app for version 1
app_v1 = FastAPI(docs_url=None if DISABLE_SWAGGER else "/",
    title=config.get("API_TITLE", "UNDEFINED"),
    description=config.get("API_DESCRIPTION", "UNDEFINED"),
    version=config.get("API_VERSION", "UNDEFINED"),
)
app_v1.include_router(v1_router)

## Create a FastAPI app for version 2
app_v2 = FastAPI(docs_url=None if DISABLE_SWAGGER else "/",
    title=config.get("API_TITLE", "UNDEFINED"),
    description=config.get("API_DESCRIPTION", "UNDEFINED"),
    version=config.get("API_VERSION", "UNDEFINED"),
)
app_v2.include_router(v2_router)

app = FastAPI(docs_url=None)
app.mount("/v1", app_v1)
app.mount("/v2", app_v2)


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
def handle_exception(exc):
    """Handle exceptions and return a 500 error."""
    logger.error("An error occurred: %s", exc)
    return JSONResponse(status_code=500, content={"message": "An internal error occurred"})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
