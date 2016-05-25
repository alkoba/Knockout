from itertools import chain

from libraries.freetype import ft_errors

from meredith.box import Box
from meredith import datablocks
Textstyles_D = datablocks.Textstyles_D

from fonts import get_font

class _Causes_relayout(object):
    def after(self, A):
        datablocks.DOCUMENT.layout_all()

class Textstyles(_Causes_relayout, Box):
    name = 'textstyles'

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        Textstyles_D.update_datablocks(self)

_text_DNA = [('fontsize',    'float',   13),
            ('path',        'str',      'fonts/Ubuntu-R.ttf'),
            ('tracking',    'float',    0),
            ('shift',       'float',    0),
            ('capitals',    'bool',     False),
            ('color',       'rgba',     (1, 0.15, 0.2, 1))]

class Textstyle(_Causes_relayout, Box):
    name = 'textstyle'

    DNA  = [('name',        'str', 'Untitled fontstyle')] + [A[:2] for A in _text_DNA]
    BASE = {A: D for A, TYPE, D in _text_DNA}

class _Layer(dict):
    def __init__(self, BASE):
        dict.__init__(self, BASE)
        BASE['class'] = None
        self.Z = {A: BASE for A in BASE}
        self.members = []
    
    def overlay(self, B):
        for A, V in B.items():
            self[A] = V
            self.Z[A] = B
        self.members.append(B)

class _FLayer(_Layer):
    def vmetrics(self):
        ascent, descent = self['fontmetrics'].vmetrics
        return ascent * self['fontsize'] + self['shift'], descent * self['fontsize'] + self['shift']

def _cast_default(cls):
    D = cls.BASE.copy()
    D['class'] = {}
    return cls(D)

class Blockstyles(Box):
    name = 'blockstyles'
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        
        self.block_projections = {}
        self.text_projections = {}
        
        self._block_default = _cast_default(Blockstyle)
        self._text_default = _cast_default(Textstyle)

    def after(self, A):
        self.block_projections.clear()
        self.text_projections.clear()
        datablocks.DOCUMENT.layout_all()
    
    def project_b(self, BLOCK):
        if BLOCK.implicit_ is None:
            P = BLOCK['class']
        else:
            P = BLOCK['class'] + BLOCK.implicit_
        
        H = hash(frozenset(P.items()))
        if len(BLOCK) > 1:
            H += 13 * id(BLOCK)
        
        try:
            return self.block_projections[H]
        except KeyError:
            # iterate through stack
            projection = _Layer(self._block_default)
            for B in chain((b for b in self.content if b['class'] <= P), [BLOCK]):
                projection.overlay(B)
            
            self.block_projections[H] = projection
            return projection

    def project_t(self, BLOCK, F):
        if BLOCK.implicit_ is None:
            P = BLOCK['class']
        else:
            P = BLOCK['class'] + BLOCK.implicit_
        
        H = 22 * hash(frozenset(P.items())) + hash(frozenset(F.items())) # we must give paragraph a different factor if a style has the same name as a fontstyle
        
        try:
            return self.text_projections[H]
        except KeyError:
            # iterate through stack
            projection = _FLayer(self._text_default)
            for memberstyles in (b.content for b in self.content if b.content is not None and b['class'] <= P):
                for TS in (c['textstyle'] for c in memberstyles if c['class'] <= F and c['textstyle'] is not None):
                    projection.overlay(TS)
            
            try:
                projection['fontmetrics'], projection['font'] = get_font(projection['path'])
            except ft_errors.FT_Exception:
                path = Textstyle.BASE['path']
                projection['color'] = (1, 0.15, 0.2, 1)
                projection['fontmetrics'], projection['font'] = get_font(path)
            
            projection['hash'] = H
            
            self.text_projections[H] = projection
            return projection

_block_DNA = [('hyphenate',       'bool',   False),
            ('indent',          'binomial', (0, 0, 0)),
            ('indent_range',    'int set',  {0}),
            ('leading',         'float',    22),
            ('margin_bottom',   'float',    0),
            ('margin_left',     'float',    0),
            ('margin_right',    'float',    0),
            ('margin_top',      'float',    0),
            ('align',           'float',    0),
            ('align_to',        'str',      ''),
            
            ('incr_place_value','int',      13),
            ('incr_assign',     'fn',       None),
            ('show_count',      'farray',   None)]

class Blockstyle(Box):
    name = 'blockstyle'
    
    DNA  = [('class',           'blocktc',  'body')] + [A[:2] for A in _block_DNA]
    BASE = {A: D for A, TYPE, D in _block_DNA}

    def after(self, A):
        datablocks.BSTYLES.block_projections.clear()
        datablocks.BSTYLES.text_projections.clear()
        datablocks.DOCUMENT.layout_all()

class Memberstyle(_Causes_relayout, Box):
    name = 'memberstyle'
    DNA  = [('class',           'texttc',  ''),
            ('textstyle',       'textstyle', None)]
    
members = (Textstyles, Textstyle, Blockstyles, Blockstyle, Memberstyle)
