"""
Example: OpenAI GPT-5 with Responses API

This script demonstrates how to use ChatGPT-5 via the Responses API
for various use cases including text generation, reasoning, and multimodal inputs.
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI, APIError
    
    # Initialize client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)

except ImportError:
    print("OpenAI SDK not installed. Install with: pip install openai")
    client = None


# ============================================================================
# Basic Text Generation
# ============================================================================

def simple_text_generation(prompt: str) -> str:
    """
    Simple text generation without reasoning.
    
    Args:
        prompt: Input prompt text
        
    Returns:
        Generated text
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )
    
    return response.output_text


# ============================================================================
# Reasoning-Based Generation (Recommended for GPT-5)
# ============================================================================

def reasoning_generation(
    prompt: str,
    effort: str = "medium",
    instructions: Optional[str] = None
) -> Dict:
    """
    Generate text using GPT-5 with reasoning.
    
    Args:
        prompt: Input prompt text
        effort: Reasoning effort level ("low", "medium", "high")
        instructions: Optional high-level instructions
        
    Returns:
        Dictionary with response text and usage info
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    params = {
        "model": "gpt-5",
        "reasoning": {"effort": effort},
        "input": prompt
    }
    
    if instructions:
        params["instructions"] = instructions
    
    response = client.responses.create(**params)
    
    return {
        "text": response.output_text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.total_tokens,
            "reasoning_tokens": getattr(
                response.usage.output_tokens_details,
                "reasoning_tokens",
                None
            ) if hasattr(response.usage, 'output_tokens_details') else None
        },
        "status": getattr(response, 'status', 'completed')
    }


# ============================================================================
# Structured Conversations with Message Roles
# ============================================================================

def conversation_with_roles(user_message: str, system_instruction: str) -> str:
    """
    Create a conversation using message roles.
    
    Args:
        user_message: User's message
        system_instruction: System/developer instructions
        
    Returns:
        Assistant's response
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "medium"},
        input=[
            {
                "role": "developer",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    
    return response.output_text


# ============================================================================
# Real Estate Report Generation (Project-Specific)
# ============================================================================

def generate_real_estate_report(
    transcription_data: Dict,
    prompt_id: Optional[str] = None,
    prompt_version: str = "1"
) -> str:
    """
    Generate a real estate visit report from diarized transcription using stored prompt.
    
    Args:
        transcription_data: Transcription JSON with utterances
        prompt_id: OpenAI stored prompt ID (defaults to env variable)
        prompt_version: Prompt version (default: "1")
        
    Returns:
        Markdown report
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    # Get prompt ID from parameter or environment
    if not prompt_id:
        prompt_id = os.getenv("OPENAI_PROMPT_ID")
    
    if not prompt_id:
        raise ValueError("OPENAI_PROMPT_ID not found. Either pass as parameter or set in environment.")
    
    # Format input
    input_text = f"""TRANSCRIPTION DATA:
{json.dumps(transcription_data, indent=2, ensure_ascii=False)}
"""
    
    # Generate report using stored prompt
    response = client.responses.create(
        prompt={
            "id": prompt_id,
            "version": prompt_version
        },
        input=input_text,
        text={},
        max_output_tokens=16384,
        store=True
    )
    
    # Check for incomplete responses
    if hasattr(response, 'status') and response.status == "incomplete":
        if hasattr(response, 'incomplete_details'):
            if response.incomplete_details.reason == "max_output_tokens":
                print("Warning: Response truncated due to token limit")
                return response.output_text or ""
    
    return response.output_text


# ============================================================================
# Multimodal: Image Analysis
# ============================================================================

def analyze_image(image_url: str, question: str = "What is in this image?") -> str:
    """
    Analyze an image using GPT-5's multimodal capabilities.
    
    Args:
        image_url: URL of the image to analyze
        question: Question about the image
        
    Returns:
        Analysis text
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": question
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
    )
    
    return response.output_text


# ============================================================================
# File Input Processing
# ============================================================================

def process_document(file_path: str, instruction: str) -> str:
    """
    Process a document file using GPT-5.
    
    Args:
        file_path: Path to document file
        instruction: Instruction for processing the document
        
    Returns:
        Processed result
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    # Upload file
    with open(file_path, "rb") as f:
        file = client.files.create(
            file=f,
            purpose="user_data"
        )
    
    # Process with GPT-5
    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "medium"},
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": instruction
                    },
                    {
                        "type": "input_file",
                        "file_id": file.id
                    }
                ]
            }
        ]
    )
    
    return response.output_text


# ============================================================================
# Web Search Tool
# ============================================================================

def search_and_answer(query: str) -> str:
    """
    Use web search tool to answer questions.
    
    Args:
        query: Question to answer
        
    Returns:
        Answer with web search results
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    response = client.responses.create(
        model="gpt-5",
        tools=[{"type": "web_search"}],
        reasoning={"effort": "low"},
        input=query
    )
    
    return response.output_text


# ============================================================================
# Streaming Responses
# ============================================================================

def stream_response(prompt: str):
    """
    Stream response tokens as they're generated.
    
    Args:
        prompt: Input prompt
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    stream = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "medium"},
        input=prompt,
        stream=True
    )
    
    for event in stream:
        print(event, flush=True)


# ============================================================================
# Error Handling Example
# ============================================================================

def safe_generate(prompt: str, max_retries: int = 3) -> Optional[str]:
    """
    Generate response with error handling and retries.
    
    Args:
        prompt: Input prompt
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated text or None if failed
    """
    if not client:
        raise ImportError("OpenAI client not initialized")
    
    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model="gpt-5",
                reasoning={"effort": "medium"},
                input=prompt,
                max_output_tokens=4000
            )
            
            # Check for incomplete response
            if hasattr(response, 'status') and response.status == "incomplete":
                print(f"Warning: Response incomplete ({response.incomplete_details.reason})")
                return response.output_text or None
            
            return response.output_text
            
        except APIError as e:
            print(f"API Error (attempt {attempt + 1}/{max_retries}): {e.message}")
            if e.status_code == 429:  # Rate limit
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            elif e.status_code >= 500:  # Server error
                import time
                time.sleep(2 ** attempt)
            else:
                return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    return None


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GPT-5 Responses API Examples")
    print("=" * 60)
    
    # Example 1: Simple generation
    print("\n1. Simple Text Generation:")
    print("-" * 60)
    try:
        result = simple_text_generation(
            "Write a one-sentence bedtime story about a unicorn."
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Reasoning generation
    print("\n2. Reasoning-Based Generation:")
    print("-" * 60)
    try:
        result = reasoning_generation(
            "Write a bash script that takes a matrix represented as a string with format '[1,2],[3,4],[5,6]' and prints the transpose in the same format.",
            effort="medium"
        )
        print(f"Text: {result['text']}")
        print(f"Reasoning tokens: {result['usage']['reasoning_tokens']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Conversation with roles
    print("\n3. Conversation with Roles:")
    print("-" * 60)
    try:
        result = conversation_with_roles(
            user_message="Are semicolons optional in JavaScript?",
            system_instruction="Talk like a pirate."
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Web search
    print("\n4. Web Search Tool:")
    print("-" * 60)
    try:
        result = search_and_answer("What was a positive news story from today?")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Safe generation with error handling
    print("\n5. Safe Generation with Error Handling:")
    print("-" * 60)
    try:
        result = safe_generate("Explain quantum computing in simple terms.")
        if result:
            print(result[:200] + "..." if len(result) > 200 else result)
        else:
            print("Failed to generate response")
    except Exception as e:
        print(f"Error: {e}")


