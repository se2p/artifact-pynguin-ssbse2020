========
Glossary
========

   .. glossary::

      cherry-pick
         is a term used within the context of flutils to describe the process of choosing modules
         that will be lazy-loaded.   Meaning, the module (as set in the :term:`foreign-name`) will
         be loaded (unless already loaded) and executed when an attribute is accessed.

         *Cherry-picking* differs from :term:`tree shaking` in that it does not remove "dead" code.
         Instead, code is loaded (unless already loaded) and executed when used.  Unused code will
         not be loaded and executed.

      cherry-pick-definition package module
         is a term used within the context of flutils to describe a Python package module
         (``__init__.py``) which contains an ``__attr_map__`` attribute and calls the
         :obj:`~flutils.cherry_pick` function.

         ``__attr_map__`` must be a :obj:`tuple` with each row containing a :term:`foreign-name`

         This module may also have an optional ``__additional_attrs__`` attribute  which is a
         :obj:`dictionary <dict>` of attribute names and values to be passed to the
         :term:`cherry-picking module`.

         This module should not have any functions or classes defined.

      cherry-picking module
         is a term used within the context of flutils to describe a dynamically generated Python
         module that will load (unless already loaded) and execute a :term:`cherry-picked <cherry-pick>`
         module when an attribute (on the cherry-picking module) is accessed.


      foreign-name
         is a term used within the context of flutils to describe a string that contains the full
         dotted notation to a module.  This is used for :term:`cherry-picking <cherry-pick>` modules.

         This full dotted notation can **not** contain any relative
         references (e.g ``'..othermodule'``, ``'.mysubmodule'``).  However,the
         :obj:`importlib.util.resolve_name` function can be used to generate the full dotted
         notation string of a relative referenced module in a :term:`cherry-pick-definition package module`::

             from importlib.util import resolve_name
             from flutils import cherry_pick
             __attr_map__ = (
                 resolve_name('.mysubmodule', __package__)
             )
             cherry_pick(globals())


         The *foreign-name* for the :obj:`os.path` module is::

             'os.path'

         A *foreign-name* may also reference a :term:`module attribute` by using the full dotted notation
         to the module, followed with a colon ``:`` and then the desired :term:`module attribute`.

         To reference the :obj:`dirname <os.path.dirname>` function::

             'os.path:dirname'


         A *foreign-name* can also contain an alias which will become the attribute name on the
         :term:`cherry-picking module`.  This attribute (alias) will be bound to the :term:`cherry-picked <cherry-pick>`
         module.  Follow the `pep-8 naming conventions <https://www.python.org/dev/peps/pep-0008/#naming-conventions>`_.
         when creating the the alias.  A foreign-name with an alias is just the foreign-name followed by a comma ``,``
         then the alias::

             'mymodule.mysubmodule:hello,custom_function'

         Or::

             'mymodule.mysubmodule,mymodule'

         *Foreign-names* are used in a :term:`cherry-picking module` to manage the loading and executing of modules
         when calling attributes on the :term:`cherry-picking module`.

      glob pattern
         flutils provides functions for working with filesystem paths.  Some of these functions
         offer the ability to find matching paths using "glob patterns".

         *Glob patterns* are Unix shell-style wildcards (pattern), which are **not** the same as
         regular expressions.  The special characters used in shell-style wildcards are:

         +------------+--------------------------------------------------------------------+
         | Pattern    | Meaning                                                            |
         +============+====================================================================+
         | ``*``      | matches everything                                                 |
         +------------+--------------------------------------------------------------------+
         | ``**``     | matches any files and zero or more directories and sub directories |
         +------------+--------------------------------------------------------------------+
         | ``?``      | matches any single character                                       |
         +------------+--------------------------------------------------------------------+
         | ``[seq]``  | matches any character in *seq*                                     |
         +------------+--------------------------------------------------------------------+
         | ``[!seq]`` | matches any character not in *seq*                                 |
         +------------+--------------------------------------------------------------------+

         .. Warning:: Using the ``**`` pattern in large directory trees may consume an inordinate
            amount of time.


         **Examples:**

         - To find all python files in a directory:

             >>> from flutils import find_paths
             >>> list(find_paths('~/tmp/*.py')
             [PosixPath('/home/test_user/tmp/one.py')
             PosixPath('/home/test_user/tmp/two.py')]

         - To find all python files in a directory and any subdirectories:

             >>> list(find_paths('~/tmp/**/*.py')
             [PosixPath('/home/test_user/tmp/one.py')
             PosixPath('/home/test_user/tmp/two.py')]
             PosixPath('/home/test_user/tmp/zero/__init__.py')]

         - To find all python files that have a 3 character extension:

             >>> list(find_paths('~/tmp/*.py?')

         - To find all .pyc and .pyo files:

             >>> list(find_paths('~/tmp/*.py[co]')

         - If you want to match an arbitrary literal string that may have any of the patterns, use
           :obj:`glob.escape`:

             >>> import glob
             >>> base = glob.escape('~/a[special]file%s')
             >>> list(find_paths(base % '[0-9].txt'))

      module attribute
         is an executable statement or a function/class definition. In other words a module attribute
         is an attribute on a python module that can reference pretty much anything, such as functions,
         objects, variables, etc...

      tree shaking
         is a `term <https://developer.mozilla.org/en-US/docs/Glossary/Tree_shaking>`_ commonly used within
         JavaScript context to describe the removal of dead code.


