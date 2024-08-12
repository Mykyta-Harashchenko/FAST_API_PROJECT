from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from FAST_API.src.entity.models import Contacts
from FAST_API.src.database.db import get_db
from FAST_API.src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactResponse
from FAST_API.src.services.auth import auth_service


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contacts).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact(contact_id: int, db: AsyncSession, ):
    stmt = select(Contacts).filter_by(id=contact_id)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    contact = Contacts(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    stmt = select(Contacts).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.id = body.id
        contact.name = body.name
        contact.surname = body.surname
        contact.phone = body.phone
        contact.email = body.email
        contact.birthday = body.birthday
        contact.extra = body.extra
        await db.commit()
        await db.refresh(contact)
    return contact
async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contacts).filter_by(id=contact_id)
    contacts = await db.execute(stmt)
    contact = contacts.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact

async def search_contacts(name: str = None, surname: str = None, email: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Contacts)
    if name:
        query = query.filter(Contacts.name.contains(name))
    if surname:
        query = query.filter(Contacts.surname.contains(surname))
    if email:
        query = query.filter(Contacts.email.contains(email))

    result = await db.execute(query)
    return result.scalars().all()

async def get_upcoming_birthdays(db: AsyncSession):
    today = datetime.today().date()
    end_date = today + timedelta(days=7)
    stmt = select(Contacts).filter(Contacts.birthday.between(today, end_date))
    contacts = await db.execute(stmt)
    return contacts.scalars().all()