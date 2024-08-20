from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from FAST_API.src.entity.models import Contacts
from FAST_API.src.database.db import get_db
from FAST_API.src.schemas.contacts import (
    ContactSchema,
    ContactUpdateSchema,
    ContactResponse,
)
from FAST_API.src.services.auth import auth_service


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_contacts function retrieves a list of contacts from the database with a specified limit and offset.

    :param limit: int: Specify the maximum number of contacts to retrieve
    :param offset: int: Specify the number of contacts to skip before starting to retrieve records
    :param db: AsyncSession: Database session for executing the query
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contacts).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    """
    The get_contact function retrieves a specific contact from the database by its ID.

    :param contact_id: int: Specify the ID of the contact to retrieve
    :param db: AsyncSession: Database session for executing the query
    :return: The contact if found, otherwise None
    :doc-author: Trelent
    """
    stmt = select(Contacts).filter_by(id=contact_id)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    """
    The create_contact function adds a new contact to the database based on the provided schema.

    :param body: ContactSchema: Specify the contact details to be added
    :param db: AsyncSession: Database session for executing the query
    :return: The newly created contact
    :doc-author: Trelent
    """
    contact = Contacts(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    """
    The update_contact function updates the details of an existing contact in the database.

    :param contact_id: int: Specify the ID of the contact to update
    :param body: ContactUpdateSchema: Specify the updated contact details
    :param db: AsyncSession: Database session for executing the query
    :return: The updated contact if it exists, otherwise None
    :doc-author: Trelent
    """
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
    """
    The delete_contact function removes a specific contact from the database by its ID.

    :param contact_id: int: Specify the ID of the contact to delete
    :param db: AsyncSession: Database session for executing the query
    :return: The deleted contact if it exists, otherwise None
    :doc-author: Trelent
    """
    stmt = select(Contacts).filter_by(id=contact_id)
    contacts = await db.execute(stmt)
    contact = contacts.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(
    name: str = None,
    surname: str = None,
    email: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    The search_contacts function searches for contacts in the database based on optional name, surname, or email criteria.

    :param name: str: Filter contacts by name (optional)
    :param surname: str: Filter contacts by surname (optional)
    :param email: str: Filter contacts by email (optional)
    :param db: AsyncSession: Database session for executing the query
    :return: A list of contacts matching the search criteria
    :doc-author: Trelent
    """
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
    """
    The get_upcoming_birthdays function retrieves a list of contacts who have birthdays within the next 7 days.

    :param db: AsyncSession: Database session for executing the query
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    today = datetime.today().date()
    end_date = today + timedelta(days=7)
    stmt = select(Contacts).filter(Contacts.birthday.between(today, end_date))
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
