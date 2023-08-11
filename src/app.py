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

from src.config import *
from src.embeddings import EmbeddingSource
from src.logging_setup import setup_logger

logger = setup_logger()

class HandleRequestPostBody(BaseModel):
    user_input: str

def call_language_model(input_val):
    if MODEL_PROVIDER == 'openai':
        result = call_openai(input_val)
    elif MODEL_PROVIDER == 'vertex':
        result = call_vertexai(input_val)
    else:
        raise ValueError(f"Invalid model name: {MODEL_PROVIDER}")
    return result
    
def call_vertexai(input_val):
    llm = VertexAI(model_name=VERTEX_MODEL_NAME, temperature=0.9)
    prompt = PromptTemplate(
        input_variables=["input_val"],
        template="Tell me an interesting fact about {input_val}",
    )
    logger.debug(f"template: {prompt.template}")
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(input_val)
    return result
    

def call_openai(input_val):
    llm = OpenAI(model_name=OPENAI_MODEL_NAME, temperature=0.9)
    prompt = PromptTemplate(
        input_variables=["input_val"],
        template="Tell me an interesting fact about {input_val}",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    with get_openai_callback() as cb:
        result = chain.run(input_val)
    token_cost_of_run(cb.total_tokens)
    calculate_total_spend()
    return result

def token_cost_of_run(total_tokens):
    total_cost = total_tokens * float(OPENAI_MODEL_PRICE)
    logger.debug(f"Total tokens: {total_tokens}")
    logger.debug(f"Total cost: ${total_cost:.5f}")

    with open(SPEND_LOG_FILE, "a") as file:
        file.write(f"{total_cost:.5f}\n")
        
    return JSONResponse(
        {
            "total_tokens": total_tokens,
            "total_cost": f"${total_tokens:.5f}",
        }
    )
    
def calculate_total_spend():
    with open(SPEND_LOG_FILE, "r") as file:
        total_spend = sum(float(line.strip()) for line in file)
    logger.debug(f"Total Spend: ${total_spend:.5f}")
    return total_spend

def get_bot_response(user_input):
    logger.info(user_input)
    if user_input == 'hello':
        return 'Hi there!'
    elif user_input == 'what is your name?':
        return 'My name is Chat Bot!'
    else:
        return call_language_model(user_input)

    
app = FastAPI()
origins = ["http://localhost:3000"]
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
