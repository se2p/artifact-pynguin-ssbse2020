# pylint: disable=E0603
from .moduleutils import cherry_pick

__all__ = [
    'AnsiTextWrapper',
    'add_setup_cfg_commands',
    'as_escaped_unicode_literal',
    'as_escaped_utf8_literal',
    'bump_version',
    'cached_property',
    'camel_to_underscore',
    'cherry_pick',
    'chmod',
    'chown',
    'convert_escaped_unicode_literal',
    'convert_escaped_utf8_literal',
    'directory_present',
    'exists_as',
    'find_paths',
    'get_os_group',
    'get_os_user',
    'has_any_attrs',
    'has_any_callables',
    'has_attrs',
    'has_callables',
    'is_list_like',
    'is_subclass_of_any',
    'lazy_import_module',
    'len_without_ansi',
    'normalize_path',
    'path_absent',
    'register_codecs',
    'run',
    'to_namedtuple',
    'underscore_to_camel',
    'validate_identifier',
    'cmdutils',
    'codecs',
    'decorators',
    'moduleutils',
    'moduleutils',
    'namedtupleutils',
    'objutils',
    'packages',
    'pathutils',
    'setuputils',
    'strutils',
    'txtutils',
    'validators',

]

__version__ = '0.6'

# map of functions with modules to be cherry-picked.
__attr_map__ = (
    'flutils.cmdutils:run',
    'flutils.codecs:register_codecs',
    'flutils.decorators:cached_property',
    'flutils.namedtupleutils:to_namedtuple',
    'flutils.moduleutils:cherry_pick',
    'flutils.moduleutils:lazy_import_module',
    'flutils.objutils:has_any_attrs',
    'flutils.objutils:has_any_callables',
    'flutils.objutils:has_attrs',
    'flutils.objutils:has_callables',
    'flutils.objutils:is_list_like',
    'flutils.objutils:is_subclass_of_any',
    'flutils.packages:bump_version',
    'flutils.pathutils:chmod',
    'flutils.pathutils:chown',
    'flutils.pathutils:directory_present',
    'flutils.pathutils:exists_as',
    'flutils.pathutils:find_paths',
    'flutils.pathutils:get_os_group',
    'flutils.pathutils:get_os_user',
    'flutils.pathutils:normalize_path',
    'flutils.pathutils:path_absent',
    'flutils.setuputils:add_setup_cfg_commands',
    'flutils.strutils:as_escaped_unicode_literal',
    'flutils.strutils:as_escaped_utf8_literal',
    'flutils.strutils:camel_to_underscore',
    'flutils.strutils:convert_escaped_unicode_literal',
    'flutils.strutils:convert_escaped_utf8_literal',
    'flutils.strutils:underscore_to_camel',
    'flutils.txtutils:len_without_ansi',
    'flutils.txtutils:AnsiTextWrapper',
    'flutils.validators:validate_identifier',
    'flutils.cmdutils',
    'flutils.codecs',
    'flutils.decorators',
    'flutils.moduleutils',
    'flutils.moduleutils',
    'flutils.namedtupleutils',
    'flutils.objutils',
    'flutils.packages',
    'flutils.pathutils',
    'flutils.setuputils',
    'flutils.strutils',
    'flutils.txtutils',
    'flutils.validators',
)

cherry_pick(globals())
