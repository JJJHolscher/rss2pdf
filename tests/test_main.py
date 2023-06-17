#! /usr/bin/env python3
# vim:fenc=utf-8

import unittest

from src.main import *


class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertEqual(UNITTESTS(), 0)

if __name__ == "__main__":
    unittest.main()
