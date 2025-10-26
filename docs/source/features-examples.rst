Features
-----------------

A basic feature
"""""""""""""""

*Example of a feature that will open a new page and tried to navigate to google.com*

.. literalinclude:: ../../src/chanina/examples/basic_usage.py
   :language: python
   :lines: 30-41

*Running the celery worker ...*

.. code-block:: bash

    $ celery -A app:celery worker


*Running our new feature as a single task.*

.. code-block:: bash

   $ poetry run cli -a app:app --task check-google


Passing arguments to the feature
""""""""""""""""""""""""""""""""

Using a default feature
"""""""""""""""""""""""

