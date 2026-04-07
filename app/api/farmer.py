from fastapi import APIRouter

router = APIRouter()


@router.get("/{phone}/profile")
async def get_farmer_profile(phone: str):
    """Farmer's own profile view."""
    # TODO: Implement
    return {"phone": phone, "status": "not_implemented"}


@router.get("/{phone}/agriscore")
async def get_farmer_agriscore(phone: str):
    """Farmer's current AgriScore and history."""
    # TODO: Implement
    return {"phone": phone, "status": "not_implemented"}


@router.get("/{phone}/challenges")
async def get_farmer_challenges(phone: str):
    """Farmer's active gamification challenges."""
    # TODO: Implement
    return {"phone": phone, "status": "not_implemented"}
