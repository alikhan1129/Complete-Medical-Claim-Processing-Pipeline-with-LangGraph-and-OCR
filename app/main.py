import os
import shutil
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.utils.pdf_loader import extract_text_from_pdf
from app.graph import process_claim

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from app.models import ClaimResponse

app = FastAPI(title="Medical Claim Processing Pipeline")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Medical Claim Processing Pipeline is running"}

@app.post("/api/process", response_model=ClaimResponse)
async def process_pdf_claim(
    claim_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    FastAPI endpoint for medical claim PDF processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Create a temporary file to store the upload
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. PDF -> page-wise text extraction
        logger.info(f"Extracting text from PDF: {file.filename}")
        pages = extract_text_from_pdf(temp_file_path)
        
        if not pages:
            raise HTTPException(status_code=400, detail="The PDF is empty or could not be processed.")

        # 2. Pass into LangGraph pipeline
        logger.info(f"Processing claim ID: {claim_id} through LangGraph pipeline")
        result = await process_claim(claim_id, pages)
        
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error processing claim {claim_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
