Application
--------------------

Declaring an app
""""""""""""""""

*This is how you would declare an app instance.*

.. literalinclude:: ../../src/chanina/examples/basic_usage.py
   :language: python
   :lines: 1-29

*Running the celery worker ...*

.. code-block:: bash

    $ celery -A app:celery worker


*Running a default feature as a single task.*

.. code-block:: bash

   $ poetry run cli -a app:app --task _chanina.list_features



Profile handling
""""""""""""""""


Worker specificities
""""""""""""""""""""



