from typing import List, Optional
from fastapi import Path, Depends, HTTPException, Query, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from src.database.db import get_db
from src.schemas import ContactModel, ContactFavoriteModel, ContactResponse
from src.repository import contacts as rep_contact
from src.services.auth import auth_service
from src.services.role import RoleAccess
from src.database.models import User, Role


router = APIRouter(prefix="/contacts", tags=["contact"])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])

@router.get("/all", response_model = List[ContactResponse], dependencies=[Depends(allowed_operation_update)], summary="Get all contacts if you are admin or moderator ")
async def get_all_contact(
        skip: int = 0,
        limit: int = Query(default=10, le=100, ge=10),
        favorite: bool = None,
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The get_all_contact function returns a list of contacts.

    :param skip: int: Skip a number of contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned to 100
    :param ge: Specify the minimum value of the limit parameter
    :param favorite: bool: Filter the contacts by favorite
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the token
    :return: A list of contacts
    """
    contacts = await rep_contact.get_all_contacts(db=db, skip=skip, limit=limit, favorite=favorite)
    return contacts

@router.get("", response_model = List[ContactResponse], dependencies=[Depends(allowed_operation_get)], summary="Get contacts only for user")
async def get_contacts(
        skip: int = 0,
        limit: int = Query(default=10, le=100, ge=10),
        favorite: bool = None,
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The get_contact function returns a list of contacts.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned to 100
    :param ge: Specify the minimum value of limit
    :param favorite: bool: Filter the contacts by favorite
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A list of contacts
    """
    contacts = await rep_contact.get_contacts(db=db, skip=skip, user=current_user, limit=limit, favorite=favorite)
    return contacts



@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    If no such contact exists, it raises an HTTP 404 error.

    :param contact_id: int: Get the contact id from the path
    :param db: Session: Get a database session from the dependency injection container
    :param current_user: User: Get the current user from the database
    :return: A contact object
    """
    contact = await rep_contact.get_contact_by_id(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.post("",   response_model=ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[
        Depends(allowed_operation_create), Depends(RateLimiter(times=2, seconds=5))

    ], description="Two attempt on 5 second")
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        It takes an email, first_name, last_name and phone as parameters.
        The function returns the newly created contact object.

    :param body: ContactModel: Pass the contact model to the function
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: A contactmodel object
    """
    contact = await rep_contact.get_contact_by_email(body.email, db, current_user)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Email is exist!"
        )
    try:
        contact = await rep_contact.create(body, db, current_user)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_404_INVALID_REQUEST, detail=f"Error: {err}"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def update_contact(
        body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as input, and returns the updated contact.
        If no contact is found with that id, it raises an HTTPException.

    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Specify the id of the contact to be updated
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: The updated contact
    """
    contact = await rep_contact.update(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.patch("/contact_id/favorite", response_model=ContactResponse, dependencies=[Depends(allowed_operation_update)])
async def favorite_update(
        body: ContactFavoriteModel,
        contact_id: int = Path(ge=1),
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.token_manager.get_current_user)
):
    """
    The favorite_update function updates the favorite status of a contact.
        The function takes in an integer representing the id of a contact, and returns that same contact with its updated favorite status.
        If no such contact exists, it will return a 404 error.

    :param body: ContactFavoriteModel: Get the contact favorite model from the request body
    :param contact_id: int: Specify the id of the contact to be updated
    :param db: Session: Get the database session
    :param current_user: User: Get the user information from the token
    :return: The updated contact
    """
    contact = await rep_contact.favorite_update(contact_id, body, db,  current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allowed_operation_get)])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The remove_contact function is used to delete a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns None if successful.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Get the database connection
    :param current_user: User: Get the user that is currently logged in
    :return: None, so it is not necessary to create a schema for the function
    """
    contact = await rep_contact.delete(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return None


@router.get("/search_by/{query}", response_model=List[ContactResponse], tags=['search'], summary="Search contacts by name, lastname, email",
            dependencies=[Depends(allowed_operation_get)])
async def search_by(query: Optional[str] = None,
                         db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.token_manager.get_current_user)):
    """
    The search_by function searches for contacts by name or email.
        It returns a list of contacts that match the search query.

    :param query: Optional[str]: Specify the query string that will be used to search for contacts
    :param db: Session: Get the database connection
    :param current_user: User: Get the user from the token
    :return: A list of contacts
    """
    contacts = await rep_contact.search_contacts(query, db, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact Not Found")

    return contacts


@router.get("/search/birthdays", response_model=List[ContactResponse], dependencies=[Depends(allowed_operation_get)])
async def search_contacts(
        days: int = Query(default=7, le=30, ge=1),
        skip: int = 0,
        limit: int = Query(default=10, le=30, ge=1),
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.token_manager.get_current_user)
):
    """
    The search_contacts function is used to search for contacts that have a birthday within the next 7 days.
    The function takes in an optional parameter of days, which defaults to 7 if not provided. The function also takes in
    optional parameters skip and limit, which are used for pagination purposes. The skip parameter specifies how many
    contacts should be skipped before returning results (defaults to 0), while the limit parameter specifies how many
    results should be returned (defaults to 10). If no contacts are found with a birthday within the specified number of
    days, then an HTTP 404 Not Found error is raised.

    :param days: int: Specify the number of days to search for
    :param le: Specify the maximum value of a parameter
    :param ge: Specify the minimum value of a parameter
    :param skip: int: Skip the first n records
    :param limit: int: Limit the number of contacts returned
    :param le: Specify the maximum value that can be passed to the parameter
    :param ge: Specify the minimum value of the parameter
    :param db: Session: Get the database session
    :param current_user: User: Get the user object from the token
    :return: A list of contacts, but the function is not called anywhere
    """
    contacts = None
    if days:
        par = {
            "days": days,
            "skip": skip,
            "limit": limit,
        }
        contacts = await rep_contact.search_birthday(par, db, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found")
    return contacts


