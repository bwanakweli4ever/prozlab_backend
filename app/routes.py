from fastapi import APIRouter

from app.config.settings import settings
from app.modules.auth.routes import router as auth_router
from app.modules.proz.routes import router as proz_router
from app.modules.proz.controllers.admin_controller import router as admin_router


api_router = APIRouter()

# Include all module routers here
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(proz_router, prefix="/proz")
api_router.include_router(admin_router, prefix="/admin/proz", tags=["Admin - Profile Verification"])