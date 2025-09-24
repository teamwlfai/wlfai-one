from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.role import RoleCreate, RoleUpdate
from app.services.roles import service as role_service
from app.core.database import get_db
from utils.response_wrapper import standard_response

router = APIRouter(prefix="/roles", tags=["roles"])
CURRENT_USER_ID = 1  # Replace with auth later


@router.post("/")
@standard_response("Role created successfully")
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new role. Duplicate roles will automatically raise HTTPException in the service.
    """
    return await role_service.create_role(db, role, user_id=CURRENT_USER_ID)


@router.get("/")
@standard_response("Roles fetched successfully")
async def read_roles(db: AsyncSession = Depends(get_db)):
    return await role_service.get_roles(db)


@router.get("/{role_id}")
@standard_response("Role fetched successfully")
async def read_role(role_id: int, db: AsyncSession = Depends(get_db)):
    role = await role_service.get_role(db, role_id)
    return role  # None will be handled globally


@router.put("/{role_id}")
@standard_response("Role updated successfully")
async def update_role(
    role_id: int, role: RoleUpdate, db: AsyncSession = Depends(get_db)
):
    updated_role = await role_service.update_role(
        db, role_id, role, user_id=CURRENT_USER_ID
    )
    return updated_role  # None will be handled globally


@router.patch("/{role_id}/status")
@standard_response("Role status updated successfully")
async def update_role_status(role_id: int, db: AsyncSession = Depends(get_db)):
    updated_role = await role_service.update_role_status(
        db, role_id, user_id=CURRENT_USER_ID
    )
    return updated_role  # None will be handled globally
