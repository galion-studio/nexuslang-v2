"""
NexusLang execution API routes.
Handles code execution, compilation, and analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

from ..services.nexuslang_executor import get_executor

router = APIRouter()

class CodeRequest(BaseModel):
    code: str
    compile_to_binary: bool = False

class CodeResponse(BaseModel):
    output: str
    execution_time: float
    success: bool
    error: Optional[str] = None

@router.post("/run", response_model=CodeResponse)
async def run_code(request: CodeRequest):
    """Execute NexusLang code and return output."""
    executor = get_executor()
    result = await executor.execute(request.code, request.compile_to_binary)
    return result

@router.post("/compile")
async def compile_code(request: CodeRequest):
    """Compile NexusLang code to binary format."""
    executor = get_executor()
    result = await executor.execute(request.code, compile_to_binary=True)
    
    if result["success"]:
        return {
            "success": True,
            "binary_size": result.get("binary_size", 0),
            "compression_ratio": len(request.code) / result.get("binary_size", 1)
        }
    else:
        return {
            "success": False,
            "error": result.get("error")
        }

@router.post("/analyze")
async def analyze_code(request: CodeRequest):
    """Analyze NexusLang code for errors and suggestions."""
    executor = get_executor()
    analysis = await executor.analyze(request.code)
    return analysis

@router.get("/examples")
async def get_examples():
    """Get list of example NexusLang programs."""
    examples_dir = Path(__file__).parent.parent.parent / "nexuslang" / "examples"
    
    if not examples_dir.exists():
        return {"examples": []}
    
    examples = []
    for file in examples_dir.glob("*.nx"):
        with open(file, 'r') as f:
            content = f.read()
        
        examples.append({
            "name": file.stem,
            "filename": file.name,
            "code": content,
            "description": content.split('\n')[0].replace('//', '').strip() if content else ""
        })
    
    return {"examples": examples}

