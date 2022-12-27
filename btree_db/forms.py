from django.forms import Form, IntegerField, CharField, Textarea, NumberInput, ValidationError
from .db.db_operations import init_db


class KeyValueForm(Form):
    key = IntegerField(label='', min_value=0, max_value=2 ** 32 - 1, widget=NumberInput({'placeholder': 'Key'}))
    value = CharField(label='', max_length=2 ** 16 - 1, widget=Textarea({'placeholder': 'Value', 'rows': 5}))


class KeyForm(Form):
    key = IntegerField(label='', min_value=0, widget=NumberInput({'placeholder': 'Key'}))


class KeyExistsForm(Form):

    def clean_key(self):
        key = int(self.cleaned_data['key'])
        btree = init_db(False)
        with btree.open('r'):
            try:
                btree[key]
            except KeyError:
                return key
            else:
                raise ValidationError('Key already exists')


class KeyDoesntExistForm(Form):

    def clean_key(self):
        key = int(self.cleaned_data['key'])
        btree = init_db(False)
        with btree.open('r'):
            try:
                btree[key]
            except KeyError:
                raise ValidationError("Key doesn't exists")
            else:
                return key


class InsertForm(KeyValueForm, KeyExistsForm):
    pass


class UpdateForm(KeyValueForm, KeyDoesntExistForm):
    pass


class DeleteForm(KeyForm, KeyDoesntExistForm):
    pass


class ReadForm(KeyForm, KeyDoesntExistForm):
    pass
