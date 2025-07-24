import os
import pickle
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import tiktoken

# Load API key from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Config
DATA_DIR = "../Data/langchain_documents"  # Updated to point to your processed documents
MODEL_NAME = "gpt-4o"  # Use gpt-3.5-turbo if budget is tight
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Cost tracking
def count_tokens(text, model="gpt-4"):
    """Count tokens in text for cost estimation"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4

def estimate_cost(input_tokens, output_tokens, model="gpt-4o"):
    """Estimate cost based on token usage"""
    if model == "gpt-4o":
        input_cost_per_1k = 0.005
        output_cost_per_1k = 0.015
    elif model == "gpt-3.5-turbo":
        input_cost_per_1k = 0.0005
        output_cost_per_1k = 0.0015
    else:
        return 0
    
    input_cost = (input_tokens / 1000) * input_cost_per_1k
    output_cost = (output_tokens / 1000) * output_cost_per_1k
    return input_cost + output_cost

# Load documents from a specific pickle file
def load_documents_from_specific_file(folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        print("Available files in the directory:")
        if os.path.exists(folder_path):
            for f in os.listdir(folder_path):
                if f.endswith(".pkl") and "chunked" in f:
                    print(f"  - {f}")
        return []
    
    try:
        with open(file_path, 'rb') as f:
            documents = pickle.load(f)
        print(f"Loaded {len(documents)} documents from {filename}")
        return documents
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def get_rag_prediction(fighter1_name, fighter2_name, chunked_doc_file=None):
    """
    Get RAG-based prediction for a UFC fight.
    
    Args:
        fighter1_name (str): Name of the first fighter
        fighter2_name (str): Name of the second fighter
        chunked_doc_file (str): Optional specific chunked document file to use
        
    Returns:
        dict: Prediction results with response and cost information
    """
    # If no specific file provided, try to find the most recent one for this fight
    if chunked_doc_file is None:
        # Look for files that match the fighter names
        if os.path.exists(DATA_DIR):
            available_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pkl") and "chunked" in f]
            # Try to find a file that matches the fighter names
            for file in available_files:
                if fighter1_name.lower().replace(" ", "_") in file.lower() or fighter2_name.lower().replace(" ", "_") in file.lower():
                    chunked_doc_file = file
                    break
            # If no match found, use the first available file
            if chunked_doc_file is None and available_files:
                chunked_doc_file = available_files[0]
    
    if chunked_doc_file is None:
        print("No chunked document files found!")
        return None
    
    print(f"Loading documents from specific file: {chunked_doc_file}")
    docs = load_documents_from_specific_file(DATA_DIR, chunked_doc_file)

    if not docs:
        print("No documents found! Make sure to run load_sentiment_data.py first.")
        return None

    print(f"Loaded {len(docs)} total documents")

    # Estimate embedding costs
    total_text = " ".join([doc.page_content for doc in docs])
    embedding_tokens = count_tokens(total_text, "text-embedding-ada-002")
    embedding_cost = (embedding_tokens / 1000) * 0.0001
    print(f"Estimated embedding cost: ${embedding_cost:.4f}")

    print("Embedding and building vector store...")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Setup QA chain
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
    llm = ChatOpenAI(model_name=MODEL_NAME)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # Create dynamic query based on fighter names
    query = f"""You are a veteran MMA analyst with 15+ years of experience. Given retrieved documents (news, expert opinions, and public sentiment), your task is to predict the likely winner of the upcoming fight between {fighter1_name} and {fighter2_name}.

Instructions:
Analyze the documents through your expert lens — not just summarize.

Focus on recent performance, training camp changes, and fight-readiness.

Weigh the credibility, tone, and confidence of sources.

Evaluate:

Technical Skills: Striking, grappling, size, cardio, adaptability

Recent Form: Last 3–5 fights, level of opposition, trends

Physical & Mental Edge: Injuries, mindset, discipline

Media Signals: Bias, insider info, sentiment shifts

Output Structure:
Matchup Summary – Key stylistic notes

Fighter Comparison – Strengths, flaws, form

Media Sentiment – What’s the narrative? Who's getting the edge?

Prediction – Choose the winner confidently and decisively. Specify how the fight is most likely to end: will it go to a decision, or will one fighter finish the other? If a finish is likely, indicate the method – knockout, submission, or other.

Confidence Level – High / Medium / Low (with explanation)

Expert Reasoning – A step-by-step rationale behind your pick

Caveats – If any key info is uncertain or contradictory

Important: Your role is to interpret, compare, and predict — not to remain neutral. Make a clear call based on the available evidence."""

    print("Querying LLM...")

    # Estimate query costs
    input_tokens = count_tokens(query + " " + total_text[:2000])  # Rough estimate
    estimated_query_cost = estimate_cost(input_tokens, 200, MODEL_NAME)  # Assume 200 output tokens
    print(f"Estimated query cost: ${estimated_query_cost:.4f}")

    response = qa_chain.invoke({"query": query})

    # Count actual output tokens
    output_tokens = count_tokens(response["result"])
    actual_query_cost = estimate_cost(input_tokens, output_tokens, MODEL_NAME)
    print(f"Actual query cost: ${actual_query_cost:.4f}")
    print(f"Total estimated cost: ${embedding_cost + actual_query_cost:.4f}")

    print("\n🔮 RAG Prediction:\n", response["result"])
    
    return {
        "prediction": response["result"],
        "embedding_cost": embedding_cost,
        "query_cost": actual_query_cost,
        "total_cost": embedding_cost + actual_query_cost,
        "documents_loaded": len(docs)
    }

# Legacy code for backward compatibility
if __name__ == "__main__":
    # Default test case
    CHUNKED_DOC_FILE = "matthews_vs_njokuani_20250712_151021_chunked_docs_20250712_151552.pkl"
    result = get_rag_prediction("Jake Matthews", "Chidi Njokuani", CHUNKED_DOC_FILE)





