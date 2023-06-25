import pycountry
from wtforms import SelectField


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [
            (country.alpha_2, country.name) for country in pycountry.countries
        ]
        self.choices.sort(key=lambda x: x[1])
