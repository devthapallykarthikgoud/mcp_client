# controller/mcp_client.py

import requests
import json
import asyncio
import os
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv()

MCP_SERVER_URL = "https://medibot-mcp-remote.onrender.com/mcp"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

mcp_client = Client(MCP_SERVER_URL)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "symptom_checker",
            "description": "Analyze symptoms and provide possible conditions, severity, remedies and doctor consultation advice",
            "parameters": {
                "type": "object",
                "properties": {
                    "symptoms": {
                        "type": "string",
                        "description": "Symptoms described by the patient"
                    }
                },
                "required": ["symptoms"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "medicine_lookup",
            "description": "Look up medicine information like uses, side effects and warnings",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {
                        "type": "string",
                        "description": "Name of the medicine"
                    }
                },
                "required": ["medicine_name"]
            }
        }
    }
]


async def call_mcp_tool(tool_name, arguments):
    async with mcp_client:
        result = await mcp_client.call_tool(
            tool_name,
            arguments
        )

        return result.data


def decide_and_run(user_input):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 800,
        "tools": TOOLS,
        "tool_choice": "auto",
        "messages": [
            {
                "role": "system",
                "content": "You are MediBot, an AI medical assistant. Use tools when needed and always end with consult a doctor."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    response = requests.post(
        GROQ_URL,
        headers=GROQ_HEADERS,
        data=json.dumps(payload)
    )

    data = response.json()
    choice = data["choices"][0]
    message = choice["message"]
    finish_reason = choice["finish_reason"]

    if finish_reason == "tool_calls":
        tool_call = message["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        arguments = json.loads(
            tool_call["function"]["arguments"]
        )

        tool_result = asyncio.run(
            call_mcp_tool(tool_name, arguments)
        )

        final_response = requests.post(
            GROQ_URL,
            headers=GROQ_HEADERS,
            data=json.dumps({
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 800,
                "messages": [
                    {
                        "role": "system",
                        "content": "Format the response clearly and always end with consult a doctor."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    },
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": message["tool_calls"]
                    },
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(tool_result)
                    }
                ]
            })
        )

        return final_response.json()["choices"][0]["message"]["content"]

    return message.get("content", "No response")