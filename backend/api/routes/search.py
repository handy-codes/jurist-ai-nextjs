from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def search():
    return {"message": "Search endpoint"}

