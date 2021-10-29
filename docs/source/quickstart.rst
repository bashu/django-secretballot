Quickstart
==========

Install ``django-secretballot``:

.. code-block:: bash

    pip install django-secretballot

Add ``secretballot`` to your ``INSTALLED_APPS``:

.. code-block:: python

    # settings.py
    INSTALLED_APPS += [
        "secretballot"
    ]

Activate ``SecretBallotIpMiddleware`` or ``SecretBallotIpUseragentMiddleware`` middleware class (see :ref:`tokens_and_secretballotmiddleware`):

.. code-block:: python

    MIDDLEWARE = [
        ...
        "secretballot.middleware.SecretBallotIpMiddleware",
        # or
        "secretballot.middleware.SecretBallotIpUseragentMiddleware",
    ]

Be sure you have ``django.template.context_processors.request`` processor listed in ``TEMPLATES["OPTIONS"]["context_processors"]`` setting:

.. code-block:: python

    TEMPLATES = [
        {
            ...
            "OPTIONS": {
                "context_processors": [
                    ...
                    "django.template.context_processors.request",
                ],
            },
        },
    ]

In order to attach the voting helpers to a particular model, it is enough to list them in ``SECRETBALLOT_FOR_MODELS`` setting and you're almost done.

.. code-block::  python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {},
    }


Run ``./manage.py migrate``. This creates the tables in your database that are necessary for operation.

Please see `example`_ application on Github. This application is used to manually test the functionalities of this package. This also serves as a good example.

.. _example: https://github.com/bashu/django-secretballot/tree/develop/example
