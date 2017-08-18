#!/usr/bin/env python
# -*- coding: utf-8 -*-


import settings
from yy.entity.formulas import register_formula
from yy.entity.index import SortedIndexing, UniqueIndexing, SetIndexing


@register_formula
def get_idx(floor):
    from common.index import IndexString
    index = IndexString('C_T_{$regionID}_f{%d}' % floor)
    return SortedIndexing(index.render(), settings.REDISES['index'])


@register_formula
def get_idx_p(floor):
    from common.index import IndexString
    index = IndexString('C_T_{$regionID}_p{%d}' % floor)
    return SortedIndexing(index.render(), settings.REDISES['index'])


@register_formula
def get_lock(floor):
    from common.index import IndexString
    index = IndexString('C_T_{$regionID}_l{%d}' % floor)
    return SortedIndexing(index.render(), settings.REDISES['index'])
