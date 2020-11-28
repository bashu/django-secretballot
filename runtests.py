#!test/usr/bin/env python
import os
import sys

from django.core.management import execute_from_command_line

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"

def runtests():

    argv = [sys.argv[0], "test"]
    return execute_from_command_line(argv)


if __name__ == "__main__":
    sys.exit(runtests())
