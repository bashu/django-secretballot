# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/bashu/django-secretballot/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                         |    Stmts |     Miss |   Cover |   Missing |
|----------------------------- | -------: | -------: | ------: | --------: |
| secretballot/\_\_init\_\_.py |       58 |        9 |     84% |4-17, 50-51, 115-119 |
| secretballot/apps.py         |       10 |        1 |     90% |        12 |
| secretballot/middleware.py   |       19 |        1 |     95% |        32 |
| secretballot/models.py       |       20 |        0 |    100% |           |
| secretballot/receivers.py    |        6 |        0 |    100% |           |
| secretballot/settings.py     |        2 |        0 |    100% |           |
| secretballot/utils.py        |        4 |        0 |    100% |           |
| secretballot/views.py        |       50 |        4 |     92% |     88-92 |
| **TOTAL**                    |  **169** |   **15** | **91%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/bashu/django-secretballot/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/bashu/django-secretballot/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/bashu/django-secretballot/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/bashu/django-secretballot/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fbashu%2Fdjango-secretballot%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/bashu/django-secretballot/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.