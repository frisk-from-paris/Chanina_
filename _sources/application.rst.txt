Application
-------------------


What is it ?
~~~~~~~~~~~~

ChaninaAppplication is the **app** instance that registers your features, manages the injection of the WorkerSession, and handles the **Celery** application instance.

Profile handling
~~~~~~~~~~~~~~~~

*A browser context can write the session's data into a profile directory. ChaninaApplication manages it for your WorkerSession.*

.. autofunction:: chanina.core.chanina.init_profile
   :no-index:

.. autofunction:: chanina.core.chanina.remove_profile
   :no-index:


Celery init and shutdown signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Every ChaninaAppplication instance comes with default features registered that you can find below*


====================================================================================================


Object(s) reference(s)
""""""""""""""""""""""

.. autoclass:: chanina.core.chanina.ChaninaApplication
   :no-index:
