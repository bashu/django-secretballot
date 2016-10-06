from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='django-secretballot',
    version="0.6.0",
    packages=find_packages(),
    include_package_data=True,
    description='Django anonymous voting application',
    author='James Turk',
    author_email='james.p.turk@gmail.com',
    license='BSD License',
    url='http://github.com/jamesturk/django-secretballot/',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
