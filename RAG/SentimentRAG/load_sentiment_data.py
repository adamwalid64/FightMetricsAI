"""
Load and chunk documents from the Lewis vs Teixeira sentiment dataset.
This script processes the CSV file and prepares the text data for RAG systems.
"""

import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging
import pickle
import os
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sentiment_data(csv_file_path: str):
    """
    Load sentiment data from CSV file and convert to LangChain Documents.
    
    Args:
        csv_file_path (str): Path to the CSV file containing sentiment articles
        
    Returns:
        List[Document]: List of LangChain Document objects
    """
    try:
        logger.info(f"Loading sentiment data from {csv_file_path}")
        
        # Extract filename prefix from CSV path
        csv_filename = os.path.basename(csv_file_path)
        filename_prefix = csv_filename.replace('_sentiment_articles_', '_').replace('.csv', '')
        
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} articles from CSV")
        
        # Convert to LangChain Documents
        documents = []
        for idx, row in df.iterrows():
            # Create document content with title and text
            content = f"Title: {row['title']}\n\nText: {row['text']}\n\nURL: {row['url']}"
            
            # Create metadata
            metadata = {
                'title': row['title'],
                'url': row['url'],
                'publish_date': row.get('publish_date', ''),
                'source': f'{filename_prefix}_sentiment',
                'index': idx
            }
            
            # Create LangChain Document
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        logger.info(f"Created {len(documents)} LangChain Documents")
        return documents, filename_prefix
        
    except Exception as e:
        logger.error(f"Error loading sentiment data: {e}")
        raise

def load_sentiment_data_by_fight(fighter1_name: str, fighter2_name: str):
    """
    Load sentiment data for a specific fight by fighter names.
    
    Args:
        fighter1_name (str): Name of the first fighter
        fighter2_name (str): Name of the second fighter
        
    Returns:
        List[Document]: List of LangChain Document objects
    """
    # Create the expected CSV filename with different naming patterns
    fight_name_exact = f"{fighter1_name}_vs_{fighter2_name}"
    fight_name_clean = f"{fighter1_name.lower().replace(' ', '_')}_vs_{fighter2_name.lower().replace(' ', '_')}"
    
    # Try multiple filename patterns
    possible_filenames = [
        f"{fight_name_exact}_sentiment_articles.csv",
        f"{fight_name_clean}_sentiment_articles.csv"
    ]
    
    csv_file_path = None
    for filename in possible_filenames:
        test_path = f"../Data/sentiment_datasets/{filename}"
        if os.path.exists(test_path):
            csv_file_path = test_path
            break
    
    # If exact match not found, look for files with timestamp pattern
    if csv_file_path is None:
        sentiment_dir = "../Data/sentiment_datasets"
        
        # Try both naming patterns with timestamp
        patterns = [
            f"{fight_name_exact}_sentiment_articles_*.csv",
            f"{fight_name_clean}_sentiment_articles_*.csv"
        ]
        
        matching_files = []
        for pattern in patterns:
            # Use forward slashes for glob patterns on Windows
            full_pattern = sentiment_dir.replace('\\', '/') + '/' + pattern
            files = glob.glob(full_pattern)
            matching_files.extend(files)
        
        if matching_files:
            # Use the most recent file
            latest_file = max(matching_files, key=os.path.getctime)
            csv_file_path = latest_file
        else:
            logger.error(f"No sentiment data files found for {fight_name_exact} or {fight_name_clean}")
            return None, None
    
    try:
        return load_sentiment_data(csv_file_path)
    except Exception as e:
        logger.error(f"Error loading sentiment data for {fight_name_exact}: {e}")
        return None, None

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split documents into smaller chunks for better processing.
    
    Args:
        documents (List[Document]): List of LangChain Document objects
        chunk_size (int): Size of each chunk in characters
        chunk_overlap (int): Overlap between chunks in characters
        
    Returns:
        List[Document]: List of chunked Document objects
    """
    try:
        logger.info("Chunking documents...")
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        # Split documents into chunks
        chunked_docs = text_splitter.split_documents(documents)
        
        logger.info(f"Split {len(documents)} documents into {len(chunked_docs)} chunks")
        return chunked_docs
        
    except Exception as e:
        logger.error(f"Error chunking documents: {e}")
        raise

def save_langchain_documents(documents, filename_prefix, output_folder="../Data/langchain_documents"):
    """
    Save LangChain documents to the langchain_documents folder.
    
    Args:
        documents (List[Document]): List of LangChain Document objects
        filename_prefix (str): Prefix for the saved files (extracted from CSV filename)
        output_folder (str): Path to the output folder
    """
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Save original documents with simple naming (no timestamp)
        original_filename = f"{filename_prefix}_original_docs.pkl"
        original_path = os.path.join(output_folder, original_filename)
        
        with open(original_path, 'wb') as f:
            pickle.dump(documents, f)
        
        logger.info(f"Saved {len(documents)} original documents to {original_path}")
        
        # Save chunked documents with simple naming (no timestamp)
        chunked_filename = f"{filename_prefix}_chunked_docs.pkl"
        chunked_path = os.path.join(output_folder, chunked_filename)
        
        # First chunk the documents
        chunked_docs = chunk_documents(documents)
        
        with open(chunked_path, 'wb') as f:
            pickle.dump(chunked_docs, f)
        
        logger.info(f"Saved {len(chunked_docs)} chunked documents to {chunked_path}")
        
        return {
            'original_path': original_path,
            'chunked_path': chunked_path,
            'original_count': len(documents),
            'chunked_count': len(chunked_docs)
        }
        
    except Exception as e:
        logger.error(f"Error saving LangChain documents: {e}")
        raise

def load_langchain_documents(file_path):
    """
    Load LangChain documents from a saved pickle file.
    
    Args:
        file_path (str): Path to the saved pickle file
        
    Returns:
        List[Document]: List of LangChain Document objects
    """
    try:
        with open(file_path, 'rb') as f:
            documents = pickle.load(f)
        
        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents
        
    except Exception as e:
        logger.error(f"Error loading LangChain documents: {e}")
        raise

def analyze_sentiment_data(documents):
    """
    Analyze the sentiment data to provide insights.
    
    Args:
        documents (List[Document]): List of LangChain Document objects
    """
    logger.info("Analyzing sentiment data...")
    
    # Basic statistics
    total_articles = len(documents)
    total_text_length = sum(len(doc.page_content) for doc in documents)
    avg_text_length = total_text_length / total_articles if total_articles > 0 else 0
    
    # Extract titles for analysis
    titles = [doc.metadata.get('title', '') for doc in documents]
    
    # Find articles with specific keywords
    lewis_mentions = [title for title in titles if 'lewis' in title.lower()]
    teixeira_mentions = [title for title in titles if 'teixeira' in title.lower()]
    prediction_mentions = [title for title in titles if 'prediction' in title.lower()]
    odds_mentions = [title for title in titles if 'odds' in title.lower()]
    
    print(f"\n=== Sentiment Data Analysis ===")
    print(f"Total articles: {total_articles}")
    print(f"Average text length: {avg_text_length:.0f} characters")
    print(f"Articles mentioning Lewis: {len(lewis_mentions)}")
    print(f"Articles mentioning Teixeira: {len(teixeira_mentions)}")
    print(f"Articles with predictions: {len(prediction_mentions)}")
    print(f"Articles with odds: {len(odds_mentions)}")
    
    print(f"\n=== Sample Titles ===")
    for i, title in enumerate(titles[:5], 1):
        print(f"{i}. {title}")
    
    return {
        'total_articles': total_articles,
        'avg_text_length': avg_text_length,
        'lewis_mentions': len(lewis_mentions),
        'teixeira_mentions': len(teixeira_mentions),
        'prediction_mentions': len(prediction_mentions),
        'odds_mentions': len(odds_mentions)
    }

def main():
    """
    Main function to load and process the sentiment data.
    """
    # Path to the sentiment dataset
    csv_file_path = r"C:\CODE\Python\ML Projects\UFC-Prediction\Data\sentiment_datasets\matthews_vs_njokuani_sentiment_articles_20250712_151021.csv"
    
    try:
        # Load the sentiment data
        print("Loading fight sentiment data...")
        documents, filename_prefix = load_sentiment_data(csv_file_path)
        
        # Analyze the data
        analysis = analyze_sentiment_data(documents)
        
        # Save the processed documents to langchain_documents folder
        print("\nSaving LangChain documents...")
        saved_files = save_langchain_documents(documents, filename_prefix)
        
        print(f"\n=== Processing Complete ===")
        print(f"Original documents: {saved_files['original_count']}")
        print(f"Chunked documents: {saved_files['chunked_count']}")
        print(f"Files saved to: {saved_files['original_path']}")
        print(f"Chunked files saved to: {saved_files['chunked_path']}")
        print(f"Ready for RAG system integration!")
        
        # Return the processed documents for use in RAG
        return {
            'original_documents': documents,
            'saved_files': saved_files,
            'analysis': analysis
        }
        
    except Exception as e:
        print(f"Error processing sentiment data: {e}")
        return None

if __name__ == "__main__":
    main() 