"""LLM API interfaces for mAIgic_core.

This module defines generic LLM interfaces that can be implemented
by different providers (OpenAI, Gemini, Claude, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .types import (
    Intent,
    UserContext,
    UserGoal,
    AssistantInteraction,
    GoalProgressAssessment,
    LLMConfig,
)


class LLMClient(ABC):
    """Generic LLM client for AI operations.
    
    This interface provides core LLM capabilities that can be used
    by higher-level assistant components for various tasks.
    """
    
    @abstractmethod
    async def parse_intent(
        self,
        text: str,
        context: UserContext,
        user_id: str = "default"
    ) -> Intent:
        """Parse user intent from natural language with context.
        
        Args:
            text: User's natural language input
            context: Current user context for better parsing
            user_id: User identifier for personalization
            
        Returns:
            Structured intent object with type and parameters
            
        Raises:
            LLMIntentParsingError: If intent parsing fails
            LLMConnectionError: If LLM service is unavailable
        """
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: Optional[UserContext] = None,
        user_id: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate a natural language response.
        
        Args:
            prompt: Text prompt for the LLM
            context: Optional user context for personalization
            user_id: User identifier for personalization
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
            
        Raises:
            LLMResponseError: If response generation fails
            LLMConnectionError: If LLM service is unavailable
        """
    
    @abstractmethod
    async def assess_goal_progress(
        self,
        goal: UserGoal,
        recent_activities: List[AssistantInteraction],
        user_id: str = "default"
    ) -> GoalProgressAssessment:
        """Assess progress toward a specific goal.
        
        Args:
            goal: User goal to assess
            recent_activities: Recent user activities and interactions
            user_id: User identifier for personalization
            
        Returns:
            Progress assessment with recommendations
            
        Raises:
            LLMGoalAssessmentError: If goal assessment fails
            LLMConnectionError: If LLM service is unavailable
        """
    
    @abstractmethod
    async def close(self) -> None:
        """Close LLM client and clean up resources."""


class LLMProvider(ABC):
    """Provider interface for different LLM services.
    
    Abstracts away the specifics of different LLM providers
    (OpenAI, Gemini, Claude, etc.) behind a common interface.
    """
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models from this provider.
        
        Returns:
            List of model names as strings
        """
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model name for this provider.
        
        Returns:
            Default model name
        """
    
    @abstractmethod
    async def generate_completion(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs: Any
    ) -> str:
        """Generate completion using specified model.
        
        Args:
            model_name: Name of the model to use
            prompt: Text prompt for completion
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Returns:
            Generated completion text
            
        Raises:
            LLMProviderError: If completion generation fails
            LLMModelNotFoundError: If model is not available
        """
    
    @abstractmethod
    async def close(self) -> None:
        """Close provider connections and clean up resources."""


class ConversationRepository(ABC):
    """Repository for storing and retrieving assistant interactions.
    
    Handles persistent storage of user interactions with the assistant
    for context building and conversation history.
    """
    
    @abstractmethod
    async def save_interaction(
        self,
        interaction: AssistantInteraction,
        user_id: str = "default"
    ) -> None:
        """Save an assistant interaction.
        
        Args:
            interaction: Complete interaction record
            user_id: User identifier for organization
            
        Raises:
            ConversationSaveError: If save operation fails
        """
    
    @abstractmethod
    async def get_recent_interactions(
        self,
        user_id: str = "default",
        days: int = 7,
        limit: int = 50
    ) -> List[AssistantInteraction]:
        """Get recent assistant interactions for context.
        
        Args:
            user_id: User identifier
            days: Number of days back to retrieve
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions, most recent first
            
        Raises:
            ConversationRetrievalError: If retrieval fails
        """
    
    @abstractmethod
    async def get_interactions_by_intent_type(
        self,
        intent_type: str,
        user_id: str = "default",
        days: int = 30,
        limit: int = 20
    ) -> List[AssistantInteraction]:
        """Get interactions by specific intent type.
        
        Args:
            intent_type: Type of intent to filter by
            user_id: User identifier
            days: Number of days back to search
            limit: Maximum number of interactions to return
            
        Returns:
            List of matching interactions
            
        Raises:
            ConversationRetrievalError: If retrieval fails
        """
    
    @abstractmethod
    async def delete_user_data(self, user_id: str) -> None:
        """Delete all stored data for a user.
        
        Args:
            user_id: User identifier
            
        Raises:
            ConversationDeleteError: If deletion fails
        """


class LLMClientFactory(ABC):
    """Factory for creating LLM clients with different providers."""
    
    @abstractmethod
    def create_client(
        self,
        provider_name: str,
        config: Dict[str, Any],
        conversation_repo: Optional[ConversationRepository] = None
    ) -> LLMClient:
        """Create an LLM client for the specified provider.
        
        Args:
            provider_name: Name of the LLM provider ("openai", "gemini", etc.)
            config: Provider-specific configuration
            conversation_repo: Optional conversation repository
            
        Returns:
            Configured LLM client instance
            
        Raises:
            LLMFactoryError: If provider is not supported
            LLMConfigurationError: If configuration is invalid
        """
    
    @abstractmethod
    def get_supported_providers(self) -> List[str]:
        """Get list of supported LLM providers.
        
        Returns:
            List of provider names
        """