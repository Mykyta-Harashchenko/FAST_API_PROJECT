from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from FAST_API.src.database.db import get_db
from FAST_API.src.repository import contacts as repositories_contacts
from FAST_API.src.schemas.contacts import (
    ContactSchema,
    ContactUpdateSchema,
    ContactResponse,
)
from FAST_API.src.services.auth import auth_service
from FAST_API.src.entity.models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/upcoming-birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_upcoming_birthdays function retrieves a list of contacts who have birthdays within the upcoming week.

    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_upcoming_birthdays(db)
    return contacts


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(
    name: str = Query(None),
    surname: str = Query(None),
    email: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The search_contacts function searches for contacts based on the provided name, surname, or email.

    :param name: str: Filter contacts by name
    :param surname: str: Filter contacts by surname
    :param email: str: Filter contacts by email
    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: A list of contacts that match the search criteria
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.search_contacts(name, surname, email, db)
    return contacts


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contacts function retrieves a list of contacts with pagination support.

    :param limit: int: The maximum number of contacts to return (default is 10, minimum is 10, maximum is 500)
    :param offset: int: The number of contacts to skip before starting to collect the result set (default is 0)
    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: A paginated list of contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db)
    return contacts


@router.get("/{contacts_id}", response_model=ContactResponse)
async def get_contact(
    contacts_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contact function retrieves a specific contact by their ID.

    :param contacts_id: int: The ID of the contact to retrieve
    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: The contact with the specified ID
    :raise HTTPException: If the contact is not found (404 Not Found)
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact(contacts_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The create_contact function creates a new contact with the provided details.

    :param body: ContactSchema: The contact details for the new contact
    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: The newly created contact
    :doc-author: Trelent
    """
    contact = await repositories_contacts.create_contact(body, db)
    return contact


@router.put("/{contacts_id}")
async def update_contact(
    body: ContactUpdateSchema,
    contacts_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates an existing contact with the provided details.

    :param body: ContactUpdateSchema: The updated contact details
    :param contacts_id: int: The ID of the contact to update
    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: The updated contact
    :raise HTTPException: If the contact is not found (404 Not Found)
    :doc-author: Trelent
    """
    contact = await repositories_contacts.update_contact(contacts_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contacts_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contacts_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The delete_contact function deletes a specific contact by their ID.

    :param contacts_id: int: The ID of the contact to delete
    :param db: AsyncSession: Database session for executing queries
    :param current_user: User: The currently authenticated user
    :return: None (204 No Content)
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contacts_id, db)
    return contact
