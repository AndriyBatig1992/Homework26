import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.repository.contacts import get_contacts, get_all_contacts, get_contact_by_id, get_contact_by_email, create, update,\
    delete, search_contacts, search_birthday, favorite_update
from datetime import date

class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="some@email.ua")
        self.contact = Contact(
            id=1,
            first_name='ContactName',
            last_name='ContactSurname',
            email='test@test.com',
            phone='1234567890',
            birthday='2000-10-10',
            comments='some info',
            favorite=False,
            created_at='2023-01-05',
            updated_at='2023-01-05',
            user_id=self.user.id
        )

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        favorite = True
        q = self.session.query().filter_by()
        if favorite is not None:
            q = q.filter_by()
        q.offset().limit().all.return_value = contacts
        result = await get_contacts(db=self.session, skip=0, limit=10, user=self.user, favorite=favorite)
        self.assertEqual(result, contacts)

    async def test_get_all_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        favorite = True
        q = self.session.query().filter_by()
        q.offset.return_value.limit.return_value.all.return_value = contacts
        result = await get_all_contacts(db=self.session, skip=0, limit=10, favorite=favorite)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_by_email(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_email(email="as@ee.ua", user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)


    async def test_get_contact_by_email_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_email(email="as@ee.ua", user=self.user, db=self.session)
        self.assertIsNone(result)


    async def test_create_contact(self):
        body = self.contact
        result = await create(body=body, db=self.session, user=self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.user.id, self.user.id)


    async def test_delete_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await delete(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, contact)


    async def test_delete_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await delete(contact_id=1, db=self.session, user=self.user)
        self.assertIsNone(result)


    async def test_update_contact(self):
        contact = Contact()
        body = self.contact
        self.session.query().filter_by().first.return_value = contact
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, db=self.session, user=self.user)
        self.assertEqual(result, contact)


    async def test_update_not_found(self):
        body = self.contact
        self.session.query().filter_by().first.return_value = None
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, db=self.session, user=self.user)
        self.assertIsNone(result)


    async def test_update_favorite_contact(self):
        contact = Contact()
        body = self.contact
        body.favorite = True
        self.session.query().filter_by().first.return_value = contact
        result = await favorite_update(contact_id =1, body=body, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_update_favorite_contact_not_found(self):
        body = self.contact
        body.favorite = True
        self.session.query().filter_by().first.return_value = None
        result = await favorite_update(contact_id=1, body=body, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_get_contact_search_birthday(self):
        par = {"query": "ContactName", "db": self.session, "user": self.user}
        self.session.query.return_value.filter.return_value.all.return_value = [self.contact]
        result = await search_contacts(**par)
        self.assertIn(self.contact, result)


    async def test_get_birthdays(self):
        par = {"days": 7, "skip": 0, "limit": 10}
        contacts = [Contact(birthday=date(year=1990, month=12, day=21)), Contact()]
        self.session.query.return_value.filter_by.return_value.offset.return_value.limit.return_value = contacts
        result = await search_birthday(par=par, db=self.session, user=self.user)
        self.assertEqual(contacts[0].birthday, result[0].birthday)


if __name__ == "__main__":
    unittest.main()