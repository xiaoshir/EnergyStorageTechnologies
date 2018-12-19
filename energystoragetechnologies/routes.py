from flask import render_template, send_from_directory, current_app
from pathlib import Path
from energystoragetechnologies import app
from energystoragetechnologies.forms import SelectTechnologyForm, CompareTechnologiesForm
from energystoragetechnologies.models import Technology, Parameter, Source
from energystoragetechnologies.charts import drawfigure, drawdensityfigure, drawcapitalcostfigure, drawappplicationsfigure, drawcapitalcostcomponentsfigure
import os.path


# home route, shows home.html view
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


# about route, shows about.html view
@app.route("/about")
def about():
    return render_template('about.html', title='About')

def buildvaluedict(list, techname):
    outputdict={}
    for par in list:
        outputdict[par] = {
            'name': "round-trip efficiency" if par=="efficiency"
                    else "capital cost energy-specific" if par=="capital_cost_energyspecific"
                    else "capital cost power-specific" if par=="capital_cost_powerspecific"
                    else "LCOES*" if par=="LCOES"
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
    return outputdict

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
    applicationlist = ["any","frequency containment reserve (primary control)",
       "frequency restoration reserve (secondary control)", "replacement reserve (tertiary control)", "black start",
       "black start", "energy arbitrage", "grid investment deferral", "increase of self-consumption",
       "island operation", "load levelling", "mobility", "off grid applications", "peak shaving",
       "portable electronic applications", "power reliability", "renewable energy integration",
       "uninterrupted power supply", "voltage support"]
    form.applications_Field.choices = [(application, application) for application in applicationlist]
    stringfieldlist = ["energy_capacity", "power_capacity", "efficiency", "gravimetric_power_density",
                       "volumetric_power_density", "gravimetric_energy_density", "volumetric_energy_density",
                       "calendar_lifetime", "cycle_lifetime",
                       "capital_cost_energyspecific", "capital_cost_powerspecific", "LCOES"]
    selectfieldlist = ["discharge_time", "response_time"]
    # defaults
    nochoicealert = False
    techchoices = [t for t in Technology.query.order_by('id')]
    techname = techchoices[0].name
    lcoes_tool_link = "../uploads/LCOES_tool.xlsx"
    inventory_data_exists=False
    inventory_data_link = f"../uploads/inventory_data_{techname.replace(' ', '_')}.xlsx"
    if os.path.isfile(os.path.join(current_app.root_path, f"static/uploads/inventory_data_{techname.replace(' ', '_')}.xlsx")):
        inventory_data_exists = True
    techdescription = Technology.query.filter_by(name=techname).first().description
    techdiagram=Technology.query.filter_by(name=techname).first().diagram
    techdiagram_description=Technology.query.filter_by(name=techname).first().diagram_description
    techdiagram_source=f" ({Source.query.filter_by(id=Technology.query.filter_by(name=techname).first().diagram_source_id).first().author}, {Source.query.filter_by(id=Technology.query.filter_by(name=techname).first().diagram_source_id).first().releaseyear})."
    techdiagram_link=Source.query.filter_by(id=Technology.query.filter_by(name=techname).first().diagram_source_id).first().link
    applications=Technology.query.filter_by(name=techname).first().applications
    techparlist = ["energy_capacity", "power_capacity", "efficiency", "discharge_time", "response_time",
                   "gravimetric_power_density", "volumetric_power_density", "gravimetric_energy_density",
                   "volumetric_energy_density", "calendar_lifetime", "cycle_lifetime",]

    techvalues=buildvaluedict(techparlist, techname)
    economicparlist = ["capital_cost_energyspecific", "capital_cost_powerspecific", "capital_cost_of_energy_based_components", "capital_cost_of_power_based_components"]
    economicvalues = buildvaluedict(economicparlist, techname)
    environmentalparlist = []
    environmentalvalues = buildvaluedict(environmentalparlist, techname)
    #trying to get indendations in the drop down
    choicelist=[[t.id, t.name if t.level==1 else ". . . "+t.name if t.level==2 else ". . . . . . "+t.name] for t in techchoices]
    #form.SelectTechnologyField.choices = [(t.id, t.name) for t in techchoices]
    form.SelectTechnologyField.choices = [tuple(choice) for choice in choicelist]
    # what happens if user presses apply or filter
    if form.validate_on_submit():
        # remove choices that are filtered out
        for t in Technology.query.order_by('id'):
            for par in stringfieldlist:
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
            if form.applications_Field.data != "any":
                if t in techchoices:
                    if form.applications_Field.data not in t.applications:
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
        techdescription = Technology.query.filter_by(id=id).first().description
        techdiagram = Technology.query.filter_by(name=techname).first().diagram
        techdiagram_description = Technology.query.filter_by(name=techname).first().diagram_description
        techdiagram_source = f" ({Source.query.filter_by(id=Technology.query.filter_by(name=techname).first().diagram_source_id).first().author}, {Source.query.filter_by(id=Technology.query.filter_by(name=techname).first().diagram_source_id).first().releaseyear})."
        techdiagram_link = Source.query.filter_by(id=Technology.query.filter_by(name=techname).first().diagram_source_id).first().link
        applications = Technology.query.filter_by(name=techname).first().applications
        techparlist = ["energy_capacity", "power_capacity", "efficiency", "discharge_time", "response_time",
                       "gravimetric_power_density", "volumetric_power_density", "gravimetric_energy_density",
                       "volumetric_energy_density", "calendar_lifetime", "cycle_lifetime", ]

        techvalues = buildvaluedict(techparlist, techname)
        economicparlist = ["capital_cost_energyspecific", "capital_cost_powerspecific", "capital_cost_of_energy_based_components", "capital_cost_of_power_based_components"]
        economicvalues = buildvaluedict(economicparlist, techname)
        environmentalparlist = []
        environmentalvalues = buildvaluedict(environmentalparlist, techname)
        inventory_data_link = f"/uploads/inventory_data_{techname.replace(' ', '_')}.xlsx"
        if os.path.isfile(os.path.join(current_app.root_path,
                                       f"static/uploads/inventory_data_{techname.replace(' ', '_')}.xlsx")):
            inventory_data_exists = True
    # render HTML
    return render_template('technologyinformation.html',
                           title='Technology Information',
                           form=form,
                           techvalues=techvalues,
                           economicvalues=economicvalues,
                           environmentalvalues=environmentalvalues,
                           discharge_time_converter=discharge_time_converter,
                           response_time_converter=response_time_converter,
                           techname=techname,
                           techdescription=techdescription,
                           techdiagram=techdiagram,
                           techdiagram_description=techdiagram_description,
                           techdiagram_source=techdiagram_source,
                           techdiagram_link=techdiagram_link,
                           applications=applications,
                           nochoicealert=nochoicealert,
                           inventory_data_link=inventory_data_link,
                           inventory_data_exists=inventory_data_exists)


# function that orders the choiceslist such that specific technologies are placed below their generic "parent" technology
def orderchoices(techchoices):
    caeslist = []
    pheslist = []
    batterieslist = []
    otherslist = []
    levellist = []
    emptypositions=[]
    for tech in techchoices:
        if "CAES" in tech.name:
            caeslist.append(tech)
        elif "PHES" in tech.name:
            pheslist.append(tech)
        elif "Battery" in tech.name or "Batteries" in tech.name:
            batterieslist.append(tech)
        else:
            otherslist.append(tech)
    batteriescount=0
    caescount=0
    phescount=0
    otherscount = 0
    orderedchoices = []
    i = 0
    while batteriescount < len(batterieslist) or caescount < len(caeslist) or phescount < len(pheslist) or \
            otherscount < len(otherslist):
        if len(batterieslist)>0:
            if i % 2 == 0:
                if batteriescount < len(batterieslist):
                    orderedchoices.append(batterieslist[batteriescount])
                    levellist.append(batterieslist[batteriescount].level)
                    batteriescount = batteriescount + 1
                else:
                    orderedchoices.append(otherslist[otherscount])
                    levellist.append(otherslist[otherscount].level)
                    otherscount = otherscount + 1
            else:
                if phescount < len(pheslist):
                    orderedchoices.append(pheslist[phescount])
                    levellist.append(pheslist[phescount].level)
                    phescount = phescount + 1
                elif caescount < len(caeslist):
                    orderedchoices.append(caeslist[caescount])
                    levellist.append(caeslist[caescount].level)
                    caescount = caescount + 1
                elif otherscount < len(otherslist):
                    orderedchoices.append(otherslist[otherscount])
                    levellist.append(otherslist[otherscount].level)
                    otherscount = otherscount + 1
                else:
                    levellist.append(0)
                    emptypositions.append(i)
            i = i + 1
        elif len(caeslist)>0:
            if i % 2 == 0:
                if caescount < len(caeslist):
                    orderedchoices.append(caeslist[caescount])
                    levellist.append(caeslist[caescount].level)
                    caescount = caescount + 1
                else:
                    orderedchoices.append(otherslist[otherscount])
                    levellist.append(otherslist[otherscount].level)
                    otherscount = otherscount + 1
            else:
                if phescount < len(pheslist):
                    orderedchoices.append(pheslist[phescount])
                    levellist.append(pheslist[phescount].level)
                    phescount = phescount + 1
                elif otherscount < len(otherslist):
                    orderedchoices.append(otherslist[otherscount])
                    levellist.append(otherslist[otherscount].level)
                    otherscount = otherscount + 1
                else:
                    levellist.append(0)
                    emptypositions.append(i)
            i = i + 1
        else:
            if i % 2 == 0:
                if phescount < len(pheslist):
                    orderedchoices.append(pheslist[phescount])
                    levellist.append(pheslist[phescount].id)
                    phescount = phescount + 1
                else:
                    orderedchoices.append(otherslist[otherscount])
                    levellist.append(otherslist[otherscount].id)
                    otherscount = otherscount + 1
            else:
                if otherscount < len(otherslist):
                    orderedchoices.append(otherslist[otherscount])
                    levellist.append(otherslist[otherscount].id)
                    otherscount = otherscount + 1
                else:
                    levellist.append(0)
                    emptypositions.append(i)

            i = i + 1
    return {'orderedchoices': orderedchoices, 'levellist': levellist, 'emptypositions': emptypositions}


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
    applicationlist = ["any","frequency containment reserve (primary control)",
       "frequency restoration reserve (secondary control)", "replacement reserve (tertiary control)", "black start",
       "energy arbitrage", "grid investment deferral", "increase of self-consumption",
       "island operation", "load levelling", "mobility", "off grid applications", "peak shaving",
       "portable electronic applications", "power reliability", "renewable energy integration",
       "uninterrupted power supply", "voltage support"]
    form.applications_Field.choices = [(application, application) for application in applicationlist]
    stringfieldlist = ["energy_capacity", "power_capacity", "efficiency", "gravimetric_power_density",
                       "volumetric_power_density", "gravimetric_energy_density", "volumetric_energy_density",
                       "capital_cost_energyspecific", "capital_cost_powerspecific", "LCOES"]
    selectfieldlist = ["discharge_time", "response_time"]
    # defaults
    orderedidlist=[]
    notechalert=False
    nochoicealert=False
    #form.CompareTechnologiesField.data = [12, 19]
    techlist = [Technology.query.filter_by(name="Batteries").first(),
                Technology.query.filter_by(name="Pumped Hydro Energy Storage (PHES)").first()]
    # order choices
    techchoices = [t for t in Technology.query.order_by('id')]
    orderedchoices=orderchoices(techchoices)['orderedchoices']
    # generate list of choices
    form.CompareTechnologiesField.choices=[(t.id, t.name) for t in orderedchoices]
    orderedchoiceslistwithoutempty = list(form.CompareTechnologiesField)
    emptypositions = orderchoices(techchoices)['emptypositions']
    orderedchoiceslist=[]
    k=0
    for i in range(len(orderedchoices)+len(emptypositions)):
        if i in emptypositions:
            orderedchoiceslist.append('empty')
        else:
            orderedchoiceslist.append(orderedchoiceslistwithoutempty[k])
            k=k+1
    levellist = orderchoices(techchoices)['levellist']
    # draw charts
    applications_fig = drawappplicationsfigure(techlist, applicationlist)
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
    capital_cost_components_fig = drawcapitalcostcomponentsfigure(techlist)
    lcoes_fig = drawfigure(techlist, "LCOES")
    greenhousegas_fig = drawfigure(techlist, "life_cycle_greenhouse_gas_emissions")
    # what happens if user klicks on compare or filter
    if form.validate_on_submit():
        # remove choices that are filtered out
        for t in Technology.query.order_by('id'):
            for par in stringfieldlist:
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
            if form.applications_Field.data != "any":
                if t in techchoices:
                    if form.applications_Field.data not in t.applications:
                        techchoices.remove(t)
        if not form.CompareTechnologiesField.data:
            notechalert=True
        # generate list of choices
        orderedchoices = orderchoices(techchoices)['orderedchoices']
        form.CompareTechnologiesField.choices = [(t.id, t.name) for t in orderedchoices]
        orderedchoiceslistwithoutempty = list(form.CompareTechnologiesField)
        emptypositions = orderchoices(techchoices)['emptypositions']
        orderedchoiceslist = []
        k = 0
        for i in range(len(orderedchoices) + len(emptypositions)):
            if i in emptypositions:
                orderedchoiceslist.append('empty')
            else:
                orderedchoiceslist.append(orderedchoiceslistwithoutempty[k])
                k = k + 1
        levellist = orderchoices(techchoices)['levellist']
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
        # build list of technologies that will be compared
        idlist = form.CompareTechnologiesField.data
        techlist = []
        for id in idlist:
            techlist.append(Technology.query.filter_by(id=id).first())
        if not notechalert:
            if not nochoicealert:
                # draw charts
                applications_fig = drawappplicationsfigure(techlist, applicationlist)
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
                capital_cost_components_fig=drawcapitalcostcomponentsfigure(techlist)
                lcoes_fig = drawfigure(techlist, "LCOES")
                greenhousegas_fig = drawfigure(techlist, "life_cycle_greenhouse_gas_emissions")

    return render_template('technologycomparison.html',
                           title='Technology Comparison',
                           form=form,
                           applications_fig=applications_fig,
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
                           capital_cost_components_fig=capital_cost_components_fig,
                           greenhousegas_fig=greenhousegas_fig,
                           lcoes_fig=lcoes_fig,
                           orderedchoiceslist=orderedchoiceslist,
                           notechalert=notechalert,
                           nochoicealert=nochoicealert,
                           techlist=techlist,
                           applicationlist=applicationlist,
                           levellist=levellist)


#route used for download of excel sheets
@app.route('/uploads/<path:filename>')
def download_file(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)
