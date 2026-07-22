from uuid import UUID
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.inventory.models import Product, InventoryItem
from app.domain.conversation.repository import ConversationRepository
from app.domain.conversation.state_machine import ConversationStateMachine, ConversationState
from app.domain.ai.guardrails import ToolCallRequest

class ToolExecutor:
    """Executes backend functions invoked by Gemini LLM function calls."""

    def __init__(self, db: AsyncSession, tenant_id: UUID, conversation_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.conversation_id = conversation_id

    async def execute(self, tool_request: ToolCallRequest) -> Dict[str, Any]:
        """Routes tool request to the appropriate handler function."""
        tool_name = tool_request.tool_name
        args = tool_request.arguments

        if tool_name == "check_inventory":
            return await self._check_inventory(args.get("sku"))
        elif tool_name == "reserve_inventory":
            return await self._reserve_inventory(args.get("sku"), args.get("quantity", 1))
        elif tool_name == "search_knowledge":
            return await self._search_knowledge(args.get("query"))
        elif tool_name == "create_order":
            return await self._create_order(args.get("sku"), args.get("quantity", 1))
        elif tool_name == "handoff_human":
            return await self._handoff_human(args.get("reason", "Customer requested agent escalation"))
        else:
            return {"error": f"Unknown tool execution requested: {tool_name}"}

    async def _check_inventory(self, sku: str) -> Dict[str, Any]:
        """Checks available stock for a product SKU."""
        if not sku:
            return {"error": "Missing required SKU parameter."}

        stmt = (
            select(Product, InventoryItem)
            .join(InventoryItem, Product.id == InventoryItem.product_id)
            .where(Product.tenant_id == self.tenant_id, Product.sku == sku.upper(), Product.is_active.is_(True))
        )
        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return {"status": "not_found", "message": f"Product with SKU '{sku}' was not found in catalog."}

        product, inventory = row
        available = inventory.quantity_available - inventory.quantity_reserved
        return {
            "sku": product.sku,
            "product_name": product.name,
            "price": float(product.price),
            "currency": product.currency,
            "quantity_available": max(0, available),
            "in_stock": available > 0
        }

    async def _reserve_inventory(self, sku: str, quantity: int) -> Dict[str, Any]:
        """Placeholder for inventory reservation (full concurrency logic in Sprint 5)."""
        res = await self._check_inventory(sku)
        if not res.get("in_stock") or res.get("quantity_available", 0) < quantity:
            return {"status": "failed", "message": f"Insufficient stock for SKU '{sku}'. Available: {res.get('quantity_available', 0)}"}
        
        return {
            "status": "reserved",
            "sku": sku,
            "quantity_reserved": quantity,
            "reservation_ttl_minutes": 15
        }

    async def _search_knowledge(self, query: str) -> Dict[str, Any]:
        """Performs pgvector semantic search across business knowledge documents."""
        if not query:
            return {"error": "Missing search query parameter."}

        from app.domain.rag.retriever import RAGRetriever
        retriever = RAGRetriever(self.db)
        chunks = await retriever.search_relevant_chunks(self.tenant_id, query, top_k=3)

        if not chunks:
            return {
                "status": "no_results",
                "message": f"No knowledge document context matched the query: '{query}'."
            }

        return {
            "status": "success",
            "query": query,
            "results": [c["content"] for c in chunks]
        }

    async def _create_order(self, sku: str, quantity: int) -> Dict[str, Any]:
        """Executes transactional order checkout via OrderService."""
        if not sku or quantity <= 0:
            return {"error": "Invalid order parameters."}

        try:
            from app.domain.order.service import OrderService
            order_service = OrderService(self.db)
            order = await order_service.create_order(
                tenant_id=self.tenant_id,
                conversation_id=self.conversation_id,
                items=[{"sku": sku, "quantity": quantity}]
            )
            return {
                "status": "created",
                "order_id": str(order.id),
                "sku": sku,
                "quantity": quantity,
                "total_amount": float(order.total_amount),
                "currency": order.currency,
                "payment_status": order.payment_status,
                "message": f"Order #{str(order.id)[:8]} created successfully."
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    async def _handoff_human(self, reason: str) -> Dict[str, Any]:
        """Transitions conversation state to HUMAN_ESCALATED and alerts support pool."""
        repo = ConversationRepository(self.db)
        await repo.update_status(self.conversation_id, ConversationState.HUMAN_ESCALATED.value)
        await repo.append_message(
            tenant_id=self.tenant_id,
            conversation_id=self.conversation_id,
            sender_type="SYSTEM",
            content=f"[System Event] Human handoff triggered: {reason}"
        )
        return {
            "status": "escalated",
            "message": "Conversation transferred to human support queue."
        }
