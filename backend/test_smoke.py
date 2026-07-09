# -*- coding: utf-8 -*-
import unittest
from backend.routes.auth import validate_email, validate_phone

class TestAuthValidation(unittest.TestCase):
    def test_validate_email_correct(self):
        self.assertTrue(validate_email("student@ifri.bj"))
        self.assertTrue(validate_email("mentor.test@gmail.com"))

    def test_validate_email_incorrect(self):
        self.assertFalse(validate_email("studentifri.bj"))
        self.assertFalse(validate_email("student@ifri"))

    def test_validate_phone_correct(self):
        self.assertTrue(validate_phone("12345678"))
        self.assertTrue(validate_phone("0022912345678"))

    def test_validate_phone_incorrect(self):
        self.assertFalse(validate_phone("abc"))
        self.assertFalse(validate_phone("12345")) # too short

if __name__ == '__main__':
    unittest.main()
