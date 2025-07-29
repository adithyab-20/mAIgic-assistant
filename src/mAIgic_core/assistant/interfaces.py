"""Assistant interfaces for workflow orchestration and session management.

This module defines the abstract interfaces that assistant implementations
must implement for scheduling, workflow execution, and session management.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Import core types from LLM API and assistant
from ..llm.llm_api.types import (
    Intent,
    UserContext,
    SchedulingDecision,
    ConflictInfo,
    AssistantInteraction,
)
from .types import (
    WorkflowResult,
    AssistantResponse,
    SessionState,
    AssistantConfig,
    ContextSnapshot,
    WorkflowStep,
)


class SchedulingEngine(ABC):
    """Interface for intelligent scheduling operations.
    
    Handles scheduling decisions, conflict resolution, and calendar management
    using LLM intelligence combined with business logic.
    """
    
    @abstractmethod
    async def make_scheduling_decision(
        self,
        intent: Intent,
        context: UserContext,
        user_id: str = "default"
    ) -> SchedulingDecision:
        """Make intelligent scheduling decisions based on intent and context.
        
        Args:
            intent: Parsed user intent for scheduling
            context: Complete user context for decision making
            user_id: User identifier for personalization
            
        Returns:
            Structured scheduling decision with reasoning
            
        Raises:
            SchedulingError: If scheduling decision fails
            ContextError: If context is insufficient or stale
        """
    
    @abstractmethod
    async def resolve_conflicts(
        self,
        conflicts: List[ConflictInfo],
        context: UserContext,
        user_id: str = "default"
    ) -> List[SchedulingDecision]:
        """Resolve scheduling conflicts with intelligent alternatives.
        
        Args:
            conflicts: List of scheduling conflicts to resolve
            context: User context for resolution strategies
            user_id: User identifier for personalization
            
        Returns:
            List of alternative scheduling decisions
            
        Raises:
            ConflictResolutionError: If conflicts cannot be resolved
            SchedulingError: If scheduling operation fails
        """
    
    @abstractmethod
    async def optimize_schedule(
        self,
        context: UserContext,
        optimization_window_days: int = 7,
        user_id: str = "default"
    ) -> List[SchedulingDecision]:
        """Optimize existing schedule for efficiency and goal alignment.
        
        Args:
            context: User context with current schedule and goals
            optimization_window_days: Number of days to optimize
            user_id: User identifier for personalization
            
        Returns:
            List of optimization recommendations
            
        Raises:
            SchedulingError: If optimization fails
        """


class WorkflowEngine(ABC):
    """Interface for orchestrating multi-service workflows.
    
    Coordinates execution of complex workflows that involve multiple
    services (calendar, email, speech, etc.) in response to user intents.
    """
    
    @abstractmethod
    async def execute_workflow(
        self,
        intent: Intent,
        context: UserContext,
        user_id: str = "default"
    ) -> WorkflowResult:
        """Execute a complete workflow based on user intent.
        
        Args:
            intent: Parsed user intent
            context: User context for workflow execution
            user_id: User identifier
            
        Returns:
            Complete workflow execution result
            
        Raises:
            WorkflowError: If workflow execution fails
            ServiceIntegrationError: If service integration fails
            WorkflowTimeoutError: If workflow times out
        """
    
    @abstractmethod
    async def get_workflow_status(
        self,
        workflow_id: str,
        user_id: str = "default"
    ) -> WorkflowResult:
        """Get current status of a running workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            user_id: User identifier
            
        Returns:
            Current workflow status and results
            
        Raises:
            WorkflowError: If workflow not found or status unavailable
        """
    
    @abstractmethod
    async def cancel_workflow(
        self,
        workflow_id: str,
        user_id: str = "default"
    ) -> bool:
        """Cancel a running workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            user_id: User identifier
            
        Returns:
            True if workflow was successfully cancelled
            
        Raises:
            WorkflowError: If workflow cannot be cancelled
        """
    
    @abstractmethod
    async def list_active_workflows(
        self,
        user_id: str = "default"
    ) -> List[WorkflowResult]:
        """List all active workflows for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active workflow results
        """


class AssistantSession(ABC):
    """Interface for managing assistant sessions and interactions.
    
    Handles voice-to-voice interactions, session state management,
    and conversation flow control.
    """
    
    @abstractmethod
    async def start_session(
        self,
        user_id: str = "default",
        config: Optional[AssistantConfig] = None
    ) -> SessionState:
        """Start a new assistant session.
        
        Args:
            user_id: User identifier
            config: Optional session configuration
            
        Returns:
            New session state
            
        Raises:
            SessionError: If session creation fails
            ConfigurationError: If configuration is invalid
        """
    
    @abstractmethod
    async def process_voice_input(
        self,
        audio_data: bytes,
        session_id: str,
        user_id: str = "default"
    ) -> AssistantResponse:
        """Process voice input and return complete response.
        
        This is the main entry point for voice-first interactions.
        
        Args:
            audio_data: Raw audio data from user
            session_id: Active session identifier
            user_id: User identifier
            
        Returns:
            Complete assistant response with actions taken
            
        Raises:
            SessionError: If session is invalid or expired
            VoiceProcessingError: If voice processing fails
            WorkflowError: If triggered workflow fails
        """
    
    @abstractmethod
    async def process_text_input(
        self,
        text: str,
        session_id: str,
        user_id: str = "default"
    ) -> AssistantResponse:
        """Process text input and return complete response.
        
        Args:
            text: User text input
            session_id: Active session identifier
            user_id: User identifier
            
        Returns:
            Complete assistant response with actions taken
            
        Raises:
            SessionError: If session is invalid or expired
            WorkflowError: If triggered workflow fails
        """
    
    @abstractmethod
    async def get_session_state(
        self,
        session_id: str,
        user_id: str = "default"
    ) -> SessionState:
        """Get current session state.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Current session state
            
        Raises:
            SessionError: If session not found
        """
    
    @abstractmethod
    async def end_session(
        self,
        session_id: str,
        user_id: str = "default"
    ) -> bool:
        """End an assistant session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            True if session was successfully ended
            
        Raises:
            SessionError: If session cannot be ended
        """


class ContextManager(ABC):
    """Interface for managing user context and state.
    
    Handles context building, caching, and refresh operations
    to provide rich context for LLM decision making.
    """
    
    @abstractmethod
    async def build_context(
        self,
        user_id: str = "default",
        force_refresh: bool = False
    ) -> UserContext:
        """Build complete user context from all available sources.
        
        Args:
            user_id: User identifier
            force_refresh: Force refresh of cached context
            
        Returns:
            Complete user context
            
        Raises:
            ContextError: If context building fails
            ServiceIntegrationError: If service data unavailable
        """
    
    @abstractmethod
    async def update_context(
        self,
        user_id: str,
        partial_context: Dict[str, Any],
        merge_strategy: str = "update"
    ) -> UserContext:
        """Update specific parts of user context.
        
        Args:
            user_id: User identifier
            partial_context: Partial context updates
            merge_strategy: How to merge updates ("update", "replace", "merge")
            
        Returns:
            Updated complete user context
            
        Raises:
            ContextError: If context update fails
        """
    
    @abstractmethod
    async def get_context_snapshot(
        self,
        user_id: str = "default"
    ) -> ContextSnapshot:
        """Get a snapshot of current user context.
        
        Args:
            user_id: User identifier
            
        Returns:
            Context snapshot with timestamp and hash
            
        Raises:
            ContextError: If context snapshot creation fails
        """
    
    @abstractmethod
    async def is_context_stale(
        self,
        user_id: str,
        max_age_minutes: int = 30
    ) -> bool:
        """Check if user context needs refresh.
        
        Args:
            user_id: User identifier
            max_age_minutes: Maximum age before context is stale
            
        Returns:
            True if context is stale and needs refresh
        """
    
    @abstractmethod
    async def clear_context(
        self,
        user_id: str
    ) -> bool:
        """Clear cached context for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if context was successfully cleared
            
        Raises:
            ContextError: If context clearing fails
        """ 