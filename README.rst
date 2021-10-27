django-secretballot
===================

.. image:: https://img.shields.io/pypi/v/django-secretballot.svg
    :target: https://pypi.python.org/pypi/django-secretballot/

.. image:: https://img.shields.io/pypi/dm/django-secretballot.svg
    :target: https://pypi.python.org/pypi/django-secretballot/

.. image:: https://img.shields.io/github/license/bashu/django-secretballot.svg
    :target: https://pypi.python.org/pypi/django-secretballot/

.. image:: https://img.shields.io/travis/bashu/django-secretballot.svg
    :target: https://travis-ci.com/github/bashu/django-secretballot/

Django voting application that allows voting without a logged in user.

Provides abstract base model for types that the user wishes to allow voting on as well as related utilities including generic views to ease the addition of 'anonymous' voting to a Django project.

Maintained by `Basil Shubin <https://github.com/bashu/>`_, and some great
`contributors <https://github.com/bashu/django-secretballot/contributors>`_.

Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI:

.. code-block:: bash

    pip install django-secretballot

Setup
=====

First of all, you must add this project to your list of ``INSTALLED_APPS`` in
``settings.py`` :

.. code-block:: python
  
    INSTALLED_APPS += [
        "secretballot",  # must be last in a list
    ]

There is only one mandatory configuration option you need to set in your ``settings.py``:

.. code-block:: python

    # In order to attach the voting helpers to a particular model it is enough
    # to list them here...
    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {},
    }

Run ``./manage.py migrate``. This creates the tables in your database
that are necessary for operation.

Please see ``example`` application. This application is used to manually
test the functionalities of this package. This also serves as a good
example.

You need Django 1.8 or above to run that. It might run on older
versions but that is not tested.

Using voting-enabled models
===========================

Once a model is voting-enabled a number of special fields are available on all instances:

Fields
------

Votable objects have the following fields:

``votes``
*********

Manager to of all ``Vote`` objects related to the current model (typically doesn't need to be accessed directly). Can be renamed by passing ``votes_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:
    
.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "votes_name": "vs",
        },
    }
    
``total_upvotes``
*****************

Total number of +1 votes. Can be renamed by passing ``upvotes_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "upvotes_name": "total_upvs",
        },
    }

``total_downvotes``
*******************

Total number of -1 votes. Can be renamed by passing ``downvotes_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "downvotes_name": "total_downvs",
        },
    }

``vote_total``
**************
    
Shortcut accessor for (``total_upvotes`` minus ``total_downvotes``). Can be renamed by passing ``total_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "total_name": "v_total",
        },
    }

``_secretballot_enabled``
*************************

Boolean indicating that ``secretballot`` is enabled (can be tested for with hasattr). Cannot be renamed, exists for a reliable check that secretballot is available even if all other fields were renamed.

Methods
-------

Votable objects have the following custom methods:

``add_vote``
************

Function that takes a ``token`` and a vote (+1 or -1) and adds or updates the vote for said token. Can be renamed by passing ``add_vote_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "add_vote_name": "add_v",
        },
    }

``remove_vote``
***************

Function that takes a ``token`` and removes the vote (if present) for said token. Can be renamed by passing ``remove_vote_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "remove_vote_name": "remove_v",
        },
    }

Manager functions
-----------------

A special manager is added that enables the inclusion of ``total_upvotes`` and ``total_downvotes`` as well as some extra functionality.

This manager by default replaces the ``objects`` manager, but this can be altered by passing the ``manager_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "manager_name": "ballot_custom_manager",
        },
    }


There is also an additional method on the Votable manager:

``from_request(self, request)``
*******************************
    
When called on a votable object's queryset will add a ``user_vote`` attribute that is the vote cast by the current 'user' (actually the token assigned to the request), for example:

.. code-block:: python

    def story_view(request, slug):
        story = Story.objects.from_request(request).get(pk=slug)
        # story has the following extra attributes
        # user_vote: -1, 0, or +1
        # total_upvotes: total number of +1 votes
        # total_downvotes: total number of -1 votes
        # vote_total: total_upvotes-total_downvotes
        # votes: related object manager to get specific votes (rarely needed)


Tokens and SecretBallotMiddleware
---------------------------------

Without user logins it is impossible to be certain that a user does not vote more than once, but there are several methods to limit abuses.  ``secretballot`` takes a fairly hands-off approach to this problem, the Vote object has a ``token`` field that is used to store a uniquely identifying token generated from a request.  To limit how many votes come from a particular ip address it is sufficient to set the token to the IP address, but it is also possible to develop more sophisticated heuristics to limit voters.

``secretballot`` uses a simple piece of middleware to do this task, and makes it trival for users to define their own middleware that will use whatever heuristic they desire.

``SecretBallotMiddleware`` is an abstract class that defines a ``generate_token(request)`` method that should return a string to be used for the token.  

For convenience several middleware have already been defined:

``SecretBallotIpMiddleware``
****************************

Simply sets the ``token`` to ``request.META['REMOTE_ADDR']`` -- the user's IP address

``SecretBallotIpUseragentMiddleware``
*************************************

Sets the ``token`` to a hash of the user's ip address and user agent -- hopefully slightly more unique than IP alone

If you wish to define your own middleware simply derive a class from ``SecretBallotMiddleware`` and implement the ``generate_token`` method. If you come up with something that may be useful for others contributions are always welcome.

Generic Views
-------------

``secretballot.views`` includes the following generic views:

``secretballot.views.vote``
***************************

**Description:**

This view creates or alters a vote on the object of ``content_type`` with a primary key of ``object_id``.
If a vote already exists it will be replaced (unless vote is 0 in which case it will be deleted).

The ``token`` attribute of the vote that is used to prevent unlimited voting is set within this view based on the active ``SecretBallotMiddleware``.

Depending on the parameters given the return value of this view varies:
    
#. if ``redirect_url`` is specified it will be used no matter what
#. if ``template_name`` is specified it will be used (along with ``template_loader``, ``context_processors`` and etc.)
#. without ``redirect_url`` or ``template_name`` a text/json response will be returned

**Required arguments:**

* ``content_type`` : class that voting is taking place on (a VotableModel-derived model). 

  May be an instance of ``django.contrib.contenttypes.models.ContentType``, the Model class itself, or an ``<app_label.model_name>`` string.
* ``object_id`` : primary key of object to vote on
* ``vote`` : value of this vote (+1, 0, or -1) (0 deletes the vote)

**Optional arguments:**

* ``can_vote_test`` : function that allows limiting if user can vote or not. It's an optional argument to the view that can be specified in the urlconf that is called before a vote is recorded for a user.

  Example implementation of ``can_vote_test``:

  .. code-block:: python

      from secretballot.utils import get_vote_model

      def only_three_votes(request, content_type, object_id, vote):
          return get_vote_model().objects.filter(content_type=content_type, token=request.secretballot_token).count() < 3

  All ``can_vote_test`` methods must take the non-optional parameters to ``secretballot.views.vote`` and should return ``True`` if the vote should be allowed. If the vote is not allowed by default the view will return a 403, but it is also acceptable to raise a different exception.

* ``redirect_url`` : url to redirect to, if present will redirect instead of returning a normal HttpResponse
* ``template_name`` : template to render to, recieves a context containing ``content_obj`` which is the object voted upon
* ``template_loader`` : template loader to use, defaults to ``django.template.loader``
* ``extra_context`` : dictionary containing any extra context, callables will be called at render time
* ``context_processors`` : list of context processors for this view
* ``mimetype`` :  mimetype override

Credits
=======

`django-secretballot <https://github.com/bashu/django-secretballot/>`_ was originally started by `James Turk <https://jamesturk.net/>`_ who has now unfortunately abandoned the project.

License
=======

``django-secretballot`` is released under the BSD license.
