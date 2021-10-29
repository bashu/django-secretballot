Using voting-enabled models
===========================

Once a model is voting-enabled a number of special fields are available on all instances:

Fields
------

Votable objects have the following fields:

votes
~~~~~

Manager to of all ``Vote`` objects related to the current model (typically doesn't need to be accessed directly). Can be renamed by passing ``votes_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "votes_name": "vs",
        },
    }

total_upvotes
~~~~~~~~~~~~~

Total number of +1 votes. Can be renamed by passing ``upvotes_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "upvotes_name": "total_upvs",
        },
    }

total_downvotes
~~~~~~~~~~~~~~~

Total number of -1 votes. Can be renamed by passing ``downvotes_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "downvotes_name": "total_downvs",
        },
    }

vote_total
~~~~~~~~~~

Shortcut accessor for (``total_upvotes`` minus ``total_downvotes``). Can be renamed by passing ``total_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

.. code-block:: python

    SECRETBALLOT_FOR_MODELS = {
        "<app_label.model_name>": {
            "total_name": "v_total",
        },
    }

_secretballot_enabled
~~~~~~~~~~~~~~~~~~~~~

Boolean indicating that ``secretballot`` is enabled (can be tested for with ``hasattr``). Cannot be renamed, exists for a reliable check that ``secretballot`` is available even if all other fields were renamed.

Methods
-------

Votable objects have the following custom methods:

.. py:method:: add_vote(token, vote):

    Adds or updates the vote for said token. Can be renamed by passing ``add_vote_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

    .. code-block:: python

        SECRETBALLOT_FOR_MODELS = {
            "<app_label.model_name>": {
                "add_vote_name": "add_v",
            },
        }

    :param str token: mandatory token
    :param int vote: value of this vote (+1, 0, or -1) (0 deletes the vote)

.. py:method:: remove_vote(token):

    Removes the vote (if present) for said token. Can be renamed by passing ``remove_vote_name`` parameter to ``SECRETBALLOT_FOR_MODELS``, for example:

    .. code-block:: python

        SECRETBALLOT_FOR_MODELS = {
            "<app_label.model_name>": {
                "remove_vote_name": "remove_v",
            },
        }

    :param str token: mandatory token

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

.. py:method:: from_request(request):

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

    :param django.http.HttpRequest request: the request object.
    :rtype: instance of :class:`django.db.models.query.QuerySet`.


.. _tokens_and_secretballotmiddleware:

Tokens and SecretBallotMiddleware
---------------------------------

Without user logins it is impossible to be certain that a user does not vote more than once, but there are several methods to limit abuses.  ``secretballot`` takes a fairly hands-off approach to this problem, the ``Vote`` object has a ``token`` field that is used to store a uniquely identifying token generated from a ``request``.  To limit how many votes come from a particular ip address it is sufficient to set the ``token`` to the IP address, but it is also possible to develop more sophisticated heuristics to limit voters.

``secretballot`` uses a simple piece of middleware to do this task, and makes it trival for users to define their own middleware that will use whatever heuristic they desire.

``secretballot.middleware.SecretBallotMiddleware`` is an abstract class that defines a ``generate_token(request)`` method that should return a string to be used for the token.

For convenience several middleware have already been defined:

secretballot.middleware.SecretBallotIpMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply sets the ``token`` to ``request.META['REMOTE_ADDR']`` -- the user's IP address

secretballot.middleware.SecretBallotIpUseragentMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sets the ``token`` to a hash of the user's ip address and user agent -- hopefully slightly more unique than IP alone.

If you wish to define your own middleware simply derive a class from ``secretballot.middleware.SecretBallotMiddleware`` and implement the ``generate_token`` method. If you come up with something that may be useful for others contributions are always welcome.

Generic views
-------------

``secretballot.views`` includes the following generic views:

.. py:function:: vote(request, content_type, object_id, vote, can_vote_test=None, redirect_url=None, template_name=None, template_loader=loader, extra_context=None, context_processors=None, mimetype=None):

    This view creates or alters a vote on the object of ``content_type`` with a primary key of ``object_id``.
    If a vote already exists it will be replaced (unless vote is 0 in which case it will be deleted).

    The ``token`` attribute of the vote that is used to prevent unlimited voting is set within this view based on the active ``SecretBallotMiddleware`` class.

    Depending on the parameters given the return value of this view varies:

    #. if ``redirect_url`` is specified it will be used no matter what
    #. if ``template_name`` is specified it will be used (along with ``template_loader``, ``context_processors`` and etc.)
    #. without ``redirect_url`` or ``template_name`` a *text/json* response will be returned


    :param django.http.HttpRequest request: the request object.
    :param content_type: class that voting is taking place on (a VotableModel-derived model).
                         May be an instance of ``django.contrib.contenttypes.models.ContentType``, the model class itself, or an ``app_label.model_name`` string.
    :param str object_id: primary key of object to vote on
    :param int vote: value of this vote (+1, 0, or -1) (0 deletes the vote)

    :param can_vote_test: (Optional) function that allows limiting if user can vote or not. It's an optional argument to the view that can be specified in the urlconf that is called before a vote is recorded for a user

        |

        Example implementation of ``can_vote_test``:

        .. code-block:: python

            from secretballot.utils import get_vote_model

            def only_three_votes(request, content_type, object_id, vote):
                return get_vote_model().objects.filter(
                        content_type=content_type,
                        token=request.secretballot_token,
                ).count() < 3

        |

        All ``can_vote_test`` methods must take the non-optional parameters to ``secretballot.views.vote`` and should return ``True`` if the vote should be allowed. If the vote is not allowed by default the view will return a 403, but it is also acceptable to raise a different exception.

    :param str redirect_ur: (Optional) url to redirect to, if present will redirect instead of returning a normal HttpResponse
    :param str template_name: (Optional) template to render to, recieves a context containing ``content_obj`` which is the object voted upon
    :param template_loader: (Optional) template loader to use, defaults to ``django.template.loader``
    :param dict extra_context: (Optional) dictionary containing any extra context, callables will be called at render time
    :param context_processors: (Optional) list of context processors for this view
    :param str mimetype: (Optinal) mimetype override
    :rtype: django.http.HttpResponse

