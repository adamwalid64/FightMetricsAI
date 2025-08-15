import os
import sys

# Change to Prediction directory to load model files
os.chdir('Prediction')

# Add current directory to Python path
sys.path.append('.')

import custom_inputs
import UFC_scrape.ufc_sentiment_scrape as ufc_sentiment_scrape
import RAG.SentimentRAG.load_sentiment_data as load_sentiment_data
import RAG.SentimentRAG.ufcRAG as ufcRAG
import pandas as pd


def masterPrediction(fighter1id, fighter2id):


    # XGBoost Prediction ------------------------------------------------------------

    # Load in the fighters
    fighterLookup = pd.read_csv('../Data/raw-scraped-ufc-data2.csv')

    fighter1 = fighterLookup.loc[fighterLookup['id'] == fighter1id]
    fighter1_name = fighter1['name'].values[0]

    fighter2 = fighterLookup.loc[fighterLookup['id'] == fighter2id]
    fighter2_name = fighter2['name'].values[0]

    # Scrape Sentiment Data
    ufc_sentiment_scrape.scrape_ufc_sentiment(f"{fighter1_name} vs {fighter2_name}")

    # Load Sentiment Data and create chunked documents
    print("\n=== Loading Sentiment Data ===")
    documents, filename_prefix = load_sentiment_data.load_sentiment_data_by_fight(fighter1_name, fighter2_name)
    
    if documents and filename_prefix:
        # Save the processed documents to langchain_documents folder
        print("Saving LangChain documents...")
        saved_files = load_sentiment_data.save_langchain_documents(documents, filename_prefix)
        print(f"Documents saved: {saved_files['chunked_count']} chunks created")


    print(f"\n======{fighter1_name} vs. {fighter2_name}======")

    # XGboost Prediction
    custom_inputs.getCustomPredict(fighter1id, fighter2id)

    # RAG LLM Sentiment Analysis
    
    print("\n=== RAG Sentiment Analysis ===")
    rag_result = ufcRAG.get_rag_prediction(fighter1_name, fighter2_name)
    
    if rag_result:
        print(f"RAG Analysis completed successfully!")
        print(f"Cost: ${rag_result['total_cost']:.4f}")
        print(f"Documents processed: {rag_result['documents_loaded']}")
    else:
        print("RAG Analysis failed - no sentiment data available for this fight.")


masterPrediction(3544, 2697)





