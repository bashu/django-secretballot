from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='django-secretballot',
    version="2.0.0-dev2",
    packages=find_packages(),
    include_package_data=True,
    description='Django anonymous voting application',
    author='James Turk',
    author_email='dev@jamesturk.net',
    license='BSD License',
    url='https://github.com/jamesturk/django-secretballot/',
    long_description=long_description,
    platforms=["any"],
    install_requires=[
        "django",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
