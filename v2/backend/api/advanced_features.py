"""
Advanced Features API

Provides endpoints for advanced agent capabilities:
- Learning engine management
- Workflow builder and execution
- Advanced NLP processing
- Self-improvement and adaptation
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import logging

from ..services.agents.learning_engine import LearningEngine, AgentExperience, LearningPattern
from ..services.agents.workflow_builder import WorkflowEngine, WorkflowDefinition, WorkflowExecution
from ..services.agents.advanced_nlp import AdvancedNLPProcessor, ConversationContext, Intent
from ..core.dependencies import get_learning_engine, get_workflow_engine, get_nlp_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced", tags=["advanced-features"])


# Learning Engine Models
class ExperienceData(BaseModel):
    """Agent experience data."""
    task_type: str = Field(..., description="Type of task performed")
    input_features: Dict[str, Any] = Field(..., description="Input features for the task")
    execution_result: Dict[str, Any] = Field(..., description="Execution result data")
    context: Dict[str, Any] = Field(..., description="Execution context")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    lessons_learned: List[str] = Field(default_factory=list, description="Lessons learned")


class LearningPatternResponse(BaseModel):
    """Learning pattern response."""
    pattern_id: str
    pattern_type: str
    conditions: Dict[str, Any]
    outcome: Any
    confidence: float
    sample_size: int
    last_updated: str


# Workflow Builder Models
class WorkflowNodeData(BaseModel):
    """Workflow node data."""
    node_id: str
    node_type: str
    name: str
    description: str = ""
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, float] = Field(default_factory=dict)


class WorkflowEdgeData(BaseModel):
    """Workflow edge data."""
    edge_id: str
    source_node: str
    target_node: str
    condition: Optional[str] = None
    priority: int = 1


class WorkflowDefinitionData(BaseModel):
    """Workflow definition data."""
    name: str
    description: str = ""
    nodes: List[WorkflowNodeData]
    edges: List[WorkflowEdgeData]


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response."""
    execution_id: str
    workflow_id: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    current_nodes: List[str]
    completed_nodes: List[str]
    failed_nodes: List[str]
    node_results: Dict[str, Any]


# NLP Processor Models
class NLPProcessingRequest(BaseModel):
    """NLP processing request."""
    text: str = Field(..., description="Text to process")
    conversation_id: Optional[str] = Field(None, description="Conversation context ID")
    language: str = Field("en", description="Language code")


class IntentResponse(BaseModel):
    """Intent recognition response."""
    name: str
    confidence: float
    entities: Dict[str, Any]
    context: Dict[str, Any]
    metadata: Dict[str, Any]


class ConversationContextResponse(BaseModel):
    """Conversation context response."""
    conversation_id: str
    user_id: Optional[str]
    message_count: int
    topics: List[str]
    sentiment_trend: List[float]
    recent_intents: List[str]
    created_at: str
    last_updated: str


class NLPProcessingResponse(BaseModel):
    """Complete NLP processing response."""
    original_text: str
    language: str
    processed_at: str
    tokens: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    intent: Optional[IntentResponse]
    sentiment: Dict[str, Any]
    key_phrases: List[str]
    summary: str
    complexity_score: float
    readability_score: float
    topics: List[str]
    semantic_matches: List[Dict[str, Any]]
    knowledge_entities: List[Dict[str, Any]]
    confidence: float


# Learning Engine Endpoints
@router.post("/learning/experience")
async def record_experience(
    experience: ExperienceData,
    learning_engine: LearningEngine = Depends(get_learning_engine)
):
    """Record an agent execution experience for learning."""
    try:
        # Convert to AgentExperience
        agent_experience = AgentExperience(
            task_type=experience.task_type,
            input_features=experience.input_features,
            execution_result=experience.execution_result,
            context=experience.context,
            performance_metrics=experience.performance_metrics,
            lessons_learned=experience.lessons_learned
        )

        learning_engine.record_experience(agent_experience)

        return {"message": "Experience recorded successfully"}

    except Exception as e:
        logger.error(f"Failed to record experience: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/patterns/success/{task_type}")
async def get_success_patterns(
    task_type: str,
    learning_engine: LearningEngine = Depends(get_learning_engine)
) -> List[LearningPatternResponse]:
    """Get learned success patterns for a task type."""
    try:
        patterns = learning_engine.get_success_patterns(task_type)

        return [
            LearningPatternResponse(
                pattern_id=pattern.pattern_id,
                pattern_type=pattern.pattern_type,
                conditions=pattern.conditions,
                outcome=pattern.outcome,
                confidence=pattern.confidence,
                sample_size=pattern.sample_size,
                last_updated=pattern.last_updated.isoformat()
            )
            for pattern in patterns
        ]

    except Exception as e:
        logger.error(f"Failed to get success patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/patterns/failure/{task_type}")
async def get_failure_patterns(
    task_type: str,
    learning_engine: LearningEngine = Depends(get_learning_engine)
) -> List[LearningPatternResponse]:
    """Get learned failure patterns for a task type."""
    try:
        patterns = learning_engine.get_failure_patterns(task_type)

        return [
            LearningPatternResponse(
                pattern_id=pattern.pattern_id,
                pattern_type=pattern.pattern_type,
                conditions=pattern.conditions,
                outcome=pattern.outcome,
                confidence=pattern.confidence,
                sample_size=pattern.sample_size,
                last_updated=pattern.last_updated.isoformat()
            )
            for pattern in patterns
        ]

    except Exception as e:
        logger.error(f"Failed to get failure patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/optimization/{task_type}")
async def get_optimization_suggestions(
    task_type: str,
    learning_engine: LearningEngine = Depends(get_learning_engine)
) -> List[Dict[str, Any]]:
    """Get optimization suggestions based on learned patterns."""
    try:
        suggestions = learning_engine.get_optimization_suggestions(task_type)
        return suggestions

    except Exception as e:
        logger.error(f"Failed to get optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/collaborative")
async def collaborative_learning(
    agent_data: Dict[str, Any],
    learning_engine: LearningEngine = Depends(get_learning_engine)
) -> Dict[str, Any]:
    """Perform collaborative learning with other agents."""
    try:
        other_agents_data = [agent_data]  # Single agent data for now
        result = await learning_engine.collaborative_learning(other_agents_data)
        return result

    except Exception as e:
        logger.error(f"Collaborative learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/prediction/{task_type}")
async def get_performance_prediction(
    task_type: str,
    features: Dict[str, Any],
    learning_engine: LearningEngine = Depends(get_learning_engine)
) -> Dict[str, Any]:
    """Get performance prediction for a task type."""
    try:
        prediction = await learning_engine.get_performance_prediction(task_type, features)
        return prediction

    except Exception as e:
        logger.error(f"Failed to get performance prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/stats")
async def get_learning_stats(
    learning_engine: LearningEngine = Depends(get_learning_engine)
) -> Dict[str, Any]:
    """Get learning engine statistics."""
    try:
        return learning_engine.get_learning_stats()

    except Exception as e:
        logger.error(f"Failed to get learning stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow Builder Endpoints
@router.post("/workflows/create")
async def create_workflow(
    workflow_data: WorkflowDefinitionData,
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
) -> Dict[str, Any]:
    """Create a new workflow definition."""
    try:
        # Create workflow definition
        workflow = WorkflowDefinition(
            workflow_id=None,  # Auto-generate
            name=workflow_data.name,
            description=workflow_data.description
        )

        # Add nodes
        for node_data in workflow_data.nodes:
            from ..services.agents.workflow_builder import WorkflowNodeType
            node = WorkflowNode(
                node_id=node_data.node_id,
                node_type=WorkflowNodeType(node_data.node_type),
                name=node_data.name,
                description=node_data.description,
                config=node_data.config,
                position=node_data.position
            )
            workflow.add_node(node)

        # Add edges
        for edge_data in workflow_data.edges:
            edge = WorkflowEdge(
                edge_id=edge_data.edge_id,
                source_node=edge_data.source_node,
                target_node=edge_data.target_node,
                condition=edge_data.condition,
                priority=edge_data.priority
            )
            workflow.add_edge(edge)

        # Validate workflow
        if not workflow.validate():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid workflow: {workflow.validation_errors}"
            )

        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "is_valid": workflow.is_valid,
            "node_count": len(workflow.nodes),
            "edge_count": len(workflow.edges)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any] = None,
    background_tasks: BackgroundTasks = None,
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
) -> WorkflowExecutionResponse:
    """Execute a workflow."""
    try:
        # In a real implementation, you'd load the workflow from storage
        # For now, we'll create a simple example workflow
        workflow = _create_example_workflow(workflow_id)

        execution = await workflow_engine.execute_workflow(workflow, input_data or {})

        return WorkflowExecutionResponse(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            status=execution.status.value,
            started_at=execution.started_at.isoformat() if execution.started_at else None,
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            current_nodes=list(execution.current_nodes),
            completed_nodes=list(execution.completed_nodes),
            failed_nodes=list(execution.failed_nodes),
            node_results=execution.node_results
        )

    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/executions/{execution_id}")
async def get_workflow_execution(
    execution_id: str,
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
) -> Optional[WorkflowExecutionResponse]:
    """Get workflow execution status."""
    try:
        execution = workflow_engine.get_execution_status(execution_id)

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        return WorkflowExecutionResponse(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            status=execution.status.value,
            started_at=execution.started_at.isoformat() if execution.started_at else None,
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            current_nodes=list(execution.current_nodes),
            completed_nodes=list(execution.completed_nodes),
            failed_nodes=list(execution.failed_nodes),
            node_results=execution.node_results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflows/executions/{execution_id}")
async def cancel_workflow_execution(
    execution_id: str,
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Cancel a running workflow execution."""
    try:
        success = workflow_engine.cancel_execution(execution_id)

        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or already completed")

        return {"message": "Workflow execution cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/executions")
async def list_workflow_executions(
    limit: int = 50,
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
) -> List[WorkflowExecutionResponse]:
    """List workflow executions."""
    try:
        executions = workflow_engine.list_execution_history(limit)

        return [
            WorkflowExecutionResponse(
                execution_id=execution.execution_id,
                workflow_id=execution.workflow_id,
                status=execution.status.value,
                started_at=execution.started_at.isoformat() if execution.started_at else None,
                completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
                current_nodes=list(execution.current_nodes),
                completed_nodes=list(execution.completed_nodes),
                failed_nodes=list(execution.failed_nodes),
                node_results=execution.node_results
            )
            for execution in executions
        ]

    except Exception as e:
        logger.error(f"Failed to list workflow executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/stats")
async def get_workflow_stats(
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine)
) -> Dict[str, Any]:
    """Get workflow execution statistics."""
    try:
        return workflow_engine.get_execution_stats()

    except Exception as e:
        logger.error(f"Failed to get workflow stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# NLP Processor Endpoints
@router.post("/nlp/process")
async def process_text(
    request: NLPProcessingRequest,
    nlp_processor: AdvancedNLPProcessor = Depends(get_nlp_processor)
) -> NLPProcessingResponse:
    """Process text with advanced NLP analysis."""
    try:
        # Get conversation context if provided
        context = None
        if request.conversation_id:
            context = await nlp_processor.manage_conversation_context(
                request.conversation_id
            )

        # Process text
        result = await nlp_processor.process_text(
            request.text,
            context,
            request.language
        )

        # Convert intent to response format
        intent_response = None
        if result.get('intent') and isinstance(result['intent'], Intent):
            intent = result['intent']
            intent_response = IntentResponse(
                name=intent.name,
                confidence=intent.confidence,
                entities=intent.entities,
                context=intent.context,
                metadata=intent.metadata
            )

        return NLPProcessingResponse(
            original_text=result.get('original_text', request.text),
            language=result.get('language', request.language),
            processed_at=result.get('processed_at', ''),
            tokens=result.get('tokens', []),
            entities=result.get('entities', []),
            intent=intent_response,
            sentiment=result.get('sentiment', {}),
            key_phrases=result.get('key_phrases', []),
            summary=result.get('summary', ''),
            complexity_score=result.get('complexity_score', 0.0),
            readability_score=result.get('readability_score', 0.0),
            topics=result.get('topics', []),
            semantic_matches=result.get('semantic_matches', []),
            knowledge_entities=result.get('knowledge_entities', []),
            confidence=result.get('confidence', 0.0)
        )

    except Exception as e:
        logger.error(f"Failed to process text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nlp/conversation/{conversation_id}")
async def get_conversation_context(
    conversation_id: str,
    nlp_processor: AdvancedNLPProcessor = Depends(get_nlp_processor)
) -> ConversationContextResponse:
    """Get conversation context."""
    try:
        context = await nlp_processor.manage_conversation_context(conversation_id)

        return ConversationContextResponse(
            conversation_id=context.conversation_id,
            user_id=context.user_id,
            message_count=len(context.messages),
            topics=context.topics,
            sentiment_trend=context.sentiment_trend,
            recent_intents=context.intent_history[-10:] if context.intent_history else [],
            created_at=context.created_at.isoformat(),
            last_updated=context.last_updated.isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nlp/conversation/{conversation_id}/message")
async def add_conversation_message(
    conversation_id: str,
    message: str,
    sender: str = "user",
    nlp_processor: AdvancedNLPProcessor = Depends(get_nlp_processor)
):
    """Add a message to conversation context."""
    try:
        context = await nlp_processor.manage_conversation_context(conversation_id)

        # Process the message to extract intent
        nlp_result = await nlp_processor.process_text(message, context)
        intent = nlp_result.get('intent')
        intent_name = intent.name if intent and hasattr(intent, 'name') else None

        context.add_message(message, sender, intent_name)

        return {
            "message": "Message added successfully",
            "message_count": len(context.messages),
            "extracted_intent": intent_name
        }

    except Exception as e:
        logger.error(f"Failed to add conversation message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nlp/correct-grammar")
async def correct_grammar(
    text: str,
    nlp_processor: AdvancedNLPProcessor = Depends(get_nlp_processor)
) -> Dict[str, Any]:
    """Correct grammar and spelling in text."""
    try:
        result = nlp_processor.correct_grammar(text)
        return result

    except Exception as e:
        logger.error(f"Failed to correct grammar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nlp/translate")
async def translate_text(
    text: str,
    target_language: str = "es",
    nlp_processor: AdvancedNLPProcessor = Depends(get_nlp_processor)
) -> Dict[str, Any]:
    """Translate text to another language."""
    try:
        result = nlp_processor.translate_text(text, target_language)
        return result

    except Exception as e:
        logger.error(f"Failed to translate text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nlp/stats")
async def get_nlp_stats(
    nlp_processor: AdvancedNLPProcessor = Depends(get_nlp_processor)
) -> Dict[str, Any]:
    """Get NLP processor statistics."""
    try:
        return nlp_processor.get_nlp_stats()

    except Exception as e:
        logger.error(f"Failed to get NLP stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper function to create example workflow
def _create_example_workflow(workflow_id: str) -> WorkflowDefinition:
    """Create an example workflow for demonstration."""
    from ..services.agents.workflow_builder import WorkflowNode, WorkflowEdge, WorkflowNodeType

    workflow = WorkflowDefinition(
        workflow_id=workflow_id,
        name="Example Task Processing Workflow",
        description="A simple workflow that processes tasks through multiple agents"
    )

    # Add nodes
    start_node = WorkflowNode(
        node_id="start",
        node_type=WorkflowNodeType.START,
        name="Start",
        description="Workflow entry point"
    )
    workflow.add_node(start_node)

    task_node = WorkflowNode(
        node_id="process_task",
        node_type=WorkflowNodeType.TASK,
        name="Process Task",
        description="Execute main task processing",
        config={
            "agent_type": "planning_agent",
            "task_description": "Process the input task",
            "store_result": True,
            "result_variable": "task_result"
        }
    )
    workflow.add_node(task_node)

    decision_node = WorkflowNode(
        node_id="check_result",
        node_type=WorkflowNodeType.DECISION,
        name="Check Result",
        description="Check if task processing was successful",
        config={
            "condition": "${task_result.success} == True"
        }
    )
    workflow.add_node(decision_node)

    success_node = WorkflowNode(
        node_id="success",
        node_type=WorkflowNodeType.END,
        name="Success",
        description="Task completed successfully"
    )
    workflow.add_node(success_node)

    failure_node = WorkflowNode(
        node_id="failure",
        node_type=WorkflowNodeType.END,
        name="Failure",
        description="Task processing failed"
    )
    workflow.add_node(failure_node)

    # Add edges
    workflow.add_edge(WorkflowEdge(
        edge_id="start_to_process",
        source_node="start",
        target_node="process_task"
    ))

    workflow.add_edge(WorkflowEdge(
        edge_id="process_to_check",
        source_node="process_task",
        target_node="check_result"
    ))

    workflow.add_edge(WorkflowEdge(
        edge_id="check_to_success",
        source_node="check_result",
        target_node="success",
        condition="true"
    ))

    workflow.add_edge(WorkflowEdge(
        edge_id="check_to_failure",
        source_node="check_result",
        target_node="failure",
        condition="false"
    ))

    return workflow
