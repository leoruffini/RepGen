# GPT-5 and Responses API - Quick Reference

## Summary

I've gathered comprehensive information about ChatGPT-5 and the OpenAI Responses API. Here's what you need to know:

## Key Points

1. **GPT-5**: Latest multimodal reasoning model (released Aug 7, 2025)
2. **Responses API**: Recommended API for all new projects (especially reasoning models)
3. **Reasoning Models**: Think before answering, excel at complex problem-solving
4. **Multimodal**: Processes text, speech, and images
5. **Message Roles**: `developer` > `user` > `assistant` priority system

## Quick Start

```python
from openai import OpenAI

client = OpenAI()

# Simple generation
response = client.responses.create(
    model="gpt-5",
    input="Your prompt here"
)

# With reasoning (recommended)
response = client.responses.create(
    model="gpt-5",
    reasoning={"effort": "medium"},  # "low", "medium", or "high"
    input="Your prompt here"
)

print(response.output_text)
```

## Reasoning Parameter

- **low**: Fastest, economical token usage
- **medium**: Balanced speed and reasoning (default)
- **high**: More complete reasoning, slower response

## Message Roles

```python
response = client.responses.create(
    model="gpt-5",
    input=[
        {"role": "developer", "content": "System instructions"},
        {"role": "user", "content": "User question"}
    ]
)
```

## Key Differences from Chat Completions

1. **Use `responses.create()` not `chat.completions.create()`**
2. **Better performance with reasoning models**
3. **Use `input` parameter (string or array) instead of `messages`**
4. **Use `instructions` parameter for system-level instructions**
5. **Response structure has `output` array instead of `choices`**

## Response Structure

- **`response.output_text`**: Convenient property (aggregates all text outputs)
- **`response.output`**: Array of output items (may contain multiple items)
- **`response.usage`**: Token usage information
- **`response.usage.output_tokens_details.reasoning_tokens`**: Reasoning tokens (if reasoning enabled)

## Important Notes

1. **Token Budget**: Reserve at least 25,000 tokens for reasoning + outputs
2. **Incomplete Responses**: Check `response.status == "incomplete"`
3. **Model Snapshots**: Pin to specific snapshots in production (e.g., `gpt-5-2025-08-07`)
4. **Reasoning Tokens**: Count toward context window and billing but aren't visible

## Files Created

1. **GPT5_RESPONSES_API_GUIDE.md** - Comprehensive documentation guide
2. **gpt5_example.py** - Practical example code with various use cases

## Integration with Your Project

Based on your Real Estate Visit Report Generator project:

```python
def generate_report(transcription_json: dict) -> str:
    # Prompt is now stored in OpenAI - accessed via prompt ID
    prompt_id = os.getenv("OPENAI_PROMPT_ID")
    
    input_text = f"""

TRANSCRIPTION DATA:
{json.dumps(transcription_json, indent=2)}
"""
    
    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "medium"},
        instructions="You are an expert commercial analyst.",
        input=input_text,
        max_output_tokens=8000
    )
    
    return response.output_text
```

## Next Steps

1. Install OpenAI SDK: `pip install openai`
2. Get your API key from: https://platform.openai.com/api-keys
3. Review the example code in `gpt5_example.py`
4. Check the full guide in `GPT5_RESPONSES_API_GUIDE.md`

## Common Use Cases

- **Complex Problem Solving**: Use `reasoning={"effort": "high"}`
- **Simple Queries**: Use `reasoning={"effort": "low"}`
- **Image Analysis**: Use `input_image` in content array
- **Document Processing**: Upload files and use `input_file`
- **Web Search**: Add `tools=[{"type": "web_search"}]`


