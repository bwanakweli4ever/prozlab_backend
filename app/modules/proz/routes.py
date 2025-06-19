# app/modules/proz/routes.py
from fastapi import APIRouter

# Import controllers
from app.modules.proz.controllers.public_controller import router as public_router
from app.modules.proz.controllers.media_controller import router as media_router

# Create the main router for the proz module
router = APIRouter()

# Include public routes (no authentication required)
router.include_router(public_router, prefix="/public", tags=["public-profiles"])

# Include media/file upload routes (authentication required)
router.include_router(media_router, prefix="/media", tags=["profile-media"])