from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from langchain.llms import OpenAI
from langchain.llms import VertexAI
from langchain.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from src.config import Config
from src.embeddings import EmbeddingSource
from src.logging_setup import setup_logger

config = Config()
logger = setup_logger()

class HandleRequestPostBody(BaseModel):
    user_input: str

def call_language_model(input_val):
    model_provider = config.get("MODEL_PROVIDER", "UNDEFINED")
    logger.debug(f"Using model provider: {model_provider}")
    prompt = PromptTemplate(
        input_variables=["input_val"],
        template="Tell me an interesting fact about {input_val}",
    )
    if model_provider == 'openai':
        result = call_openai(input_val, prompt)
    elif model_provider == 'vertex':
        result = call_vertexai(input_val, prompt)
    else:
        raise ValueError(f"Invalid model name: {model_provider}")
    return result
    
def call_vertexai(input_val, prompt):
    vertex_model_name = config.get("VERTEX_MODEL_NAME", "text-bison")
    logger.debug(f"Using Vertex AI model: {vertex_model_name}")
    llm = VertexAI(model_name=vertex_model_name, temperature=0.9)
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(input_val)
    return result
    

def call_openai(input_val, prompt):
    openai_model_name = config.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    logger.debug(f"Using OpenAI model: {openai_model_name}")
    llm = OpenAI(model_name=openai_model_name, temperature=0.9)
    chain = LLMChain(llm=llm, prompt=prompt)
    with get_openai_callback() as cb:
        result = chain.run(input_val)
    token_cost(cb.total_tokens)
    return result

def token_cost(total_tokens):
    spend_log_file = config.get("SPEND_LOG_FILE", "spend.log")
    openai_model_price = config.get("OPENAI_MODEL_PRICE", "0.000006")
    total_cost = total_tokens * float(openai_model_price)
    logger.debug(f"Total tokens: {total_tokens}")
    logger.debug(f"Total cost: ${total_cost:.5f}")

    with open(spend_log_file, "a") as file:
        file.write(f"{total_cost:.5f}\n")
    total_spent = calculate_total_spent(spend_log_file)
    return JSONResponse(
        {
            "total_tokens": total_tokens,
            "total_cost": f"${total_tokens:.5f}",
            "total_spent": f"${total_spent:.5f}",
        }
    )
    
def calculate_total_spent(spend_log_file):
    with open(spend_log_file, "r") as file:
        total_spent = sum(float(line.strip()) for line in file)
    logger.debug(f"Total Spent: ${total_spent:.5f}")
    return total_spent

def get_bot_response(user_input):
    logger.info(user_input)
    if user_input == 'hello':
        return 'Hi there!'
    elif user_input == 'what is your name?':
        return 'My name is Chat Bot!'
    else:
        return call_language_model(user_input)

    
app = FastAPI()
cors_origins = config.get("CORS_ORIGINS", "UNDEFINED")
origins = [origin.strip() for origin in cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def handle_request():
    return {"error": "Only POST requests are allowed"}

@app.post("/")
async def handle_request_post(request_body: HandleRequestPostBody):
    user_input = request_body.user_input
    bot_response = get_bot_response(user_input)
    return {"bot_response": bot_response}

@app.post("/get_embedding_sources")
def get_embedding_source(request_body: dict):
    query = request_body['query']
    num_results = request_body['num_results']
    if isinstance(query, list):
        query = ' '.join(query)
    embeddings = EmbeddingSource()
    result = embeddings.get_source(query, num_results)
    return {"embedding_source": result}

@app.post("/synthesize_response")
def synthesize_response(
    query: str = Body(...),
    num_results: int = Body(3),
    prompt: str = Body(None)
):
    if isinstance(query, list):
        query = ' '.join(query)

    embeddings = EmbeddingSource()
    embedding_results = embeddings.get_source(query, num_results)

    embedding_results_text = '\n\n---\n\n'.join([
        f"Source: <a href=\"{result.get('source_link', '#')}\">{result['source']}</a>\n\nContent:\n\n{result['content']}"
        for result in embedding_results
    ])

    if prompt is None:
        prompt = (
            "Below is the only information you know.\n"
            "It was obtained by doing a vector search for the user's query:\n\n"
            "---START INFO---\n\n{embedding_results}\n\n"
            "---END INFO---\n\nYou must acknowledge the user's original query "
            f"of \"{query}\". Attempt to generate a summary of what you know from the sources provided "
            "based ONLY on the information given and ONLY if it relates to the original query. "
            "Use no other knowledge to respond. Do not make anything up. "
            "You can let the reader know if do not think you have enough information "
            "to respond to their query...\n\n"
        )

    prompt = prompt.format(embedding_results=embedding_results_text)

    logger.info(f"Query: {query}")
    logger.info(f"Prompt: {prompt}")

    bot_response = call_language_model(prompt)

    sources_used = [f"<a href=\"{result.get('source_link', '#')}\">{result['source']}</a>" for result in embedding_results]
    bot_response += "\n\nPossibly Related Sources:\n" + '\n'.join(sources_used)

    return {"bot_response": bot_response}
    
@app.exception_handler(Exception)
def handle_exception(request, exc):
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(status_code=500, content={"message": "An internal error occurred"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
