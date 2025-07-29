"""Tests for mAIgic_core LLM API interfaces.

These tests verify the interface contracts and demonstrate proper usage patterns.
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Optional

from ..interfaces import LLMClient, LLMProvider, ConversationRepository, LLMClientFactory
from ..types import (
    AssistantInteraction,
    GoalProgressAssessment,
    Intent,
    IntentType,
    SchedulingDecision,
    SchedulingRequest,
    UserContext,
    UserGoal,
    UserTask,
    TaskPriority,
    GoalStatus,
    LLMConfig,
)
from ..exceptions import (
    LLMError,
    LLMIntentParsingError,
    ConversationStorageError,
)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    def get_available_models(self) -> List[str]:
        return ["mock-model-1", "mock-model-2"]
    
    def get_default_model(self) -> str:
        return "mock-model-1"
    
    async def generate_completion(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> str:
        return f"Mock response for {model_name}: {prompt[:50]}..."
    
    async def close(self) -> None:
        pass


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self):
        self.provider = MockLLMProvider()
        self.closed = False
    
    async def parse_intent(
        self,
        text: str,
        context: UserContext,
        user_id: str = "default"
    ) -> Intent:
        if "schedule" in text.lower():
            return Intent(
                type=IntentType.SCHEDULE_TASK,
                original_text=text,
                confidence=0.9
            )
        elif "goal" in text.lower():
            return Intent(
                type=IntentType.UPDATE_GOAL,
                original_text=text,
                confidence=0.8
            )
        else:
            return Intent(
                type=IntentType.GENERAL_CONVERSATION,
                original_text=text,
                confidence=0.7
            )
    
    async def make_scheduling_decision(
        self,
        request: SchedulingRequest,
        user_id: str = "default"
    ) -> SchedulingDecision:
        return SchedulingDecision(
            scheduled_tasks=[],
            reasoning="Mock scheduling decision",
            confidence=0.8,
            conflicts=[],
            alternative_options=[],
            follow_up_actions=["Create calendar event"]
        )
    
    async def assess_goal_progress(
        self,
        goal: UserGoal,
        recent_activities: List[AssistantInteraction],
        user_id: str = "default"
    ) -> GoalProgressAssessment:
        return GoalProgressAssessment(
            goal_id=goal.id,
            current_progress=0.5,
            progress_delta=0.1,
            completion_confidence=0.7,
            blockers=[],
            suggestions=["Keep up the good work"],
            next_actions=["Continue current tasks"],
            assessment_reasoning="Mock assessment"
        )
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[UserContext] = None,
        user_id: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        return f"Mock response to: {prompt}"
    
    async def close(self) -> None:
        self.closed = True


class MockConversationRepository(ConversationRepository):
    """Mock conversation repository for testing."""
    
    def __init__(self):
        self.interactions = {}
    
    async def save_interaction(
        self,
        interaction: AssistantInteraction,
        user_id: str = "default"
    ) -> None:
        if user_id not in self.interactions:
            self.interactions[user_id] = []
        self.interactions[user_id].append(interaction)
    
    async def get_recent_interactions(
        self,
        user_id: str = "default",
        days: int = 7,
        limit: int = 50
    ) -> List[AssistantInteraction]:
        user_interactions = self.interactions.get(user_id, [])
        cutoff = datetime.now() - timedelta(days=days)
        recent = [i for i in user_interactions if i.timestamp >= cutoff]
        return recent[:limit]
    
    async def get_interactions_by_intent_type(
        self,
        intent_type: str,
        user_id: str = "default",
        days: int = 30,
        limit: int = 20
    ) -> List[AssistantInteraction]:
        user_interactions = self.interactions.get(user_id, [])
        cutoff = datetime.now() - timedelta(days=days)
        matching = [
            i for i in user_interactions 
            if i.timestamp >= cutoff and 
            i.parsed_intent and 
            i.parsed_intent.type == intent_type
        ]
        return matching[:limit]
    
    async def delete_user_data(self, user_id: str) -> None:
        if user_id in self.interactions:
            del self.interactions[user_id]


@pytest.fixture
def mock_llm_client():
    return MockLLMClient()


@pytest.fixture
def mock_conversation_repo():
    return MockConversationRepository()


@pytest.fixture
def sample_context():
    return UserContext(
        user_id="test_user",
        current_time=datetime.now(),
        active_goals=[
            UserGoal(
                id="goal_1",
                title="Complete thesis",
                priority=9,
                status=GoalStatus.ACTIVE
            )
        ],
        pending_tasks=[
            UserTask(
                id="task_1",
                title="Write chapter 3",
                priority=TaskPriority.HIGH,
                estimated_duration=timedelta(hours=4)
            )
        ]
    )


@pytest.fixture
def sample_interaction():
    return AssistantInteraction(
        id="interaction_1",
        user_id="test_user",
        input_text="Schedule work on thesis",
        parsed_intent=Intent(
            type=IntentType.SCHEDULE_TASK,
            original_text="Schedule work on thesis"
        ),
        llm_response="I'll schedule thesis work for you",
        actions_taken=["create_calendar_event"],
        success=True
    )


class TestLLMClient:
    """Test LLM client interface."""
    
    @pytest.mark.asyncio
    async def test_parse_intent_scheduling(self, mock_llm_client, sample_context):
        intent = await mock_llm_client.parse_intent(
            "Schedule thesis work for tomorrow",
            sample_context
        )
        
        assert intent.type == IntentType.SCHEDULE_TASK
        assert intent.confidence > 0
        assert "schedule" in intent.original_text.lower()
    
    @pytest.mark.asyncio
    async def test_parse_intent_goal_update(self, mock_llm_client, sample_context):
        intent = await mock_llm_client.parse_intent(
            "Update my goal progress",
            sample_context
        )
        
        assert intent.type == IntentType.UPDATE_GOAL
        assert intent.confidence > 0
    
    @pytest.mark.asyncio
    async def test_make_scheduling_decision(self, mock_llm_client, sample_context):
        request = SchedulingRequest(
            intent=Intent(type=IntentType.SCHEDULE_TASK),
            context=sample_context
        )
        
        decision = await mock_llm_client.make_scheduling_decision(request)
        
        assert isinstance(decision, SchedulingDecision)
        assert decision.confidence > 0
        assert decision.reasoning
    
    @pytest.mark.asyncio
    async def test_assess_goal_progress(self, mock_llm_client, sample_context):
        goal = sample_context.active_goals[0]
        
        assessment = await mock_llm_client.assess_goal_progress(
            goal,
            []
        )
        
        assert assessment.goal_id == goal.id
        assert 0 <= assessment.current_progress <= 1
        assert assessment.assessment_reasoning
    
    @pytest.mark.asyncio
    async def test_generate_response(self, mock_llm_client, sample_context):
        response = await mock_llm_client.generate_response(
            "What should I work on today?",
            sample_context
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_close(self, mock_llm_client):
        await mock_llm_client.close()
        assert mock_llm_client.closed


class TestLLMProvider:
    """Test LLM provider interface."""
    
    def test_get_available_models(self):
        provider = MockLLMProvider()
        models = provider.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)
    
    def test_get_default_model(self):
        provider = MockLLMProvider()
        default = provider.get_default_model()
        
        assert isinstance(default, str)
        assert default in provider.get_available_models()
    
    @pytest.mark.asyncio
    async def test_generate_completion(self):
        provider = MockLLMProvider()
        
        response = await provider.generate_completion(
            "mock-model-1",
            "Test prompt",
            temperature=0.5
        )
        
        assert isinstance(response, str)
        assert "Test prompt" in response


class TestConversationRepository:
    """Test conversation repository interface."""
    
    @pytest.mark.asyncio
    async def test_save_and_retrieve_interaction(
        self, 
        mock_conversation_repo, 
        sample_interaction
    ):
        await mock_conversation_repo.save_interaction(sample_interaction)
        
        interactions = await mock_conversation_repo.get_recent_interactions()
        
        assert len(interactions) == 1
        assert interactions[0].id == sample_interaction.id
    
    @pytest.mark.asyncio
    async def test_get_interactions_by_intent_type(
        self,
        mock_conversation_repo,
        sample_interaction
    ):
        await mock_conversation_repo.save_interaction(sample_interaction)
        
        interactions = await mock_conversation_repo.get_interactions_by_intent_type(
            IntentType.SCHEDULE_TASK
        )
        
        assert len(interactions) == 1
        assert interactions[0].parsed_intent.type == IntentType.SCHEDULE_TASK
    
    @pytest.mark.asyncio
    async def test_delete_user_data(self, mock_conversation_repo, sample_interaction):
        await mock_conversation_repo.save_interaction(sample_interaction)
        await mock_conversation_repo.delete_user_data("test_user")
        
        interactions = await mock_conversation_repo.get_recent_interactions("test_user")
        assert len(interactions) == 0


class TestAbstractEnforcement:
    """Test that ABC properly enforces implementation."""
    
    def test_cannot_instantiate_abstract_llm_client(self):
        with pytest.raises(TypeError):
            LLMClient()
    
    def test_cannot_instantiate_abstract_provider(self):
        with pytest.raises(TypeError):
            LLMProvider()
    
    def test_cannot_instantiate_abstract_repository(self):
        with pytest.raises(TypeError):
            ConversationRepository()
    
    def test_incomplete_implementation_fails(self):
        class IncompleteLLMClient(LLMClient):
            # Missing required methods
            pass
        
        with pytest.raises(TypeError):
            IncompleteLLMClient()


class TestIntegration:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(
        self,
        mock_llm_client,
        mock_conversation_repo,
        sample_context
    ):
        # Parse intent
        intent = await mock_llm_client.parse_intent(
            "Schedule thesis work for tomorrow",
            sample_context
        )
        
        # Make scheduling decision
        request = SchedulingRequest(intent=intent, context=sample_context)
        decision = await mock_llm_client.make_scheduling_decision(request)
        
        # Save interaction
        interaction = AssistantInteraction(
            id="test_interaction",
            input_text="Schedule thesis work for tomorrow",
            parsed_intent=intent,
            llm_response=decision.reasoning,
            success=True
        )
        await mock_conversation_repo.save_interaction(interaction)
        
        # Retrieve and verify
        saved_interactions = await mock_conversation_repo.get_recent_interactions()
        assert len(saved_interactions) == 1
        assert saved_interactions[0].parsed_intent.type == IntentType.SCHEDULE_TASK