import json
import logging
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

logger = logging.getLogger("sentinel")


def collect_tool_results(messages: list) -> str:
    """Extract all tool call results from a message history into a plain text summary."""
    results = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            results.append(msg.content)
        elif isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            results.append(msg.content)
    return "\n\n---\n\n".join(results)


def parse_json_array(text: str) -> list:
    """Parse a JSON array from LLM output, handling various formatting."""
    try:
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text and "[" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        elif "[" in text:
            start = text.index("[")
            end = text.rindex("]") + 1
            json_str = text[start:end]
        else:
            return []
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError, IndexError) as e:
        logger.warning(f"JSON parse failed: {e}")
        return []
