Changes
-------

2.0.0 (unreleased)
------------------

- drop compatibility code for Django 1.10 and below

1.0.0 (2017-12-05)
------------------

- final release that supports Django 1.8 and up

0.7.1 (2017-10-03)
------------------

- improved support for Django 2.0

0.7.0 (2017-05-05)
------------------

- improved support for Django 1.11

0.6.0 (2016-10-07)
------------------

- support for Django 1.10 new manager rules
- add migrations
- fix case where object is not fetched through correct manager

0.5.0 (2015-11-02)
------------------

- drop South support
- drop support for Django < 1.8, add support for Django 1.9

0.4.0 (2015-05-27)
------------------

- drop South support
- drop support for Django < 1.7, add support for Django >= 1.7
- add Python 3 support
- add a ton of tests
- fix bug if vote_name was set in enable_voting_on

0.3.0 (2015-04-17)
------------------

- related_fields and get_object_or_404 fix from François Chapuis
- add property to check if secretballot is present on a class
- add indexed timestamps to votes via Simon de Han
- make response valid JSON for mimetype compatibility via Dan Drinkard

0.2.3 (2010-03-30)
------------------

- bugfixes, thanks to Gennadiy Potapov

0.2.2 (2009-11-27)
------------------

- fixed embarassing SyntaxError in vote

0.2.1 (2009-11-24)
------------------

- fix some documentation issues left from 0.1
- make content_type more flexible (can now take a model, content_type, or 'app.model' string)

0.2.0 (2009-02-11)
------------------

- replace inheritance from VotableObject with enable_voting_on
- when injecting manager methods inherit from existing manager

0.1.0 (2009-01-24)
------------------

- initial working release
