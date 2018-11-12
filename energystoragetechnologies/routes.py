from flask import render_template, url_for, redirect
from energystoragetechnologies import app
from energystoragetechnologies.forms import SelectTechnologyForm, CompareTechnologiesForm
from energystoragetechnologies.models import Technology, Parameter, Source
from energystoragetechnologies.charts import drawfigure, drawdensityfigure, drawcapitalcostfigure


# home route, shows home.html view
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


# about route, shows contactus.html view
@app.route("/contactus")
def about():
    return render_template('contactus.html', title='Contact Us')


# Technology information route, shows technologyinformation.html view
@app.route("/technologyinformation", methods=['GET', 'POST'])
def technologyinformation():
    form = SelectTechnologyForm()
    # definitions for filter
    discharge_time_converter = {
        0: "any",
        1: "milliseconds",
        2: "seconds",
        3: "minutes",
        4: "hours",
        5: "days",
        6: "weeks",
        7: "months",
    }
    response_time_converter = {
        0: "any",
        1: "milliseconds",
        2: "seconds",
        3: "minutes",
    }
    form.discharge_time_Field.choices = discharge_time_converter.items()
    form.response_time_Field.choices = response_time_converter.items()
    stringfieldlist = ["energy_capacity", "power_capacity", "efficiency", "gravimetric_power_density",
                       "volumetric_power_density", "gravimetric_energy_density", "volumetric_energy_density",
                       "calendar_lifetime", "cycle_lifetime",
                       "capital_cost_energyspecific", "capital_cost_powerspecific", "lcoes"]
    selectfieldlist = ["discharge_time", "response_time"]
    # defaults
    nochoicealert=False
    techchoices = [t for t in Technology.query.order_by('id')]
    techvalues = {}
    economicvalues = {}
    techname = techchoices[0].name
    techparlist = ["energy_capacity", "power_capacity", "efficiency", "discharge_time", "response_time",
                   "gravimetric_power_density", "volumetric_power_density", "gravimetric_energy_density",
                   "volumetric_energy_density", "calendar_lifetime", "cycle_lifetime",]
    for par in techparlist:
        techvalues[par] = {
            'name': "round-trip efficiency" if par=="efficiency"
                    else "capital cost energy-specific" if par=="capital_cost_energyspecific"
                    else "capital cost power-specific" if par=="capital_cost_powerspecific"
                    else par.replace('_', ' '),
            'min': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value is None
             else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value
            if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value,
                int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)
                if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value.is_integer()
                else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)),
            'minsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                name=par + "_min").first().source_id).first(),
            'max': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value is None
             else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value
            if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value,
                int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)
                if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value.is_integer()
                else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)),
            'maxsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                name=par + "_max").first().source_id).first(),
            'unit': Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().unit
        }
    economicparlist = ["capital_cost_energyspecific", "capital_cost_powerspecific", "lcoes"]
    for par in economicparlist:
        economicvalues[par] = {
            'name': "round-trip efficiency" if par=="efficiency"
                    else "capital cost energy-specific" if par=="capital_cost_energyspecific"
                    else "capital cost power-specific" if par=="capital_cost_powerspecific"
                    else par.replace('_', ' '),
            'min': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value is None
             else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value
            if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value,
                int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)
            if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value.is_integer()
            else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)),
            'minsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                name=par + "_min").first().source_id).first(),
            'max': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value is None
             else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value
            if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value,
                int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)
            if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value.is_integer()
            else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)),
            'maxsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                name=par + "_max").first().source_id).first(),
            'unit': Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().unit
        }
    #trying to get indendations in the drop down
    choicelist=[[t.id, t.name if t.level==1 else ". . . "+t.name if t.level==2 else ". . . . . . "+t.name] for t in techchoices]
    #form.SelectTechnologyField.choices = [(t.id, t.name) for t in techchoices]
    form.SelectTechnologyField.choices = [tuple(choice) for choice in choicelist]
    # what happens if user presses apply or filter
    if form.validate_on_submit():
        # remove choices that are filtered out
        for par in stringfieldlist:
            for t in Technology.query.order_by('id'):
                if t in techchoices:
                    if getattr(getattr(form, par + "_Field"), "data") != "":
                        if Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value is None:
                            techchoices.remove(t)
                        else:
                            if (float(getattr(getattr(form, par + "_Field"), "data")) <
                                Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value) or (
                                    float(getattr(getattr(form, par + "_Field"), "data")) >
                                    Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_max").first().value):
                                techchoices.remove(t)
        for par in selectfieldlist:
            for t in Technology.query.order_by('id'):
                if t in techchoices:
                    if getattr(getattr(form, par + "_Field"), "data") != 0:
                        if Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value is None:
                            techchoices.remove(t)
                        else:
                            if (getattr(getattr(form, par + "_Field"), "data") <
                                Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value) or (
                                    getattr(getattr(form, par + "_Field"), "data") >
                                    Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_max").first().value):
                                techchoices.remove(t)
        if len(techchoices)==0:
            nochoicealert=True
            choicelist = [[t.id, t.name if t.level == 1 else ". . . " + t.name if t.level == 2 else ". . . . . . " + t.name]
                          for t in Technology.query.order_by('id')]
        else:
            # trying to get indendations in the drop down
            choicelist = [[t.id, t.name if t.level == 1 else ". . . " + t.name if t.level == 2 else ". . . . . . " + t.name]
                          for t in techchoices]
        # form.SelectTechnologyField.choices = [(t.id, t.name) for t in techchoices]
        form.SelectTechnologyField.choices = [tuple(choice) for choice in choicelist]
        # build dictionary to render template
        id = form.SelectTechnologyField.data
        techname = Technology.query.filter_by(id=id).first().name
        techparlist=["energy_capacity", "power_capacity", "efficiency", "discharge_time", "response_time",
                     "gravimetric_power_density", "volumetric_power_density", "gravimetric_energy_density",
                     "volumetric_energy_density"]
        for par in techparlist:
            techvalues[par] = {
                'name': "round-trip efficiency" if par == "efficiency"
                else "capital cost energy-specific" if par == "capital_cost_energyspecific"
                else "capital cost power-specific" if par == "capital_cost_powerspecific"
                else par.replace('_', ' '),
                'min': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value is None
                else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value
                if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value,
                    int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)
                if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value.is_integer()
                else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)),
                'minsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                    name=par+"_min").first().source_id).first(),
                'max': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value is None
             else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value
                if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value,
                    int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)
                if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value.is_integer()
                else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)),
                'maxsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                    name=par + "_max").first().source_id).first(),
                'unit': Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().unit
            }
        economicparlist=["capital_cost_energyspecific", "capital_cost_powerspecific", "lcoes"]
        for par in economicparlist:
            economicvalues[par] = {
                'name': "round-trip efficiency" if par == "efficiency"
                else "capital cost energy-specific" if par == "capital_cost_energyspecific"
                else "capital cost power-specific" if par == "capital_cost_powerspecific"
                else par.replace('_', ' '),
                'min': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value is None
                else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value
                if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value,
                    int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)
                    if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value.is_integer()
                    else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().value)),
                'minsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                    name=par+"_min").first().source_id).first(),
                'max': "No data" if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value is None
             else (Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value
                if isinstance(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value,
                    int) else (int(Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)
                    if Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value.is_integer()
                    else Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_max").first().value)),
                'maxsource': Source.query.filter_by(id=Parameter.query.filter_by(technology_name=techname).filter_by(
                    name=par + "_max").first().source_id).first(),
                'unit': Parameter.query.filter_by(technology_name=techname).filter_by(name=par + "_min").first().unit
            }
    # render HTML
    return render_template('technologyinformation.html',
                           title='Technology Information',
                           form=form,
                           techvalues=techvalues,
                           economicvalues=economicvalues,
                           discharge_time_converter=discharge_time_converter,
                           response_time_converter=response_time_converter,
                           techname=techname,
                           nochoicealert=nochoicealert)


# function that orders the choiceslist such that specific technologies are placed below their generic "parent" technology
def orderlist(choicelist):
    caeslist = []
    pheslist = []
    otherslist = []
    for choice in choicelist:
        if "CAES" in str(choice.label):
            caeslist.append(choice)
        elif "PHES" in str(choice.label):
            pheslist.append(choice)
        else:
            otherslist.append(choice)
    if len(caeslist) > len(pheslist):
        largerlist = caeslist
        smallerlist = pheslist
    else:
        largerlist = pheslist
        smallerlist = caeslist
    largercount = 0
    smallercount = 0
    otherscount = 0
    orderedchoiceslist = []
    i = 0
    while largercount < len(largerlist) or smallercount < len(smallerlist) or otherscount < len(otherslist):
        if i % 2 == 0:
            if largercount < len(largerlist):
                orderedchoiceslist.append(largerlist[largercount])
                largercount = largercount + 1
            else:
                orderedchoiceslist.append(otherslist[otherscount])
                otherscount = otherscount + 1
        else:
            if smallercount < len(smallerlist):
                orderedchoiceslist.append(smallerlist[smallercount])
                smallercount = smallercount + 1
            elif otherscount < len(otherslist):
                orderedchoiceslist.append(otherslist[otherscount])
                otherscount = otherscount + 1
            else:
                orderedchoiceslist.append("empty")
        i = i + 1
    return orderedchoiceslist


# Technology comparison route, shows technologycomparison.html view
@app.route("/technologycomparison", methods=['GET', 'POST'])
def technologycomparison():
    form = CompareTechnologiesForm()
    # definitions for filter
    discharge_time_converter = {
        0: "any",
        1: "milliseconds",
        2: "seconds",
        3: "minutes",
        4: "hours",
        5: "days",
        6: "weeks",
        7: "months",
    }
    response_time_converter = {
        0: "any",
        1: "milliseconds",
        2: "seconds",
        3: "minutes",
    }
    form.discharge_time_Field.choices = discharge_time_converter.items()
    form.response_time_Field.choices = response_time_converter.items()
    stringfieldlist = ["energy_capacity", "power_capacity", "efficiency", "gravimetric_power_density",
                       "volumetric_power_density", "gravimetric_energy_density", "volumetric_energy_density",
                       "capital_cost_energyspecific", "capital_cost_powerspecific", "lcoes"]
    selectfieldlist = ["discharge_time", "response_time"]
    # defaults
    notechalert=False
    nochoicealert=False
    techchoices = [t for t in Technology.query.order_by('id')]
    #form.CompareTechnologiesField.data = [12, 19]
    techlist = [Technology.query.filter_by(name="Pumped Hydro Energy Storage (PHES)").first(), Technology.query.filter_by(name="Compressed Air Energy Storage (CAES)").first()]
    # generate list of choices
    form.CompareTechnologiesField.choices = [(t.id, t.name) for t in techchoices]
    choicelist = list(form.CompareTechnologiesField)
    # order the lit
    orderedchoiceslist = orderlist(choicelist)
    # draw charts
    energy_capacity_fig = drawfigure(techlist, "energy_capacity")
    power_capacity_fig = drawfigure(techlist, "power_capacity")
    discharge_time_fig = drawfigure(techlist, "discharge_time")
    response_time_fig = drawfigure(techlist, "response_time")
    efficiency_fig = drawfigure(techlist, "efficiency")
    gravimetric_density_fig = drawdensityfigure(techlist, "gravimetric")
    volumetric_density_fig = drawdensityfigure(techlist, "volumetric")
    calendar_lifetime_fig = drawfigure(techlist, "calendar_lifetime")
    cycle_lifetime_fig = drawfigure(techlist, "cycle_lifetime")
    capital_cost_fig = drawcapitalcostfigure(techlist)
    lcoes_fig = drawfigure(techlist, "lcoes")
    # what happens if user klicks on compare or filter
    if form.validate_on_submit():
        # remove choices that are filtered out
        for par in stringfieldlist:
            for t in Technology.query.order_by('id'):
                if t in techchoices:
                    if getattr(getattr(form, par + "_Field"), "data") != "":
                        if Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value is None:
                            techchoices.remove(t)
                        else:
                            if (float(getattr(getattr(form, par + "_Field"), "data")) <
                                Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value) or (
                                    float(getattr(getattr(form, par + "_Field"), "data")) >
                                    Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_max").first().value):
                                techchoices.remove(t)
        for par in selectfieldlist:
            for t in Technology.query.order_by('id'):
                if t in techchoices:
                    if getattr(getattr(form, par + "_Field"), "data") != 0:
                        if Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value is None:
                            techchoices.remove(t)
                        else:
                            if (getattr(getattr(form, par + "_Field"), "data") <
                                Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_min").first().value) or (
                                    getattr(getattr(form, par + "_Field"), "data") >
                                    Parameter.query.filter_by(technology_name=t.name).filter_by(name=par+"_max").first().value):
                                techchoices.remove(t)
        if not form.CompareTechnologiesField.data:
            notechalert=True
        # generate list of choices
        form.CompareTechnologiesField.choices = [(t.id, t.name) for t in techchoices]
        if form.submitfilter.data:
            #set default choice(s)
            form.CompareTechnologiesField.data = []
            if (1, "Pumped Hydro Energy Storage (PHES)") in form.CompareTechnologiesField.choices:
                form.CompareTechnologiesField.data.append(1)
            if (8, "Compressed Air Energy Storage (CAES)") in form.CompareTechnologiesField.choices:
                form.CompareTechnologiesField.data.append(8)
            if ((1, "Pumped Hydro Energy Storage (PHES)") not in form.CompareTechnologiesField.choices and
                    (8, "Compressed Air Energy Storage (CAES)") not in form.CompareTechnologiesField.choices):
                if len(techchoices)==0:
                    nochoicealert=True
                else:
                    form.CompareTechnologiesField.data.append(techchoices[0].id)

            notechalert=False
        #convert choices to list
        choicelist = list(form.CompareTechnologiesField)
        # order the list
        orderedchoiceslist = orderlist(choicelist)
        # build list of technologies that will be compared
        idlist = form.CompareTechnologiesField.data
        techlist = []
        for id in idlist:
            techlist.append(Technology.query.filter_by(id=id).first())
        if not notechalert:
            if not nochoicealert:
                # draw charts
                energy_capacity_fig = drawfigure(techlist, "energy_capacity")
                power_capacity_fig = drawfigure(techlist, "power_capacity")
                discharge_time_fig = drawfigure(techlist, "discharge_time")
                response_time_fig = drawfigure(techlist, "response_time")
                efficiency_fig = drawfigure(techlist, "efficiency")
                gravimetric_density_fig = drawdensityfigure(techlist, "gravimetric")
                volumetric_density_fig = drawdensityfigure(techlist, "volumetric")
                calendar_lifetime_fig = drawfigure(techlist, "calendar_lifetime")
                cycle_lifetime_fig = drawfigure(techlist, "cycle_lifetime")
                capital_cost_fig = drawcapitalcostfigure(techlist)
                lcoes_fig = drawfigure(techlist, "lcoes")
    return render_template('technologycomparison.html',
                           title='Technology Comparison',
                           form=form,
                           energy_capacity_fig=energy_capacity_fig,
                           power_capacity_fig=power_capacity_fig,
                           discharge_time_fig=discharge_time_fig,
                           response_time_fig=response_time_fig,
                           efficiency_fig=efficiency_fig,
                           gravimetric_density_fig=gravimetric_density_fig,
                           volumetric_density_fig=volumetric_density_fig,
                           calendar_lifetime_fig=calendar_lifetime_fig,
                           cycle_lifetime_fig=cycle_lifetime_fig,
                           capital_cost_fig=capital_cost_fig,
                           lcoes_fig=lcoes_fig,
                           orderedchoiceslist=orderedchoiceslist,
                           notechalert=notechalert,
                           nochoicealert=nochoicealert)
