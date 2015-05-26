from setuptools import setup

long_description = open('README.rst').read()

setup(
    name='django-secretballot',
    version="0.4.0",
    package_dir={'secretballot': 'secretballot'},
    packages=['secretballot'],
    description='Django anonymous voting application',
    author='James Turk',
    author_email='jturk@sunlightfoundation.com',
    license='BSD License',
    url='http://github.com/sunlightlabs/django-secretballot/',
    long_description=long_description,
    platforms=["any"],
    install_requires=[
        "django",
        "south",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
