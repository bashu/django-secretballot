#!/usr/bin/env python

import codecs
import os
import re

from setuptools import find_packages, setup


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding="utf-8").read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-secretballot",
    version=find_version("secretballot", "__init__.py"),
    license="BSD License",
    install_requires=[
        "django",
    ],
    description="Django anonymous voting application",
    long_description=read("README.rst") + "\n\n" + read("CHANGES.rst"),
    author="James Turk",
    author_email="dev@jamesturk.net",
    maintainer="Basil Shubin",
    maintainer_email="basil.shubin@gmail.com",
    url="https://github.com/bashu/django-secretballot/",
    download_url="https://github.com/bashu/django-maintenancemode/zipball/master",
    packages=find_packages(exclude=("example*", "*.tests*")),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
