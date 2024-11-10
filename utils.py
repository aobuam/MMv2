import os
from openai import OpenAI
import requests
import streamlit as st
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_embedding(text, client):
    """Génère un embedding pour le texte donné en utilisant OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def semantic_search(query, index, top_k=3):
    """
    Effectue une recherche sémantique dans Pinecone.
    
    Args:
        query (str): La requête de l'utilisateur
        index: L'index Pinecone
        top_k (int): Nombre de résultats à retourner
        
    Returns:
        list: Liste de tuples (titre, contenu) des résultats pertinents
    """
    try:
        # Créer le client OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Obtenir l'embedding de la requête
        query_embedding = get_embedding(query, client)
        
        # Faire la recherche dans Pinecone
        xr = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extraire les résultats
        results = []
        for match in xr.matches:
            # Vérifier la présence des clés nécessaires
            title = match.metadata.get("title", "Sans titre")
            
            # Essayer d'abord "transcript", puis "content" comme fallback
            content = match.metadata.get("transcript")
            if content is None:
                content = match.metadata.get("content", "Contenu non disponible")
            
            results.append((title, content))
            
        return results
        
    except Exception as e:
        print(f"Erreur lors de la recherche sémantique: {str(e)}")
        # Retourner un résultat par défaut en cas d'erreur
        return [("Erreur", "Désolé, une erreur s'est produite lors de la recherche. Veuillez réessayer.")]
