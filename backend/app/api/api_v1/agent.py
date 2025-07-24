from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.agent import Agent
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentUpdate
)
from app.api.api_v1.auth import get_current_user
from app.services.agent_service import generate_agent_response
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Define schemas within the file for clarity
class AgentCreate(BaseModel):
    name: str
    level: str
    position: str
    model: str
    projects: List[str] | None = None

class AgentResponse(AgentCreate):
    id: int
    user_id: int
    created_at: str

    class Config:
        orm_mode = True

class AgentUpdate(BaseModel):
    name: str | None = None
    level: str | None = None
    position: str | None = None
    model: str | None = None
    projects: List[str] | None = None

@router.post("/", response_model=AgentResponse)
def create_agent(
    *,
    db: Session = Depends(get_db),
    agent_in: AgentCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify if the model exists or is valid
    allowed_models = ["gpt-3.5-turbo", "gpt-4", "llama-3", "custom-model"]
    if agent_in.model not in allowed_models:
        raise HTTPException(
            status_code=400,
            detail="Invalid model specified"
        )
    
    # Verify position is valid
    allowed_positions = ["dev", "tester"]
    if agent_in.position not in allowed_positions:
        raise HTTPException(
            status_code=400,
            detail="Invalid position. Must be 'dev' or 'tester'"
        )

    # Create new agent
    agent = Agent(
        name=agent_in.name,
        level=agent_in.level,
        position=agent_in.position,
        model=agent_in.model,
        projects=agent_in.projects,
        user_id=current_user.id,
        created_at=datetime.now().isoformat()
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@router.get("/", response_model=List[AgentResponse])
def get_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    agents = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.user_id == current_user.id
        )
        .first()
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/{agent_id}/interact")
async def interact_with_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    request: dict,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.user_id == current_user.id
        )
        .first()
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get the last user input
    last_input = request["input"]
    if not isinstance(last_input, str):
        raise HTTPException(status_code=400, detail="Input must be a string")

    async def response_stream():
        async for chunk in generate_agent_response(
            query=last_input,
            agent_id=agent_id,
            model=agent.model,
            position=agent.position,
            level=agent.level,
            projects=agent.projects,
            db=db
        ):
            yield chunk

    return StreamingResponse(
        response_stream(),
        media_type="text/event-stream",
        headers={
            "x-vercel-ai-data-stream": "v1"
        }
    )

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    agent_in: AgentUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.user_id == current_user.id
        )
        .first()
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Verify model and position if provided
    if agent_in.model and agent_in.model not in ["gpt-3.5-turbo", "gpt-4", "llama-3", "custom-model"]:
        raise HTTPException(status_code=400, detail="Invalid model specified")
    
    if agent_in.position and agent_in.position not in ["dev", "tester"]:
        raise HTTPException(status_code=400, detail="Invalid position. Must be 'dev' or 'tester'")

    # Update fields if provided
    if agent_in.name is not None:
        agent.name = agent_in.name
    if agent_in.level is not None:
        agent.level = agent_in.level
    if agent_in.position is not None:
        agent.position = agent_in.position
    if agent_in.model is not None:
        agent.model = agent_in.model
    if agent_in.projects is not None:
        agent.projects = agent_in.projects

    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/{agent_id}")
def delete_agent(
    *,
    db: Session = Depends(get_db),
    agent_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.user_id == current_user.id
        )
        .first()
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    return {"status": "success"}