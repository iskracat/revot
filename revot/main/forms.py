import re
from datetime import timedelta as delta, datetime
from flask import current_app
from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext
from wtforms import ( SelectMultipleField, SubmitField, StringField, TextAreaField,
                      DateTimeField, BooleanField, IntegerField, ValidationError,
                      FormField, FieldList, SelectField )
from wtforms.fields.html5 import IntegerField as StepIntegerField 
from wtforms.widgets import CheckboxInput, ListWidget, HTMLString, html_params
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, ValidationError


class ListCheckboxWidget(ListWidget):
    """ 
    ListWidget doesn't do rendering properly with Twitter Bootstrap's CSS. 
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ["\n"]
        for subfield in field:
            html.append(u'<div class="checkbox"><label>%s%s</label></div>\n' % (subfield(), subfield.label.text))
        return HTMLString(u''.join(html))
    

class BallotForm(Form):
    options = SelectMultipleField(
        option_widget=CheckboxInput(),
        widget=ListCheckboxWidget(prefix_label=False),
        coerce=int
    )
    submit  = SubmitField(lazy_gettext(u'Vote'))
    
    def __init__(self, *args, **kwargs):                                        
        super(BallotForm,self).__init__(*args, **kwargs)                          
        self.max = kwargs['max']                                      
        self.min = kwargs['min']                                      

    def validate_options(self, field):
        if not(self.min <= len(field.data) <= self.max):
            raise ValidationError(lazy_gettext(u'You must choose between %s and %s options') % (self.min, self.max))




_ADD_BUTTON = \
"""
<span class="input-group-btn">
<button class="btn btn-success btn-add" type="button">
<span class="glyphicon glyphicon-plus"></span>
</button>
</span>
"""

_LOCKED_BUTTON = \
"""
<span class="input-group-btn">
<button class="btn" type="button">
<span class="glyphicon glyphicon-lock">
</span>
</button>
</span>
"""

_REMOVE_BUTTON = \
"""
<span class="input-group-btn">
<button class="btn btn-danger btn-remove" type="button">
<span class="glyphicon glyphicon-minus">
</span>
</button>
</span>
"""


class DynamicListWidget(object):
    """
    Renders a list of fields that grows at user demand. Assumes simple subfields.
    """
    def __init__(self, prefix_label=True):
        self.html_tag = 'div'
        self.prefix_label = prefix_label
        self.add_button = _ADD_BUTTON
        self.remove_button = _REMOVE_BUTTON
        self.locked_button = _LOCKED_BUTTON
        
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = list()
        html.append('<%s %s>' % (self.html_tag, 'id=options'))

        # take into account 'min_entries'
        mine = field.min_entries - 1
        # locked fields
        for subfield in field[:mine]:
            html.append('<div class="input-group">%s %s</div>' % \
                        (subfield(class_="form-control"), self.locked_button))
        # user added fields but the last one
        for subfield in field[mine:-1]:
            html.append('<div class="input-group">%s %s</div>' % \
                        (subfield(class_="form-control"), self.remove_button))
        # last field
        subfield = field[-1]
        html.append('<div class="input-group">%s %s</div>' % \
                    (subfield(class_="form-control"), self.add_button))
            
        html.append('</%s>' % self.html_tag)
        return HTMLString(''.join(html))


    
    
class VotingForm(Form):
    """
    Renders a form to create a new voting
    """

    title = StringField(lazy_gettext(u'Id'),
                        [Length(min=4, max=20), InputRequired()],
                        description=lazy_gettext(u'Public identifier used for the voting (max 20 chars).'))

    language =  SelectField(lazy_gettext(u'Language'),
                            description=lazy_gettext(u'Ballots will be written in this language.')) 

    descr = TextAreaField(lazy_gettext(u'Description'),
                          [InputRequired(), Length(max=100)],
                          description=lazy_gettext(u'A short description of the voting (max 100 chars).'))

    roll = TextAreaField(lazy_gettext(u'Voting roll'),
                          [InputRequired(),
                           Regexp(ur'^(?:\w+(?:\.\w+)*@\w+(?:\.\w+)* *, *[ \.\-\w]+\s*)+$',
                                  re.UNICODE,
                                  lazy_gettext(u'Wrong data format.'))],
                          description=lazy_gettext(u'List of <email>, <name> for people enrolled in this voting.'))

    starts = DateTimeField(lazy_gettext(u'Voting opens at'),
                             [InputRequired()])

    duration = SelectField(lazy_gettext(u'Voting duration'),
                           coerce=int,
                           description=lazy_gettext(u'The voting is open during this time.'))

    send_ballots = SelectField(lazy_gettext(u'Send ballots'),
                               coerce=int,
                               description=lazy_gettext(u'Send ballots this time before opening the voting.'))
    
    question = TextAreaField(lazy_gettext(u'Question'),
                             [InputRequired(), Length(min=10, max=100)],
                             description=lazy_gettext(u'The question printed in the ballot.'))

    options  = FieldList(StringField('Option'),
                         min_entries=2,
                         widget=DynamicListWidget(),
                         label=lazy_gettext(u'Options'),
                         description=lazy_gettext(u'During the voting, a voter must choose from these options.'))
    
    blanks_allowed = BooleanField(lazy_gettext(u'Blank votes are allowed'),
                                  default='checked')
    
    max_options = StepIntegerField(lazy_gettext(u'Max. choices'),
                                   [InputRequired()],
                                   default=1,
                                   description=lazy_gettext(u'In a ballot, a voter can mark at most this number of options.'))

    submit  = SubmitField(lazy_gettext(u'Add this voting'))
    

    def validate_options(form, field):
        if any(opt=='' for opt in field.data):
            raise ValidationError(lazy_gettext(u'All option fields are required.'))

    def validate_send_ballots(form, field):
        if not form.starts.data:
            # Voting start time has not been defined yet
            return

        time_left = form.starts.data - datetime.utcnow()
        if field.data < 0:
            # Send ballots from now: check if enough time left
            min_to_send = current_app.config['MIN_TIME_TO_SEND_BALLOTS_IN_MINUTES']
            print "Min to send ->", min_to_send
            if time_left < delta(minutes=min_to_send):
                raise ValidationError(lazy_gettext(u'Need to send ballots at least {0:d} minutes before voting begins.').format(min_to_send))
        else:
            # Send ballots `field.data` minutes before: check if possible
            if time_left < delta(minutes=field.data):
                raise ValidationError(lazy_gettext(u'Not enough time before voting starts.'))
            
    def validate_max_options(form, field):
        if field.data < 1 or field.data > len(form.options.data):
            raise ValidationError(lazy_gettext(u'Must be between 1 and the number of options.'))
