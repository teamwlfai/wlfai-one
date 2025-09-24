from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from app.models.role import roles
from app.schemas.role import RoleCreate, RoleUpdate
from sqlalchemy.exc import IntegrityError

# Define which columns you want to return
ROLE_COLUMNS = [
    roles.c.id,
    roles.c.name,
    roles.c.description,
    roles.c.created_at,
    roles.c.is_active,
]
# Exclude: created_by, updated_by, updated_at (sensitive/internal fields)


# Create
async def create_role(db: AsyncSession, role: RoleCreate, user_id: int):
    # Check if role already exists
    stmt = select(roles).where(roles.c.name == role.name)
    result = await db.execute(stmt)
    existing_role = result.first()

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role.name}' already exists",
        )

    # Insert new role
    stmt = (
        insert(roles)
        .values(name=role.name, description=role.description, created_by=user_id)
        .returning(*ROLE_COLUMNS)  # ✅ return all columns
    )

    try:
        result = await db.execute(stmt)
        await db.commit()
        new_role = result.first()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Database integrity error"
        )

    return dict(new_role._mapping)  # ✅ convert Row to dict


# Get all
async def get_roles(db: AsyncSession):
    result = await db.execute(select(*ROLE_COLUMNS))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]  # ✅ convert each row to dict


# Get by ID
async def get_role(db: AsyncSession, role_id: int):
    result = await db.execute(select(*ROLE_COLUMNS).where(roles.c.id == role_id))
    row = result.fetchone()
    if row:
        return dict(row._mapping)  # ✅ convert to dict
    return None


# Update
async def update_role(db: AsyncSession, role_id: int, role: RoleUpdate, user_id: int):
    stmt = (
        update(roles)
        .where(roles.c.id == role_id)
        .values(**role.model_dump(exclude_unset=True), updated_by=user_id)
        .returning(*ROLE_COLUMNS)  # ✅ return all columns
    )

    result = await db.execute(stmt)
    await db.commit()
    updated_row = result.first()
    if updated_row:
        return dict(updated_row._mapping)
    return None


# Soft delete / toggle active
async def update_role_status(db: AsyncSession, role_id: int, user_id: int):
    stmt = (
        update(roles)
        .where(roles.c.id == role_id)
        .values(is_active=~roles.c.is_active, updated_by=user_id)
        .returning(*ROLE_COLUMNS)  # ✅ return all columns
    )
    result = await db.execute(stmt)
    await db.commit()
    updated_row = result.first()
    if updated_row:
        return dict(updated_row._mapping)
    return None
