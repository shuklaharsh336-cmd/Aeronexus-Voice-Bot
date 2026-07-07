from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any, List
from ..models import CallRequest, CallResponse, ErrorResponse
from ..services.vonage_service import VonageService
from ..logger import setup_logger
from fastapi import UploadFile, File

logger = setup_logger(__name__)
router = APIRouter()

def get_vonage_service() -> VonageService:
    return VonageService()

@router.get("/health", response_model=Dict[str, str])
async def health_check():
    return {"status": "ok"}

@router.post("/call", response_model=CallResponse, responses={500: {"model": ErrorResponse}})
async def make_call(request: CallRequest, vonage_service: VonageService = Depends(get_vonage_service)):
    try:
        data = await vonage_service.create_outbound_call(request.to_number)
        return CallResponse(message="Call initiated successfully", call_id=data.get("uuid", ""))
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/answer")
async def answer_webhook(request: Request):
    """
    Webhook called by Vonage when the outbound call is answered.
    Returns an NCCO (Call Control Object) with a Talk action.
    """
    params = dict(request.query_params)
    logger.info(f"Answer webhook received. Params: {params}")
    
    ncco = [
        {
            "action": "talk",
            "text": "Hello, this is the Phase 1 AI Voice Calling Agent testing your connection. Goodbye."
        }
    ]
    return ncco

@router.post("/webhooks/events")
async def events_webhook(request: Request):
    """
    Webhook called by Vonage for call status events.
    """
    try:
        data = await request.json()
        logger.info(f"Event webhook received: {data.get('status')} for call {data.get('uuid')}")
        logger.debug(f"Full event payload: {data}")
    except Exception as e:
        logger.error(f"Error parsing event webhook: {str(e)}")

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    print(f"--- File received: {file.filename} ---")
    return {"message": "CSV uploaded successfully", "filename": file.filename}
    
    return {"status": "ok"}
