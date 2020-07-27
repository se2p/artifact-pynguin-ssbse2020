from collections import (
    defaultdict,
    namedtuple,
)


# noinspection PyAttributeOutsideInit
class CherryPickingMixin:

    @property
    def build_attr_mapping(self):
        # Poor man's cached property
        if not hasattr(self, '_build_attr_mapping_'):
            self._build_attr_mapping_ = namedtuple(
                '_AttrMapping',
                'attr_name, mod_name, mod_attr_name, item'
            )
        return self._build_attr_mapping_

    @property
    def cherry_pick_map(self):
        # Poor man's cached property
        if not hasattr(self, '_cherry_pick_map_'):
            modules = defaultdict(list)
            modules['foomod'].append(
                self.build_attr_mapping(
                    'foomod',
                    'foomod',
                    '',
                    'foomod'
                )
            )
            modules['barmod'].append(
                self.build_attr_mapping(
                    'bar',
                    'barmod',
                    'bar',
                    'barmod:bar'
                )
            )
            identifiers = dict(foomod='foomod', bar='barmod')
            build = namedtuple('_CherryPickMap', 'modules, identifiers')
            self._cherry_pick_map_ = build(modules, identifiers)
        return self._cherry_pick_map_

    @property
    def attr_map(self):
        # Poor man's cached property
        if not hasattr(self, '_attr_map_'):
            self._attr_map_ = tuple(['foomod', 'barmod:bar'])
        return self._attr_map_

    @property
    def additional_attrs(self):
        # Poor man's cached property
        if not hasattr(self, '_additional_attrs_'):
            self._additional_attrs_ = dict(one=1, two=2, __foo__='bar')
        return self._additional_attrs_

    @property
    def all_value(self):
        return list(sorted(['foomod', 'bar', 'one', 'two']))
