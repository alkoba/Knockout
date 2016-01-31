from fonts import styles
from model import cursor
from state import noticeboard

class Text_context(object):
    def __init__(self):
        self.tract = None
        self._previous_p = None
        self.paragraph = None
        self._FSTYLE = None

    def update(self):
        PP, FSTYLE = cursor.fcursor.styling_at()
        P = PP[1]
        if PP is not self.paragraph:
            print('update paragraph context')
            self.paragraph =  PP
            
            if P is not self._previous_p:
                print('update parastyle context')
                self._previous_p = P
                Parastyle.update(P)
                noticeboard.refresh_properties_stack.push_change()

        if self._FSTYLE is not FSTYLE:
            print('update font context')
            self._FSTYLE = FSTYLE
            Fontstyle.update(FSTYLE)
            noticeboard.refresh_properties_stack.push_change()

    def update_force(self):
        PP, self._FSTYLE = cursor.fcursor.styling_at()
        P = PP[1]
        self.paragraph =  PP
        self._previous_p = None
        Parastyle.update(P)
        Fontstyle.update(self._FSTYLE)
        noticeboard.refresh_properties_stack.push_change()

class Paragraph_context(object):
    def __init__(self):
        pass
    def update(self, P):
        self.parastyle = styles.PARASTYLES.project_p(P)

class Font_context(object):
    def __init__(self):
        pass
    
    def update(self, FSTYLE):
        self.fontstyle = FSTYLE

Fontstyle = Font_context()
Parastyle = Paragraph_context()
Text = Text_context()
