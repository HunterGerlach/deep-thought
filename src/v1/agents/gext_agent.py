from fastapi import APIRouter, Body

from langchain.chains import LLMChain
from langchain.llms import VertexAI
from langchain.prompts import PromptTemplate

from src.logging_setup import setup_logger
from src.embeddings import EmbeddingSource

logger = setup_logger()

router = APIRouter()


def call_language_model(input_val: str):
    """Get a response from a specified LLM with a specified prompt.

    Args:
        input_val (_type_): _description_

    Returns:
        _type_: _description_
    """
    # TODO: Move hardcoded vars to config
    
    # Create prompt template
    logger.debug("Using model provider: vertex")
    prompt = PromptTemplate(
        input_variables=["input_val"],
        template="{input_val}",
    )
    logger.debug("Using Vertex AI model: text-bison@001")
    
    # Create the LLM object - customizable
    llm = VertexAI(
        model_name="text-bison@001",
        max_output_tokens=512,
        temperature=0.0,
        top_k=1,
        # top_p=TOP_P,
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Get a response from the LLM
    result = chain.run(input_val)
    
    return result


def get_quick_response(input_val: str):
    result = None
    if input_val == "help":
        result = "I am an agent for Global Expense and Travel trained on the GET policy and FAQs.\n" + \
        "You can ask me any question about travel, expenses, or coporate cards at any time by invoking the /gext command."
    return result


@router.get("/agent_test/")
async def agent_test():
    """Test endpoint for the gext agent.

    Returns:
        list: The name of the agent.
    """
    return [{"agent": "gext"}]


@router.post("/ask")
async def ask(query: str = Body("help"), num_results: int = Body(4)):
    """Endpoint to synthesize a response to a user query.

    Args:
        query: The user query.
        num_results: The number of results to return.
        prompt: The prompt to use for the response.

    Returns:
        dict: A dictionary containing the gext agent response.
    """
    
    if isinstance(query, list):
        query = ' '.join(query)

    quick_response = get_quick_response(query)
    if quick_response is not None:
        return {"bot_response": quick_response}
        
    gext_connection_string = "postgresql://UNDEFINED"
    gext_collection_name = "UNDEFINED"

    embeddings = EmbeddingSource()
    embedding_results = embeddings.get_source(query, num_results, gext_connection_string, gext_collection_name)

    embedding_results_text = '\n\n---\n\n'.join([
        (
            f"Source: <a href=\"{result.get('source_link', '#')}\">"
            f"{result['source']}</a>\n\nContent:\n\n{result['content']}"
        )
        for result in embedding_results
    ])
    
    # TODO: Placeholder
    prompt = """Provide a detailed answer to the question based on the context below. \
    If you don't know the answer, say "I don't know".

    {embedding_results}

    Question: {query}
    Helpful Answer:"""
    
    prompt = prompt.format(embedding_results=embedding_results_text, query=query)
    
    logger.info("Query: %s", query)
    logger.info("Prompt: %s", prompt)
    
    # Get a response from the language model
    bot_response = call_language_model(prompt)

    # Format sources used
    sources_used = [
        f"<a href=\"{result.get('source_link', '#')}\">{result['source']}</a>"
        for result in embedding_results
    ]
    if sources_used:
        bot_response += "\n\nSources:\n" + '\n'.join(sources_used)
    
    return {"bot_response": bot_response}