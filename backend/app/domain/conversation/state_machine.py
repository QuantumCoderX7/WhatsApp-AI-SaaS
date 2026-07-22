from enum import Enum
from typing import Set

class ConversationState(str, Enum):
    IDLE = "IDLE"
    AI_ACTIVE = "AI_ACTIVE"
    AWAITING_CUSTOMER = "AWAITING_CUSTOMER"
    HUMAN_ESCALATED = "HUMAN_ESCALATED"
    CLOSED = "CLOSED"

class InvalidStateTransitionError(Exception):
    pass

class ConversationStateMachine:
    """Manages valid state transitions for WhatsApp conversations."""

    VALID_TRANSITIONS: dict[ConversationState, Set[ConversationState]] = {
        ConversationState.IDLE: {
            ConversationState.AI_ACTIVE, 
            ConversationState.CLOSED
        },
        ConversationState.AI_ACTIVE: {
            ConversationState.AWAITING_CUSTOMER,
            ConversationState.HUMAN_ESCALATED,
            ConversationState.CLOSED
        },
        ConversationState.AWAITING_CUSTOMER: {
            ConversationState.AI_ACTIVE,
            ConversationState.HUMAN_ESCALATED,
            ConversationState.CLOSED
        },
        ConversationState.HUMAN_ESCALATED: {
            ConversationState.AI_ACTIVE,
            ConversationState.CLOSED
        },
        ConversationState.CLOSED: {
            ConversationState.AI_ACTIVE
        }
    }

    @classmethod
    def transition(cls, current_state_str: str, target_state: ConversationState) -> str:
        try:
            current_state = ConversationState(current_state_str)
        except ValueError:
            current_state = ConversationState.IDLE

        valid_targets = cls.VALID_TRANSITIONS.get(current_state, set())
        if target_state not in valid_targets:
            raise InvalidStateTransitionError(
                f"Invalid transition from state '{current_state.value}' to '{target_state.value}'."
            )
        return target_state.value
