import json
from typing import List, Dict, Any, Optional
import httpx
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.ai.prompt_builder import SystemPromptBuilder
from app.domain.ai.tool_registry import GEMINI_TOOLS_DECLARATION
from app.domain.ai.tool_executors import ToolExecutor
from app.domain.ai.guardrails import InputSanitizer, ToolCallRequest

class GeminiClient:
    """Async Client wrapper for Google AI Studio Gemini API with Function Calling support."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate_response_with_tools(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        conversation_id: UUID,
        chat_history: List[Dict[str, Any]],
        user_message: str,
        business_name: str = "Our Business",
        rag_context: Optional[List[str]] = None
    ) -> str:
        """Executes Gemini LLM inference with automated tool calling multi-turn resolution."""
        # 1. Sanitize user input
        sanitized_input = InputSanitizer.sanitize_user_input(user_message)

        # 2. Build System Prompt
        system_prompt = SystemPromptBuilder.build_system_prompt(
            business_name=business_name,
            rag_chunks=rag_context
        )

        # 3. Assemble Contents payload
        contents = []
        
        # Format previous message history
        for msg in chat_history:
            role = "user" if msg["sender_type"] == "CUSTOMER" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        # Append current user turn
        contents.append({
            "role": "user",
            "parts": [{"text": sanitized_input}]
        })

        # 4. Construct Gemini API Request Body
        tools_payload = [{"function_declarations": GEMINI_TOOLS_DECLARATION}]
        
        request_body = {
            "contents": contents,
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "tools": tools_payload,
            "generationConfig": {
                "temperature": 0.2, # Low temperature for factual precision & tool adherence
                "maxOutputTokens": 800
            }
        }

        # Multi-turn tool execution loop (Max 3 tool hops)
        executor = ToolExecutor(db, tenant_id, conversation_id)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(3):
                url = f"{self.base_url}?key={self.api_key}" if self.api_key else self.base_url
                
                # If no real API key is set in dev, return mock fallback
                if not self.api_key or self.api_key == "mock_gemini_api_key":
                    return self._generate_mock_fallback_response(sanitized_input)

                response = await client.post(url, json=request_body)
                if response.status_code != 200:
                    print(f"Gemini API Error ({response.status_code}): {response.text}")
                    return "Thank you for reaching out! A support representative will assist you shortly."

                res_json = response.json()
                candidates = res_json.get("candidates", [])
                if not candidates:
                    return "I'm here to help! Could you please provide more details?"

                candidate = candidates[0]
                content_parts = candidate.get("content", {}).get("parts", [])
                
                function_call_part = None
                text_response = ""

                for part in content_parts:
                    if "functionCall" in part:
                        function_call_part = part["functionCall"]
                        break
                    elif "text" in part:
                        text_response += part["text"]

                # Case A: Model requested a Tool Function Call
                if function_call_part:
                    tool_req = ToolCallRequest(
                        name=function_call_part.get("name"),
                        args=function_call_part.get("args", {})
                    )
                    
                    print(f"[Gemini Function Call Request] Executing: {tool_req.tool_name}({tool_req.arguments})")
                    tool_result = await executor.execute(tool_req)
                    print(f"[Gemini Tool Result]: {tool_result}")

                    # Append complete model response (with functionCall & thoughtSignature) to turn history
                    contents.append({
                        "role": "model",
                        "parts": content_parts
                    })

                    # Append functionResponse turn under role 'user'
                    contents.append({
                        "role": "user",
                        "parts": [{
                            "functionResponse": {
                                "name": tool_req.tool_name,
                                "response": tool_result
                            }
                        }]
                    })
                    
                    request_body["contents"] = contents
                    continue # Re-run LLM loop with function output context

                # Case B: Final Natural Language Text Response returned
                if text_response:
                    return text_response.strip()

        return "Thank you! Let me know if you need anything else."

    def _generate_mock_fallback_response(self, user_input: str) -> str:
        """Development fallback response when GEMINI_API_KEY is not configured."""
        user_lower = user_input.lower()
        if "hello" in user_lower or "hi" in user_lower:
            return "Hello! Welcome to our store. How can I assist you today?"
        elif "price" in user_lower or "stock" in user_lower or "sku" in user_lower:
            return "I can certainly help you check stock and pricing for our items! Could you provide the SKU code?"
        elif "human" in user_lower or "agent" in user_lower:
            return "I am connecting you with one of our human support representatives right away."
        return f"Thank you for your message! Our automated assistant received: '{user_input}'"
