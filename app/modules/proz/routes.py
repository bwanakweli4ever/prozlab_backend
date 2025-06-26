# app/modules/proz/routes.py
from fastapi import APIRouter

# Import controllers
from app.modules.proz.controllers.public_controller import router as public_router
from app.modules.proz.controllers.media_controller import router as media_router
from app.modules.proz.controllers.proz_controller import router as proz_router
from app.modules.proz.controllers.file_access_controller import router as file_access_router


# Create the main router for the proz module
router = APIRouter()

# Include public routes (no authentication required)
router.include_router(public_router, prefix="/public", tags=["public-profiles"])

# Include media/file upload routes (authentication required)
router.include_router(media_router, prefix="/media", tags=["profile-media"])

router.include_router(proz_router, prefix="/proz", tags=["proz-profiles"])

router.include_router(file_access_router, prefix="/files", tags=["file-access"]) 