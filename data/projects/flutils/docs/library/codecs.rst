******
Codecs
******

  flutils contains additional codecs that, when registered, can be used to
  convert bytes to strings and strings to bytes.

.. _b64:

b64
---
  The ``b64`` codec will decode bytes to base64 string characters; and will
  encode strings containing base64 string characters into bytes.  Base64
  string characters can span multiple lines and may have whitespace
  indentation.

  *New in version 0.4.*

.. _raw_utf8_escape:

Raw UTF-8 Escape
----------------
  The ``raw_utf8_escape`` codec will decode a byte string containing
  escaped UTF-8 hexadecimal into a string with the proper characters.  Strings
  encoded with the ``raw_utf8_escape`` codec will be of ascii bytes and have
  escaped UTF-8 hexadecimal used for non printable characters and each
  character with an :obj:`ord` value above ``127``

  *New in version 0.4.*


Registering Codecs
------------------
  Using any of the above codecs requires registering them with Python by
  using the following function:


  .. autofunction:: flutils.codecs.register_codecs
