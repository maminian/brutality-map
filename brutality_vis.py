# via https://docs.bokeh.org/en/latest/docs/gallery/texas.html?highlight=texas

import bokeh
from bokeh.io import show
from bokeh.models import LinearColorMapper
from bokeh.palettes import Purples4
from bokeh.plotting import figure

from bokeh.models.callbacks import CustomJS

import numpy as np

###
import load_data

# my modification - if sample data not downloaded, do it.
try:
    # from bokeh.sampledata.unemployment import data as unemployment
    from bokeh.sampledata.us_counties import data as counties
except:
    raise Exception('could not import data sets; run bokeh.sampledata.download() then re-run script.')
#

palette = list(reversed(Purples4))
# make zero cases show up as white... purples colormap ends in an off-white.
palette[0] = '#ffffff'
palette = tuple(palette)
#palette = Purples6

# lower 48 plus dc for now
excludes = ['ak', 'hi', 'pr', 'mp', 'vi', 'as', 'gu']

# filter to selected states/entities
counties = {
    code: county for code, county in counties.items() if county["state"] not in excludes
}


county_xs = np.array([county["lons"] for county in counties.values()])
county_ys = np.array([county["lats"] for county in counties.values()])

county_names = np.array( [county['name'] for county in counties.values()] )
citystates = np.array( [(county['name'].lower(),county['state'].lower()) for key,county in counties.items()] )
citystate_str = np.array([', '.join(cs) for cs in citystates])
#county2id = {cs:key for key,county in counties.items() }
citystates = []
county2id = {}
cs2idx = {}
for j,(key,county) in enumerate(counties.items()):
    citystate = (county['name'].lower(), county['state'].lower())
    county2id[citystate] = key
    citystates.append(citystate)
    cs2idx[citystate] = j
#

# county_rates = [unemployment[county_id] for county_id in counties]
# county_rates = []
# for county_id in counties:
#     county_rates.append( unemployment.get(county_id, np.nan) )

df = load_data.df_cases
grouper = df.groupby(['City', 'State'])


# filter out counties that don't have any data
keepers = np.zeros(county_names.shape, dtype=bool)
#keepers = np.ones(county_names.shape, dtype=bool)
highlights = np.array(['#aaaaaa' for _ in county_names])

descriptions=[[] for _ in county_names]

instance_count = np.zeros(county_names.shape)
instance_list = [[] for _ in instance_count]
for (location, df_sub) in grouper:
    # TODO: get info on counties for cities.
    if location not in cs2idx:
        print(location)
        continue
    j = cs2idx[location]
    keepers[j] = True
    highlights[j] = '#000000'
    instance_list[j] = list( df_sub['Tweet URL'].values )
    instance_count[j] = df_sub.shape[0]
    descriptions[j] = list( df_sub['Description'].values )
#
instance_list = np.array(instance_list)
descriptions = np.array(descriptions) # why do i go from array to list to array to list...
#

color_mapper = LinearColorMapper(palette=palette, low=0, high=4)

data=dict(
    x=list(county_xs[keepers]),
    y=list(county_ys[keepers]),
    name=list(citystate_str[keepers]),
    count=list(instance_count[keepers]),
    media=list(instance_list[keepers]),
    has_hits=list(highlights[keepers]),
    descriptions=list(descriptions[keepers])
)

#TOOLS = "wheel_zoom,reset,hover"
#TOOLS = "wheel_zoom,reset,tap"

# DISABLED HOVER FOR NOW
highlighty = bokeh.models.HoverTool(names=['moo'])
#tappy = bokeh.models.TapTool()

p = figure(
    title="Instances of police brutality during George Floyd protests", tools=[highlighty,'tap'],
    x_axis_location=None, y_axis_location=None,
    tooltips=[
       ("Name", "@name"), ("Count", "@count")
    ],
    plot_width=1000,
    plot_height=600,
    toolbar_location='below'
)
#
# polysel = bokeh.models.PolySelectTool(
#     source=bokeh.models.ColumnDataSource(data),
#     tooltips=[
#        ("Name", "@name"), ("Count", "@count"), ("Links", "@media")
#     ],
# )
#p.add_tools(polysel)
#p.toolbar.active_tap = polysel

# g1_r = p.add_glyph(
#     bokeh.models.ColumnDataSource(data)
# )
# g1_hover = bokeh.models.HoverTool(renderers=[g1_r],
#                          tooltips=[('x', '@col1'), ('y', '@col2')])

xmin = min(county_xs.min())
xmax = max(county_xs.max())
ymin = min(county_ys.min())
ymax = max(county_ys.max())
#p.line([xmin,xmin,xmax,xmax,xmin],[ymin,ymax,ymax,ymin,ymin])

p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"

# TODO: Change to on-click ()

brutality_cds = bokeh.models.ColumnDataSource(data)

thing = p.patches('x', 'y',
            source=brutality_cds,
            fill_color={'field': 'count', 'transform': color_mapper},
            fill_alpha=1, line_color='has_hits', line_width=0.2, name='moo')

# TODO: taptool to open twitter links as a list on another
# side pane or something?


# TODO: draw static lines for state boundaries only; or
# use color to accentuate state boundaries and de-accentuate counties?

# ugh... why does it have to be this way
cds = bokeh.models.ColumnDataSource({
    'xs': list( county_xs[np.logical_not(keepers)] ),
    'ys': list( county_ys[np.logical_not(keepers)] )
})

# Now want to mimick
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/callbacks.html#customjs-for-user-interaction-events
div = bokeh.models.Div(width=400, height=p.plot_height, height_policy="fixed")

mooo = CustomJS(args=dict(dat=brutality_cds, page=div), code='''
var idx = dat.selected.indices[0];
var name = dat["data"]["name"][idx];
var links = dat["data"]["media"][idx];
var descrs = dat["data"]["descriptions"][idx];
var nlinks = links.length;
console.log(links)

var header="<h1 class=\'city\'>Videos for "+name+"</h1>";

var myul="<ul class=\'media_list\'>";
for (var i=0; i<nlinks; i++){
    var linky=links[i];
    myul += "<li><font class=\'brutality_descr\'>" + descrs[i] + "</font><br/>";
    myul += "<a href=\'"+linky+"\' target=_blank>" + linky + "</a>\\n";
}
myul += "</ul>\\n"

page.text = header+myul;
console.log(page.text)
'''
)

layout=bokeh.layouts.row(p,div)

# var myul="<ul class=\"media_list\">";
# for (var i=0; i<nlinks; i++){
#     var linky=links[i];
#     myul += "<li> <a href=\""+linky+"\">" + linky + "</a>\\n";
# }
# myul += "</ul>\\n"
#
# div.text = header+myul;

# mooo = CustomJS(args=dict(dat=brutality_cds), code='''
# var idx=dat.selected.indices[0];
# var name=dat["data"]["name"][idx];
# var links=dat["data"]["media"][idx];
# var nlinks=links.length;
#
# console.log(idx);
# console.log(name);
# console.log(links);
# console.log(nlinks);
#
# console.log("Selected city: " + name);
# for (var i=0; i<nlinks; i++){
#     var linky=links[i];
#     console.log( linky );
# }
# '''
# )

# console.log("Selected city: " + dat[idx]['Name'] + "\n")
# console.log('Links to media:')
# console.log(dat[idx].Links)


#thing.data_source.on_change('selected', mooo)
#brutality_cds.selected.js_on_change()
#bokeh.io.curdoc().add_root(p)

taptool = p.select(type=bokeh.models.TapTool)
taptool.callback=mooo


empty_county_ml = bokeh.models.MultiLine(xs='xs', ys='ys', line_color='#aaaaaa', line_width=0.1)

p.add_glyph(cds,empty_county_ml)

bokeh.io.show(layout)
