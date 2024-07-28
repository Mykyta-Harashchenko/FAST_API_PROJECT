from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from FAST_API.src.entity.models import Contacts
from FAST_API.src.database.db import get_db
from FAST_API.src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactResponse


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contacts).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contacts).filter_by(id=contact_id)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    contact = Contacts(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

async def update_contact():
    pass


async def delete_contact():
    pass