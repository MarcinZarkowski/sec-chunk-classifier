import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SectionTypes
from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum

# Create an Enum containing all the section names dynamically.
# This guarantees Gemini will return the exact strings we expect in the JSON response.
SectionTypeNames = Enum('SectionTypeNames', {k: k for k in SectionTypes.keys()})

class ChunkClassification(BaseModel):
    chunk_id: int = Field(description="The ID of the chunk provided in the prompt")
    section_labels: List[SectionTypeNames] = Field(description="The list of applicable section categories for this chunk.")

class BatchClassificationResponse(BaseModel):
    classifications: List[ChunkClassification]

def get_section_types_description():
    res = ""
    for name, value in SectionTypes.items():
        res += f"- {name}: {value}\n"
    return res

def get_batch_prompt(chunks: List[str]):
    prompt = f"""
    You are a financial analyst tasked with classifying chunks of text from SEC filings into one or more of the following categories:

    {get_section_types_description()}

    Please classify each of the following text chunks. 
    Return a list of classifications mapping each chunk_id to its applicable section labels.
    
    """
    for i, chunk in enumerate(chunks):
        prompt += f"--- CHUNK {i} ---\n{chunk}\n\n"
        
    return prompt
