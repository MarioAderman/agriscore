from fastapi import APIRouter, Depends

from app.dependencies import verify_bank_api_key

router = APIRouter(dependencies=[Depends(verify_bank_api_key)])


@router.get("/farmers")
async def list_farmers():
    """List all farmers with AgriScore."""
    # TODO: Implement
    return {"farmers": [], "status": "not_implemented"}


@router.get("/farmers/{farmer_id}")
async def get_farmer_detail(farmer_id: str):
    """Full farmer profile with sub-scores."""
    # TODO: Implement
    return {"farmer_id": farmer_id, "status": "not_implemented"}


@router.get("/farmers/{farmer_id}/expediente")
async def get_farmer_expediente(farmer_id: str):
    """Full report with satellite data, documents, challenges."""
    # TODO: Implement
    return {"farmer_id": farmer_id, "status": "not_implemented"}


@router.get("/stats")
async def get_stats():
    """Aggregate statistics for bank dashboard."""
    # TODO: Implement
    return {"total_farmers": 0, "avg_score": 0, "status": "not_implemented"}
