from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, SelectMultipleField, widgets, StringField
from wtforms.validators import AnyOf, ValidationError

def integercheck(form, field):
    if not field.data=="":
        if not field.data.isdigit():
            raise ValidationError("Insert a whole number")

def floatcheck(form, field):
    if not field.data == "":
        try:
            float(field.data)
        except ValueError:
            raise ValidationError("Insert a decimal number")

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SelectTechnologyForm(FlaskForm):
    SelectTechnologyField = SelectField('Select Technology:', coerce=int)
    submit = SubmitField('apply')
    energy_capacity_Field = StringField('Energy Capacity', validators=[floatcheck])
    power_capacity_Field = StringField('Power Capacity', validators=[floatcheck])
    discharge_time_Field = SelectField('Discharge Time', coerce=int)
    response_time_Field = SelectField('Response Time', coerce=int)
    efficiency_Field = StringField('Round-Trip Efficiency', validators=[integercheck])
    gravimetric_power_density_Field = StringField('Gravimetric Power Density', validators=[floatcheck])
    volumetric_power_density_Field = StringField('Columetric Power Density', validators=[floatcheck])
    gravimetric_energy_density_Field = StringField('Gravimetric Energy Density', validators=[floatcheck])
    volumetric_energy_density_Field = StringField('Volumetric Energy Density', validators=[floatcheck])
    calendar_lifetime_Field = StringField('Calendar Lifetime', validators=[integercheck])
    cycle_lifetime_Field = StringField('Cycle Lifetime', validators=[integercheck])
    capital_cost_energyspecific_Field = StringField('Capital Cost Energy-Specific', validators=[floatcheck])
    capital_cost_powerspecific_Field = StringField('Capital Cost Power-Specific', validators=[floatcheck])
    lcoes_Field = StringField('Levelized Cost of Energy Storage', validators=[floatcheck])
    submitfilter = SubmitField('apply filter')


class CompareTechnologiesForm(FlaskForm):
    CompareTechnologiesField = MultiCheckboxField('Select Technologies to compare:', coerce=int, default=[1, 8])
    submit = SubmitField('compare')
    energy_capacity_Field = StringField('Energy Capacity', validators=[floatcheck])
    power_capacity_Field = StringField('Power Capacity', validators=[floatcheck])
    discharge_time_Field = SelectField('Discharge Time', coerce=int)
    response_time_Field = SelectField('Response Time', coerce=int)
    efficiency_Field = StringField('Round-Trip Efficiency', validators=[integercheck])
    gravimetric_power_density_Field = StringField('Gravimetric Power Density', validators=[floatcheck])
    volumetric_power_density_Field = StringField('Columetric Power Density', validators=[floatcheck])
    gravimetric_energy_density_Field = StringField('Gravimetric Energy Density', validators=[floatcheck])
    volumetric_energy_density_Field = StringField('Volumetric Energy Density', validators=[floatcheck])
    calendar_lifetime_Field = StringField('Calendar Lifetime', validators=[integercheck])
    cycle_lifetime_Field = StringField('Cycle Lifetime', validators=[integercheck])
    capital_cost_energyspecific_Field = StringField('Energy Specific Capital Cost', validators=[floatcheck])
    capital_cost_powerspecific_Field = StringField('Power Specific Capital Cost', validators=[floatcheck])
    lcoes_Field = StringField('Levelized Cost of Energy Storage', validators=[floatcheck])
    submitfilter = SubmitField('apply filter')






