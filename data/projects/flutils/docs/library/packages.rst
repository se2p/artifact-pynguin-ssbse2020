========
Packages
========

  flutils offers the following package utilities:



Version Numbers
---------------

  In flutils a version number consists of two or three
  dot-separated numeric components, with an optional
  "pre-release" tag on the right-component. The pre-release tag
  consists of the letter 'a' (alpha) or 'b' (beta) followed by a
  number. If the numeric components of two version numbers are
  equal, then one with a pre-release tag will always be deemed
  earlier (lesser) than one without.

  The following are valid version numbers::

      0.4
      0.4.1
      0.5a1
      0.5b3
      0.5
      0.9.6
      1.0
      1.0.4a3
      1.0.4b1
      1.0.4

  The following are examples of invalid version numbers::

      1
      2.7.2.2
      1.3.a4
      1.3pl1
      1.3c4

  The following function is designed to work with version
  numbers formatted as described above:

  .. autofunction:: flutils.packages.bump_version
