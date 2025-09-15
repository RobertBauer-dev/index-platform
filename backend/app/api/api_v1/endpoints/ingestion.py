"""
Data ingestion API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import pandas as pd
import io

from app.core.database import get_db
from app.db import models
from app.api.api_v1.deps import get_current_user
from app.ingestion.csv_ingestor import CSVIngestor
from app.ingestion.api_ingestor import APIIngestor

router = APIRouter()


@router.post("/csv/securities")
async def ingest_securities_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Ingest securities from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create temporary file path for CSVIngestor
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(csv_content)
            tmp_file_path = tmp_file.name
        
        # Ingest data
        csv_ingestor = CSVIngestor(db, tmp_file_path)
        result = csv_ingestor.ingest_securities_from_csv()
        
        # Clean up temporary file
        import os
        os.unlink(tmp_file_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@router.post("/csv/prices")
async def ingest_prices_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Ingest price data from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create temporary file path for CSVIngestor
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(csv_content)
            tmp_file_path = tmp_file.name
        
        # Ingest data
        csv_ingestor = CSVIngestor(db, tmp_file_path)
        result = csv_ingestor.ingest_prices_from_csv()
        
        # Clean up temporary file
        import os
        os.unlink(tmp_file_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@router.post("/api/alpha-vantage")
async def ingest_from_alpha_vantage(
    symbols: List[str],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Ingest data from Alpha Vantage API"""
    try:
        api_ingestor = APIIngestor(db)
        result = api_ingestor.ingest_from_alpha_vantage(symbols)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error ingesting from Alpha Vantage: {str(e)}")


@router.post("/api/yahoo-finance")
async def ingest_from_yahoo_finance(
    symbols: List[str],
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Ingest data from Yahoo Finance API"""
    try:
        api_ingestor = APIIngestor(db)
        result = api_ingestor.ingest_from_yahoo_finance(symbols, start_date, end_date)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error ingesting from Yahoo Finance: {str(e)}")


@router.post("/api/securities")
async def ingest_securities_from_api(
    symbols: List[str],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Ingest security master data from API"""
    try:
        api_ingestor = APIIngestor(db)
        result = api_ingestor.ingest_securities_from_api(symbols)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error ingesting securities: {str(e)}")


@router.get("/templates/{data_type}")
async def get_csv_template(data_type: str):
    """Get CSV template for data ingestion"""
    if data_type not in ['securities', 'prices']:
        raise HTTPException(status_code=400, detail="Invalid data type. Use 'securities' or 'prices'")
    
    csv_ingestor = CSVIngestor(None, "")  # Dummy instance for template
    template = csv_ingestor.get_csv_template(data_type)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.post("/bulk")
async def bulk_ingest(
    securities_file: Optional[UploadFile] = File(None),
    prices_files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Bulk ingest multiple files"""
    results = {}
    
    try:
        # Process securities file
        if securities_file:
            if not securities_file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Securities file must be a CSV")
            
            content = await securities_file.read()
            csv_content = content.decode('utf-8')
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write(csv_content)
                tmp_file_path = tmp_file.name
            
            csv_ingestor = CSVIngestor(db, tmp_file_path)
            results['securities'] = csv_ingestor.ingest_securities_from_csv()
            
            import os
            os.unlink(tmp_file_path)
        
        # Process prices files
        results['prices'] = {}
        for prices_file in prices_files:
            if not prices_file.filename.endswith('.csv'):
                results['prices'][prices_file.filename] = {"error": "File must be a CSV"}
                continue
            
            try:
                content = await prices_file.read()
                csv_content = content.decode('utf-8')
                
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                    tmp_file.write(csv_content)
                    tmp_file_path = tmp_file.name
                
                csv_ingestor = CSVIngestor(db, tmp_file_path)
                results['prices'][prices_file.filename] = csv_ingestor.ingest_prices_from_csv()
                
                import os
                os.unlink(tmp_file_path)
                
            except Exception as e:
                results['prices'][prices_file.filename] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in bulk ingestion: {str(e)}")


@router.get("/status/{job_id}")
async def get_ingestion_status(job_id: str):
    """Get status of an ingestion job"""
    # This would integrate with a job queue system like Celery
    # For now, return a placeholder
    return {
        "job_id": job_id,
        "status": "completed",
        "message": "Job status tracking not yet implemented"
    }
