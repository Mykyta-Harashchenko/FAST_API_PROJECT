from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from FAST_API.src.database.db import get_db
from FAST_API.src.repository import contacts as repositories_contacts
from FAST_API.src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])



@router.get('/upcoming-birthdays', response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_upcoming_birthdays(db)
    return contacts


@router.get('/search', response_model=list[ContactResponse])
async def search_contacts(name: str = Query(None), surname: str = Query(None), email: str = Query(None), db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.search_contacts(name, surname, email, db)
    return contacts


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db)
    return contacts

@router.get('/{contacts_id}', response_model=ContactResponse)
async def get_contact(contacts_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.get_contact(contacts_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.create_contact(body, db)
    return contact


@router.put('/{contacts_id}')
async def update_contact(body: ContactUpdateSchema, contacts_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.update_contact(contacts_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete('/{contacts_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contacts_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.delete_contact(contacts_id, db)
    return contact

