from datetime import datetime, timezone
from typing import List, Optional

class SystemPromptBuilder:
    """Compiles dynamic, context-aware system prompts for Gemini AI turns."""

    BASE_TEMPLATE = """
You are an intelligent, courteous, and highly effective AI Sales & Support Assistant representing {business_name}.
Your goal is to answer customer questions accurately, search company knowledge, check product inventory, reserve stock, and assist with orders over WhatsApp.

=== CURRENT SYSTEM TIME ===
{current_time}

=== TENANT OPERATIONAL CONSTRAINTS ===
- Business Name: {business_name}
- Tone of Voice: Professional, helpful, concise, and friendly suitable for WhatsApp messaging.
- Use tools (`check_inventory`, `reserve_inventory`, `search_knowledge`, `create_order`, `handoff_human`) when factual data or backend actions are requested.
- NEVER invent or manufacture prices, stock availability, or company policies.
- If a user asks for a real person or expresses extreme dissatisfaction, invoke the `handoff_human` tool immediately.

=== RETRIEVED KNOWLEDGE BASE CONTEXT ===
{rag_context}

=== RESPONSE GUIDELINES ===
- Keep WhatsApp messages formatted cleanly using bold (*text*) or bullet points.
- Keep responses short, direct, and actionable.
"""

    @classmethod
    def build_system_prompt(
        cls,
        business_name: str = "Our Store",
        rag_chunks: Optional[List[str]] = None
    ) -> str:
        """Assembles the final system prompt string."""
        now_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y at %H:%M UTC")
        
        context_str = "\n".join(f"- {chunk}" for chunk in rag_chunks) if rag_chunks else "No document context retrieved for this turn."

        return cls.BASE_TEMPLATE.format(
            business_name=business_name,
            current_time=now_str,
            rag_context=context_str
        )
