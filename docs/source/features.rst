Features
--------


What is it ?
~~~~~~~~~~~~~~~~~~~

A feature is a decorated function that you can implement, which have access to the current **WorkerSession** object, and can be ran as a **Celery** task.


Default features
~~~~~~~~~~~~~~~~

*Every ChaninaAppplication instance comes with default features registered that you can find below*

.. autofunction:: chanina.default_features.chanina_new_page
   :no-index:

.. autofunction:: chanina.default_features.chanina_close_page
   :no-index:

.. autofunction:: chanina.default_features.chanina_list_features
   :no-index:


====================================================================================================


Object(s) Reference(s)
""""""""""""""""""""""

.. autoclass:: chanina.core.features.Feature
   :no-index:

.. autoclass:: chanina.core.worker_session.WorkerSession
   :no-index:

.. autoclass:: chanina.core.chanina.ChaninaApplication
   :no-index:

