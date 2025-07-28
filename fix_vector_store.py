#!/usr/bin/env python3
"""
Script to fix vector store indexing issue
Re-indexes all documents from database to ChromaDB
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('/app')

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.knowledge import Document, DocumentChunk
from app.services.vector_store.factory import VectorStoreFactory
from app.services.embedding.embedding_factory import EmbeddingsFactory
from langchain_core.documents import Document as LangchainDocument
import chromadb

async def fix_vector_store():
    """Fix vector store by re-indexing all documents"""
    try:
        print("🔧 FIXING VECTOR STORE INDEXING")
        print("===============================")
        
        # Test ChromaDB connection
        print("📊 Step 1: Testing ChromaDB connection...")
        client = chromadb.HttpClient(
            host=settings.CHROMA_DB_HOST,
            port=settings.CHROMA_DB_PORT
        )
        
        collections = client.list_collections()
        print(f"✅ ChromaDB connected. Found {len(collections)} collections")
        
        # Check kb_1 collection
        try:
            kb1_collection = client.get_collection('kb_1')
            current_count = kb1_collection.count()
            print(f"📋 kb_1 collection exists with {current_count} documents")
            
            # Clear existing collection to start fresh
            if current_count > 0:
                print("🧹 Clearing existing collection...")
                client.delete_collection('kb_1')
                print("✅ Collection cleared")
                
        except Exception as e:
            print(f"📋 kb_1 collection doesn't exist yet: {str(e)}")
        
        # Get database connection
        print("📊 Step 2: Connecting to database...")
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get all document chunks for knowledge base 1
        print("📊 Step 3: Getting document chunks from database...")
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.knowledge_base_id == 1
        ).all()
        
        print(f"📊 Found {len(chunks)} chunks in database")
        
        if not chunks:
            print("❌ No chunks found in database!")
            return
        
        # Create embeddings and vector store
        print("📊 Step 4: Creating vector store...")
        embeddings = EmbeddingsFactory.create()
        vector_store = VectorStoreFactory.create(
            store_type='chroma',
            collection_name='kb_1',
            embedding_function=embeddings
        )
        
        # Convert chunks to documents
        print("📊 Step 5: Converting chunks to documents...")
        documents = []
        for i, chunk in enumerate(chunks):
            doc = LangchainDocument(
                page_content=chunk.chunk_metadata,
                metadata={
                    'chunk_id': str(chunk.id),
                    'file_name': chunk.file_name,
                    'document_id': str(chunk.document_id),
                    'knowledge_base_id': str(chunk.knowledge_base_id)
                }
            )
            documents.append(doc)
            
            if (i + 1) % 5 == 0:
                print(f"  Processed {i + 1}/{len(chunks)} chunks...")
        
        # Add documents to vector store
        print("📊 Step 6: Adding documents to ChromaDB...")
        vector_store.add_documents(documents)
        print(f"✅ Added {len(documents)} documents to ChromaDB")
        
        # Verify the addition
        final_collection = client.get_collection('kb_1')
        final_count = final_collection.count()
        print(f"✅ ChromaDB now has {final_count} documents")
        
        # Test retrieval
        print("📊 Step 7: Testing document retrieval...")
        retriever = vector_store.as_retriever(search_kwargs={'k': 3})
        test_docs = await retriever.ainvoke("AWS Cursor video")
        print(f"✅ Retrieved {len(test_docs)} documents for test query")
        
        for i, doc in enumerate(test_docs):
            print(f"  Doc {i+1}: {doc.page_content[:100]}...")
        
        db.close()
        print("🎉 Vector store fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_vector_store())
