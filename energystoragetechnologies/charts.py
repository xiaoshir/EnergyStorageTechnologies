import pygal
from pygal import Config
from pygal.style import Style
import math
from energystoragetechnologies import db
from energystoragetechnologies.models import Technology, Source, Parameter

def drawfigure(techlist, par):
    config = Config()
    config.show_legend = False
    config.xrange = (0, len(techlist)+1)
    if len(techlist) > 5:
        config.truncate_label = 10
    elif len(techlist) > 3:
        config.truncate_label = 15
    else:
        config.truncate_label = 20
    config.human_readable = True
    config.dots_size = 7
    unit =Parameter.query.filter_by(name=par+'_min').first().unit
    config.y_title = par.replace('_', ' ') + unit
    #config.show_dots = False
    config.stroke_style = {'width': 50}
    config.style = pygal.style.styles['default'](label_font_size=12, stroke_opacity=1,
                                                stroke_opacity_hover=1, transition='100000000000s ease-in')
    if par == 'efficiency':
        config.range = (0, 100)

    xy_chart = pygal.XY(config)

    if par == 'discharge_time':
        xy_chart.y_labels = [
        {'label': 'milliseconds', 'value': 1},
        {'label': 'seconds', 'value': 2},
        {'label': 'minutes', 'value': 3},
        {'label': 'hours', 'value': 4},
        {'label': 'days', 'value': 5},
        {'label': 'weeks', 'value': 6},
        {'label': 'months', 'value': 7}]

    if par == 'response_time':
        xy_chart.y_labels = [
        {'label': 'milliseconds', 'value': 1},
        {'label': 'seconds', 'value': 2},
        {'label': 'minutes', 'value': 3}]
    dictlist = []
    ymin=100000000000
    ymax=0
    logscale=False
    for tech in techlist:
        if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_min").first().value != None:
            ymin = min(Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_min").first().value, ymin)
            ymax = max(Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_max").first().value, ymax)
    if (ymin*100) < ymax:
        xy_chart.logarithmic = True
        xy_chart.xrange = (0, 10**(len(techlist)+1))
        xy_chart.range = (10 ** int(math.floor(math.log10(ymin))), 10 ** (int(math.floor(math.log10(ymax))) + 1) + 1)
        logscale=True
    if logscale:
        i = 10
    else:
        i = 1
    for tech in techlist:
        minxlink=''
        maxxlink=''
        minlabel = ''
        maxlabel = ''
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=par + "_min").first().source_id).first() is not None:
            minxlink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=par + "_min").first().source_id).first().link
            minlabel = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=par + "_min").first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_min").first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=par + "_max").first().source_id).first() is not None:
            maxxlink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=par + "_max").first().source_id).first().link
            maxlabel = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=par + "_max").first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_max").first().source_id).first().releaseyear)
        xy_chart.add(f"{tech.name}", [
            {'value': (i, Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_min").first().value),
             'label': minlabel,
             'xlink': {'href': minxlink, 'target': '_blank'}},
            {'value': (i, Parameter.query.filter_by(technology_name=tech.name).filter_by(name=par + "_max").first().value),
             'label': maxlabel,
             'xlink': {'href': maxxlink, 'target': '_blank'}}])
        dictlist.append({
            'label': f"{tech.name}",
            'value': i})
        if logscale:
            i=i*10
        else:
            i=i+1
    xy_chart.x_labels = (dictlist)
    xy_chart.x_value_formatter = lambda x: ""
    xy_chart.render()
    return xy_chart.render_data_uri()


def drawdensityfigure(techlist, par):
    config = Config()
    config.show_legend = True
    config.human_readable = True
    config.dots_size = 3
    config.x_label_rotation=270
    config.legend_at_bottom=True
    if par == "gravimetric":
        power_unit="[W*kg]"
        energy_unit="[Wh/kg]"
    else:
        power_unit="[kW/m^3]"
        energy_unit="[kWh/m^3]"
    config.x_title = par + " power density " + power_unit
    config.y_title = par + " energy density " + energy_unit
    #config.show_dots = False
    config.logarithmic = True
    config.fill = True
    #config.show_minor_x_labels = False
    config.stroke_style = {'width': 1}
    config.style = pygal.style.styles['default'](label_font_size=12, stroke_opacity=0,
                                                stroke_opacity_hover=0, transition='100000000000s ease-in')
    xy_chart = pygal.XY(config)
    xmin=100
    ymin=100
    xmax=0.001
    ymax=0.001
    for tech in techlist:
        power_minstring = par+"_power_density_min"
        power_maxstring = par+"_power_density_max"
        energy_minstring = par+"_energy_density_min"
        energy_maxstring = par+"_energy_density_max"
        minpowerlink=''
        maxpowerlink=''
        minenergylink=''
        maxenergylink=''
        minpowerlabel = ''
        maxpowerlabel = ''
        minenergylabel = ''
        maxenergylabel = ''
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_minstring).first().source_id).first() is not None:
            minpowerlink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_minstring).first().source_id).first().link
            minpowerlabel = 'min. power density: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_minstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                    name=power_maxstring).first().source_id).first() is not None:
            maxpowerlink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                    name=power_maxstring).first().source_id).first().link
            maxpowerlabel = 'max. power density: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_maxstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_minstring).first().source_id).first() is not None:
            minenergylink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_minstring).first().source_id).first().link
            minenergylabel = 'min. energy density: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_minstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_maxstring).first().source_id).first() is not None:
            maxenergylink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_maxstring).first().source_id).first().link
            maxenergylabel = 'max. energy density: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_maxstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().source_id).first().releaseyear)
        xy_chart.add(f"{tech.name}", [
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value),
             'label': minenergylabel,
             'xlink': {'href': minenergylink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value),
             'label': minpowerlabel,
             'xlink': {'href': minpowerlink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value),
             'label': maxenergylabel,
             'xlink': {'href': maxenergylink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value),
             'label': maxpowerlabel,
             'xlink': {'href': maxpowerlink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value),
             'label': minenergylabel,
             'xlink': {'href': minenergylink, 'target': '_blank'}}])

        if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value is not None:
            xmin = min(xmin, Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value)
            xmax = max(xmax, Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value)
        if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value is not None:
            ymin = min(ymin, Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value)
            ymax = max(ymax, Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value)

    xy_chart.xrange = (10**int(math.floor(math.log10(xmin))), 10**(int(math.floor(math.log10(xmax)))+1)+1)
    xy_chart.range = (10**int(math.floor(math.log10(ymin))), 10**(int(math.floor(math.log10(ymax)))+1)+1)
    xy_chart.render()
    return xy_chart.render_data_uri()

def drawcapitalcostfigure(techlist):
    config = Config()
    config.show_legend = True
    config.human_readable = True
    config.dots_size = 3
    config.x_label_rotation=270
    config.legend_at_bottom=True
    config.x_title = "power specific capital cost  [$/kW]"
    config.y_title = "energy specific capital cost  [$/kWh]"
    #config.show_dots = False
    config.fill = True
    #config.show_minor_x_labels = False
    config.stroke_style = {'width': 1}
    config.style = pygal.style.styles['default'](label_font_size=12, stroke_opacity=0,
                                                stroke_opacity_hover=0, transition='100000000000s ease-in')
    xy_chart = pygal.XY(config)
    xmin=100000000
    ymin=100000000
    xmax=1
    ymax=1
    for tech in techlist:
        power_minstring = "capital_cost_powerspecific_min"
        power_maxstring = "capital_cost_powerspecific_max"
        energy_minstring = "capital_cost_energyspecific_min"
        energy_maxstring = "capital_cost_energyspecific_max"
        minpowerlink=''
        maxpowerlink=''
        minenergylink=''
        maxenergylink=''
        minpowerlabel=''
        maxpowerlabel=''
        minenergylabel=''
        maxenergylabel=''
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_minstring).first().source_id).first() is not None:
            minpowerlink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_minstring).first().source_id).first().link
            minpowerlabel = 'min. power specific capital cost: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_minstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                    name=power_maxstring).first().source_id).first() is not None:
            maxpowerlink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                    name=power_maxstring).first().source_id).first().link
            maxpowerlabel = 'max. power specific capital cost: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=power_maxstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_minstring).first().source_id).first() is not None:
            minenergylink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_minstring).first().source_id).first().link
            minenergylabel = 'min. energy specific capital cost: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_minstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().source_id).first().releaseyear)
        if Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_maxstring).first().source_id).first() is not None:
            maxenergylink = Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_maxstring).first().source_id).first().link
            maxenergylabel = 'max. energy specific capital cost: ' + Source.query.filter_by(id=Parameter.query.filter_by(technology_name=tech.name).filter_by(
                name=energy_maxstring).first().source_id).first().author + ', ' + str(Source.query.filter_by(
                id=Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().source_id).first().releaseyear)
        xy_chart.add(f"{tech.name}", [
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value),
             'label': minenergylabel,
             'xlink': {'href': minenergylink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value),
             'label': minpowerlabel,
             'xlink': {'href': minpowerlink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value),
             'label': maxenergylabel,
             'xlink': {'href': maxenergylink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value),
             'label': maxpowerlabel,
             'xlink': {'href': maxpowerlink, 'target': '_blank'}},
            {'value': (Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value,
                       Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value),
             'label': minenergylabel,
             'xlink': {'href': minenergylink, 'target': '_blank'}}])

        xmin = min(Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value
                   if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_minstring).first().value
                      is not None else xmin, xmin)
        xmax = min(Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value
                   if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=power_maxstring).first().value
                      is not None else xmax, xmax)
        ymin = min(Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value
                   if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_minstring).first().value
                      is not None else ymin, ymin)
        ymax = min(Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value
                   if Parameter.query.filter_by(technology_name=tech.name).filter_by(name=energy_maxstring).first().value
                      is not None else ymax, ymax)

        xup = 10**int(math.floor(math.log10(xmax)))
        yup = 10**int(math.floor(math.log10(ymax)))
        while xup < xmax:
            xup=xup+10**int(math.floor(math.log10(xmax)))
        while yup < ymax:
            yup=yup+10**int(math.floor(math.log10(ymax)))

        xy_chart.xrange = (10**int(math.floor(math.log10(xmin))), xup)
        xy_chart.range = (10**int(math.floor(math.log10(ymin))), yup)
    xy_chart.render()
    return xy_chart.render_data_uri()