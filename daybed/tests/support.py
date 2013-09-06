try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from uuid import uuid4
import webtest

from daybed.backends.couchdb.database import Database
from daybed.backends.exceptions import PolicyAlreadyExist


class BaseWebTest(unittest.TestCase):
    """Base Web Test to test your cornice service.

    It setups the database before each test and delete it after.
    """

    def setUp(self):
        self.app = webtest.TestApp("config:tests.ini", relative_to='.')
        self.backend = self.app.app.registry.backend
        self.db = Database(self.backend.db, lambda: str(uuid4()))

        try:
            self.db.set_policy('admin-only', {
                'group:admins': 0xFFFF,
                'authors:': 0x0F00,
                'others:': 0x4000})
        except PolicyAlreadyExist:
            pass

        self.db.add_user({'name': 'admin', 'groups': ['admins']})

    def tearDown(self):
        self.backend.delete_db()

    def put_valid_definition(self):
        """Create a valid definition named "todo".
        """
        # Put a valid definition
        self.app.put_json('/definitions/todo',
                          self.valid_definition,
                          headers=self.headers)
