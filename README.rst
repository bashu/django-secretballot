===================
django-secretballot
===================

Django voting application that allows voting without a logged in user.

Provides abstract base model for types that the user wishes to allow voting on as well as related utilities including generic views to ease the addition of 'anonymous' voting to a Django project.

django-secretballot is a project of Sunlight Labs (c) 2009.
Written by James Turk <jturk@sunlightfoundation.com>

Source: http://github.com/sunlightlabs/django-secretballot/

Requirements
============

python >= 2.4

django >= 1.0

Installation
============

To install run 

    ``python setup.py install``

which will install the application into the site-packages directory.

Usage
=====

settings.py
-----------

* add ``secretballot`` to INSTALLED_APPS
* add a secretballot middleware to MIDDLEWARE_CLASSES (see middleware section for details)

Declaring 'Votable' Models
--------------------------

In order to attach the voting helpers to a particular class it is necessary to define a model that derives from secretballot.models.VotableModel rather than django.db.models.Model.  No other changes to the model are necessary.

The only limitation is that the model does not define any of the following field names:
* votes
* total_upvotes
* total_downvotes
* vote_total

For example::

    from secretballot.models import VotableModel
    
    class Story(VotableModel):
        ... 

Using 'Votable' Models
----------------------

Models that inherit from VotableModel inherit some extra field names:

total_upvotes: 
    Total number of +1 votes
total_downvotes:
    Total number of -1 votes
vote_total:
    shortcut accessor for (total_upvotes-total_downvotes)
votes: 
    Manager to a list of all ``Vote`` objects related to the current model (typically doesn't need to be accessed directly)

tokens and SecretBallotMiddleware
---------------------------------

Without user logins it is impossible to be certain that a user does not vote more than once, but there are several methods to limit abuses.  secretballot takes a fairly hands-off approach to this problem, the Vote object has a ``token`` field that is used to store a uniquely identifying token generated from a request.  To limit how many votes come from a particular ip address it is sufficient to set the token to the IP address, but it is also possible to develop more sophisticated heuristics to limit voters.

secretballot uses a simple piece of middleware to do this task, and makes it trival for users to define their own middleware that will use whatever heuristic they desire.

SecretBallotMiddleware is an abstract class that defines a generate_token(request) method that should return a string to be used for the token.  

For convinience several middleware have already been defined:

SecretBallotIpMiddleware:
    simply sets the token to request.META['REMOTE_ADDR'] -- the user's IP address
SecretBallotIpUseragentMiddleware:
    sets the token to a hash of the user's ip address and user agent -- hopefully slightly more unique than IP alone

If you wish to define your own middleware simply derive a class from SecretBallotMiddleware and implement the generate_token method. If you come up with something that may be useful for others contributions are always welcome.

Generic Views
-------------

``secretballot.views`` includes the following generic views::
    
    vote(request, content_type, object_id, vote, 
         redirect_url=None, template_name=None, template_loader=loader, 
         extra_context=None, context_processors=None, mimetype=None)

This view creates or alters a vote on the object of ``content_type`` with a primary key of ``object_id``.
If a vote already exists it will be replaced (unless vote is 0 in which case it will be deleted).

The ``token`` attribute of the vote that is used to prevent unlimited voting is set within this view based on the active SecretBallotMiddleware.

Depending on the parameters given the return value of this view varies:
    
    #. if redirect_url is specified it will be used no matter what
    #. if template_name is specified it will be used (along with template_loader, context_processors, etc.)
    #. without redirect_url or template_name a text/json response will be returned

content_type:
    Class that voting is taking place on (a VotableModel-derived model)
object_id:
    primary key of object to vote on
vote:
    value of this vote (+1, 0, or -1) (0 deletes the vote)
redirect_url:
    (optional) url to redirect to, if present will redirect instead of returning a normal HttpResponse
template_name:
    (optional) template to render to, recieves a context containing ``content_obj`` which is the object voted upon
template_loader:
    (optional) template loader to use, defaults to ``django.template.loader``
extra_context:
    (optional) dictionary containing any extra context, callables will be called at render time
context_processors:
    (optional) list of context processors for this view
mimetype:
    (optional) mimetype override

