from wtforms import Form, StringField, IntegerField, validators

# Form for creating/editing an artist


class ArtistForm(Form):
    name = StringField('Name of artist', [validators.DataRequired()])
    year_of_birth = IntegerField('Year of birth', [validators.Optional()])
    year_of_death = IntegerField('Year of death', [validators.Optional()])
    country = StringField('Country', [validators.Optional()])
    art_movement = StringField('Art movement', [validators.Optional()])

# Form for creating/editing an artwork


class ArtworkForm(Form):
    title = StringField('Title', [validators.DataRequired()])
    medium = StringField('Medium', [validators.Optional()])
    size = StringField('Dimensions', [validators.Optional()])
    year_created = IntegerField('Year created', [validators.Optional()])
