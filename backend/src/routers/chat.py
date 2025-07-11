from fastapi import APIRouter, Query, HTTPException
from services.llama_client import ask_llama

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("")
def chat(question: str = Query(..., description="Ask me anything")):
    try:
        answer = ask_llama(question)
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
