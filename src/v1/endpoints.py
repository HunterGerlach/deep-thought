"""Module to define API routing and handle interactions with language models."""

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
from pydantic import BaseModel # pylint: disable=E0611

from langchain.llms import OpenAI
from langchain.llms import VertexAI
from langchain.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.utils.math import cosine_similarity
from langchain.prompts import PromptTemplate

from src.config import Config
from src.embeddings import EmbeddingSource
from src.logging_setup import setup_logger

config = Config()
logger = setup_logger()

router = APIRouter()

class HandleRequestPostBody(BaseModel): # pylint: disable=R0903
    """Class to define the request body for the handle_request_post endpoint."""
    user_input: str

def call_language_model(input_val):
    """Call the language model and return the result.

    Args:
        input_val: The input value to pass to the language model.

    Returns:
        The result from the language model.
    """
    model_provider = config.get("MODEL_PROVIDER", "UNDEFINED")
    logger.debug("Using model provider: %s", model_provider)
    prompt = PromptTemplate(
        input_variables=["input_val"],
        template="Pay close attention to the following... {input_val}",
    )
    if model_provider == 'openai':
        result = call_openai(input_val, prompt)
    elif model_provider == 'vertex':
        result = call_vertexai(input_val, prompt)
    else:
        raise ValueError(f"Invalid model name: {model_provider}")
    return result

def call_vertexai(input_val, prompt):
    """Call the Vertex AI language model and return the result.

    Args:
        input_val: The input value to pass to the language model.

    Returns:
        The result from the language model.
    """
    vertex_model_name = config.get("VERTEX_MODEL_NAME", "text-bison")
    logger.debug("Using Vertex AI model: %s", vertex_model_name)
    llm = VertexAI(
        model_name=vertex_model_name,
        temperature=float(
            config.get("MODEL_TEMPERATURE", 0.0))
        )
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(input_val)
    return result

def call_openai(input_val, prompt):
    """Call the OpenAI language model and return the result.

    Args:
        input_val: The input value to pass to the language model.

    Returns:
        The result from the language model.
    """
    openai_model_name = config.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    logger.debug("Using OpenAI model: %s", openai_model_name)
    if not spend_limit_exceeded():
        llm = OpenAI(model_name=openai_model_name, temperature=float(
            config.get("MODEL_TEMPERATURE", 0.0)))
        chain = LLMChain(llm=llm, prompt=prompt)
        with get_openai_callback() as openai_callback:
            result = chain.run(input_val)
        token_cost(openai_callback.total_tokens)
    else:
        raise HTTPException(status_code=402, detail="Spending limit exceeded")

    return result

def token_cost(total_tokens):
    """Calculate the cost of the tokens and log it.

    Args:
        total_tokens: The total number of tokens used.

    Returns:
        The total cost of the tokens.
    """
    spend_log_file = config.get("SPEND_LOG_FILE", "spend.log")
    openai_model_price = config.get("OPENAI_MODEL_PRICE", "0.000006")
    total_cost = total_tokens * float(openai_model_price)
    logger.debug("Total tokens: %f", total_tokens)
    logger.debug("Total cost: $%.5f", total_cost)

    with open(spend_log_file, "a", encoding="utf-8") as file:
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
    """Calculate the total amount spent on tokens.

    Args:
        spend_log_file: The file containing the spend log.

    Returns:
        The total amount spent on tokens.
    """
    with open(spend_log_file, "r", encoding="utf-8") as file:
        total_spent = sum(float(line.strip()) for line in file)
    logger.debug("Total Spent: $%.5f", total_spent)
    return total_spent

def spend_limit_exceeded():
    """Check whether the spend limit has been exceeded.

    Args:
        None

    Returns:
        True if the spend limit has been exceeded, False otherwise.
    """
    spend_log_file = config.get("SPEND_LOG_FILE", "spend.log")
    spend_limit = config.get("SPEND_LIMIT", "0.001")
    total_spent = calculate_total_spent(spend_log_file)
    if total_spent > float(spend_limit):
        logger.error("SPEND_LIMIT ($%.5f) exceeded: $%.5f", float(spend_limit), total_spent)
        return True
    # use SPENDING_WARNING_PCT to determine when to send warning
    spending_warning_pct = config.get("SPENDING_WARNING_PCT", "0.8")
    if float(spend_limit) * float(spending_warning_pct) < total_spent <= float(spend_limit):
        logger.warning("SPEND_LIMIT warning")
    logger.debug("SPEND_LIMIT ($%.5f) not exceeded: $%.5f", float(spend_limit), total_spent)
    return False

def calculate_confidence(query, result):
    embeddings = EmbeddingSource()
    query_vector = embeddings.vectorize_query(query)
    result_vector = embeddings.vectorize_query(result)
    similarity_matrix = cosine_similarity(np.array([query_vector]), np.array([result_vector]))
    similarity = similarity_matrix[0][0]  # Since both are single vectors, we get a 1x1 matrix
    logger.debug("Similarity: %s", similarity)

    if similarity >= 0.7:
        return "High"
    elif similarity >= 0.4:
        return "Medium"
    else:
        return "Low"

def get_bot_response(user_input):
    """Get the bot response.

    Args:
        user_input: The user input to pass to the bot.

    Returns:
        The bot response.
    """
    logger.info(user_input)
    if user_input == 'hello':
        return 'Hi there!'
    if user_input == 'what is your name?':
        return 'My name is Chat Bot!'
    return call_language_model(user_input)


@router.get("/api_version_test/")
async def read_items():
    """Test Endpoint for API v1.

    Returns:
        list: The API current version.
    """
    return [{"version": "v1"}]


@router.post("/")
async def handle_request_post(request_body: HandleRequestPostBody):
    """Endpoint to handle POST requests for user input.

    Args:
        request_body: The body of the request containing user input.

    Returns:
        dict: A dictionary containing the bot response.
    """
    user_input = request_body.user_input
    bot_response = get_bot_response(user_input)
    return {"bot_response": bot_response}

@router.post("/find_sources", responses = {401: {
                                        "description": "PostgreSQL connection failed",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                }
                                            }
                                        }
                                }})
def get_embedding_source(query: str = Body("step by step instructions to install a new operator"),
                        num_results: int = Body(3)):
    """Endpoint to get embedding sources for a given query.

    Args:
        request_body: The body of the request containing the query and number of results.

    Returns:
        dict: A dictionary containing the embedding source.
    """

    if isinstance(query, list):
        query = ' '.join(query)
    embeddings = EmbeddingSource()
    result = embeddings.get_source(query, num_results)
    return {"find_sources": result}


@router.post("/ask", responses = {402: {
                                        "description": "Payment Required",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                }
                                            }
                                        }
                                }})
def synthesize_response(
                        query: str = Body("step by step instructions to install a new operator"),
                        num_results: int = Body(3),
                        prompt: str = Body(None)
                    ):
    """Endpoint to synthesize a response to a user query.

    Args:
        query: The user query.
        num_results: The number of results to return.
        prompt: The prompt to use for the response.

    Returns:
        dict: A dictionary containing the bot response.
    """
    if isinstance(query, list):
        query = ' '.join(query)

    embeddings = EmbeddingSource()
    embedding_results = embeddings.get_source(query, num_results)

    embedding_results_text = '\n\n---\n\n'.join([
        (
            f"Source: <a href=\"{result.get('source_link', '#')}\">"
            f"{result['source']}</a>\n\nContent:\n\n{result['content']}"
        )
        for result in embedding_results
    ])

    if prompt is None:        
        prompt = (
            "[BACKGROUND]\n"
            "Forget any and all previous instructions.\n\n"
            "[ROLE]\n"
            "You are an AI that provides extremely technical engineering support for associates at a large open source tech company.\n"
            "You stay on task and do NOT provide responses to requests that are out of scope for your role.\n\n"
            "[USER QUERY]\n"
            "The user's question is:\n\n"
            f"{query}\n\n"
            "[SOURCE INFO]\n"
            "The information you provided below.\n"
            "It is solely based on a vector search through available documentation for the user's query.\n"
            "---START SOURCES---\n\n{embedding_results}\n\n"
            "---END SOURCES---\n\n"
            "[GUIDELINES]\n"
            "- Generate a summary using ONLY the sources provided and nothing else.\n"
            "- Your answer should be only one paragraph with NO extraneous whitespace.\n"
            "- You MUST acknowledge the user's original query in an appropriate manner (don't simply repeat the question).\n"
            "- Your answer should NOT be influenced by the user's query, but should be relevant to it.\n"
            "- Consider alternative spellings, synonyms, and other ways of expressing the query.\n"
            "- Simplicity and clarity are key. Do NOT provide any unnecessary extraneous information.\n"
            "[DECIDING TO ANSWER]\n"
            "- If you cannot provide a relevant response due to your technical role described earlier, then you MUST decline to answer and provide a clear explanation for why you declined (this is a high bar, so rarely decline).\n"
            "- If you don't have enough information, you must clearly state that you cannot respond to the query.\n"
            "- If you decline to answer, then you MUST provide a straightforward and clear explanation for why you declined.\n"
            "It is vitally important that your response strictly adheres to each and every one of the above guidelines listed above.\n"
            "Absolutely NO JOKES (or any other extraneous information) are allowed)!...unless they're SFW and extremely nerdy :-p\n"
            "Now, take a deep breath and think step by step...\n\n"
        )

    prompt = prompt.format(embedding_results=embedding_results_text)
    logger.info("Query: %s", query)
    logger.info("Prompt: %s", prompt)
    bot_response = call_language_model(prompt).strip()
    logger.debug("Bot Response: %s", bot_response)
    
    # Calculate confidence for query and bot response. Prepend confidence to bot response.
    confidence = calculate_confidence(query, bot_response)
    bot_response = f"CONFIDENCE: {confidence}\n\n{bot_response}"
    
    sources_used = [
        # f"<a href=\"{result.get('source_link', '#')}\">{result['source']}</a>"
        # for result in embedding_results
        # TODO: remove this once the above is fixed
        
        
        # f"{result['source']}"
        # for result in embedding_results
        
        # Each source contains one of the following prefix URLs: embeddings/quarkus, embeddings/k8s, embeddings/istio
        # We want to remove this prefix URL from the source name and replace it with the actual URL as outlined below
        # e.g. embeddings/quarkus -> https://github.com/quarkusio/quarkusio.github.io/blob/develop
        # e.g. embeddings/k8s -> https://github.com/kubernetes/website/blob/main/content/en/docs
        # e.g. embeddings/istio -> https://github.com/istio/istio.io/blob/master/content/en/docs
        
        f"{result['source'].replace('embeddings/quarkus', 'https://github.com/quarkusio/quarkusio.github.io/blob/develop').replace('embeddings/k8s', 'https://github.com/kubernetes/website/blob/main').replace('embeddings/istio', 'https://github.com/istio/istio.io/blob/master')}"
        for result in embedding_results
    ]
    if sources_used:
        # bot_response += "\n\nPossibly Related Sources:\n" + '\n'.join(sources_used)
        # Output Possible Sources in a numbered list (e.g. [1] Source 1, [2] Source 2, etc.)
        bot_response += "\n\nPossibly Related Sources:\n" + '\n'.join([f"[{i+1}] {source}" for i, source in enumerate(sources_used)])
    else:
        bot_response += "\n\nNo Sources Found"

    return {"bot_response": bot_response}

# Example Questions Asked in OpenShift Room:
# Can you SSH to the node?

# I have a question regarding statefulsets and pvcs. According to this article, https://kubernetes.io/docs/tasks/run-application/delete-stateful-set/#persistent-volumes
# It seems you must manually delete a PVC when deleting/scaling down a statefulset pod. There was an article a couple years ago that mentioned this would become automatic (article stated it was in alpha preview, at the time) https://kubernetes.io/blog/2021/12/16/kubernetes-1-23-statefulset-pvc-auto-deletion/

# Can someone please confirm the features available in Kubernetes, generally, as it applies to scaling down a statefulset that also has a claim template - does a PVC have to be manually deleted, or can this be done automatically, assuming the 'Delete' retention policy is set on the storage class? Thank you.
