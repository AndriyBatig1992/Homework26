from sqlalchemy.orm import Session
from src.schemas import ContactModel
from src.database.models import Contact,User
from typing import Union
from datetime import datetime
from sqlalchemy import func


async def get_contacts(db: Session, skip: int, limit: int, user: User, favorite: Union[bool, None]=None):
    """
    The get_contacts function returns a list of contacts for the user.


    :param db: Session: Access the database
    :param skip: int: Skip a number of contacts
    :param limit: int: Limit the number of contacts returned
    :param user: User: Filter the contacts by user
    :param favorite: Union[bool: Filter the contacts by favorite
    :param None: Specify that the favorite parameter is optional
    :return: A list of contacts
    """
    query = db.query(Contact).filter_by(user=user)
    if favorite is not None:
        query = query.filter_by(favorite=favorite)
    contact = query.offset(skip).limit(limit).all()
    return contact


async def get_all_contacts(db: Session, skip: int, limit: int, favorite: Union[bool, None]=None):
    """
    The get_all_contacts function returns a list of contacts from the database.


    :param db: Session: Pass the database session to the function
    :param skip: int: Skip a number of records in the database
    :param limit: int: Limit the number of results returned
    :param favorite: Union[bool: Filter the contacts by favorite
    :param None: Specify that the favorite parameter is optional
    :return: A list of contact objects
    """
    query = db.query(Contact)
    if favorite is not None:
        query = query.filter_by(favorite=favorite)
    contact = query.offset(skip).limit(limit).all()
    return contact


async def get_contact_by_id(contact_id: int, db: Session, user: User):
    """
    The get_contact_by_id function takes in a contact_id and returns the corresponding Contact object.
        Args:
            contact_id (int): The id of the Contact to be retrieved.
            db (Session): A database session for querying Contacts from the database.
            user (User): The User who owns this Contact.

    :param contact_id: int: Get the contact by id
    :param db: Session: Pass the database session to the function
    :param user: User: Check that the user who is making the request
    :return: A contact object
    """
    contact = db.query(Contact).filter_by(id=contact_id, user=user).first()
    return contact


async def get_contact_by_email(email: str, db: Session, user: User):
    """
    The get_contact_by_email function takes in an email and a database session,
    and returns the contact associated with that email. If no such contact exists,
    it returns None.

    :param email: str: Filter the database by email
    :param db: Session: Pass the database session to the function
    :param user: User: Filter the results so that only contacts belonging to a specific user are returned
    :return: A contact object
    """
    contact = db.query(Contact).filter_by(email=email, user=user).first()
    return contact


async def create(body: ContactModel, db: Session, user: User):
    """
    The create function creates a new contact in the database.


    :param body: ContactModel: Pass the data from the request body to create a new contact
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user id from the token
    :return: A contact object
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        comments=body.comments,
        favorite=body.favorite,
        user=user
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body:ContactModel, db: Session, user: User):
    """
    The update function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactModel): The updated information for the specified contact.

    :param contact_id: int: Determine which contact is being updated
    :param body:ContactModel: Pass in the contact information that will be used to update the existing contact
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user's id from the token
    :return: The contact object
    """
    contact = await get_contact_by_id(contact_id, db, user=user)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.comments = body.comments
        contact.favorite = body.favorite
        db.commit()
    return contact


async def favorite_update(contact_id: int, body: ContactModel, db: Session, user: User):
    """
    The favorite_update function updates the favorite field of a contact.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactModel): The updated ContactModel object with new favorite value.
            db (Session): A database session for making queries and commits to the database.

    :param contact_id: int: Identify the contact to update
    :param body: ContactModel: Pass the contact information to the function
    :param db: Session: Access the database
    :param user: User: Get the user_id from the token
    :return: The updated contact
    """
    contact = await get_contact_by_id(contact_id, db, user=user)
    if contact:
        contact.favorite = body.favorite
        db.commit()
    return contact


async def delete(contact_id, db: Session, user: User):
    """
    The delete function deletes a contact from the database.


    :param contact_id: Find the contact to be deleted
    :param db: Session: Pass the database session to the function
    :param user: User: Check if the user is logged in
    :return: The contact that was deleted
    """
    contact = await get_contact_by_id(contact_id, db, user=user)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(query: str, db: Session, user: User):
    """
    The search_contacts function searches the database for contacts that match a given query.

    :param query: str: Search the database for contacts that match the query
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user id of the logged in user
    :return: A list of contacts that match the query
    """
    contacts = db.query(Contact).filter(
        (Contact.user == user) & (
            func.lower(Contact.first_name).contains(func.lower(query)) |
            func.lower(Contact.last_name).contains(func.lower(query)) |
            func.lower(Contact.email).contains(func.lower(query))
        )
    ).all()
    return contacts


async def search_birthday(par: dict, db: Session, user: User):
    """
    The search_birthday function searches for contacts with birthdays within a certain number of days.
        The function takes in the following parameters:
            par: A dictionary containing the search parameters, including &quot;days&quot; and &quot;skip&quot;.
            db: A database session object.
            user: The current user's User object.

    :param par:dict: Pass the parameters from the api call to
    :param db: Session: Connect to the database
    :param user: User: Get the user's contacts from the database
    :return: A list of contacts whose birthday is in the next 7 days
    """
    days_param = par.get("days", 7)
    days = int(days_param)
    days += 1
    now = datetime.now().date()
    birthdays_contacts = []
    query = db.query(Contact).filter_by(user=user)
    contacts = query.offset(par.get("skip")).limit(par.get("limit"))

    for contact in contacts:
        birthday = contact.birthday
        if birthday:
            birthday_this_year = birthday.replace(year=now.year)
            days_until_birthday = (birthday_this_year - now).days
            if days_until_birthday in range(days):
                birthdays_contacts.append(contact)
    return birthdays_contacts



