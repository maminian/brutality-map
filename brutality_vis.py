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
excludes = load_data.excludes

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

df = load_data.df_cases
grouper = df.groupby(['City', 'State'])


# filter out counties that don't have any data
#keepers = np.zeros(county_names.shape, dtype=bool)
keepers = np.ones(county_names.shape, dtype=bool)
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
#    keepers[j] = True
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
    name=list(citystate_str[keepers]),
    count=list(instance_count[keepers]),
    media=list(instance_list[keepers]),
    has_hits=list(highlights[keepers]),
    descriptions=list(descriptions[keepers])
)
xy = np.array([load_data.latlon_lookup.get(n, (np.nan,np.nan)) for n in data['name']])
data['y'] = xy[:,0]
data['x'] = xy[:,1]
fudge = 0.5
power = 0.3
data['circle_radii'] = [fudge*c**power for c in data['count']]


#TOOLS = "wheel_zoom,reset,hover"
#TOOLS = "wheel_zoom,reset,tap"

# DISABLED HOVER FOR NOW
highlighty = bokeh.models.HoverTool(names=['moo'])
#tappy = bokeh.models.TapTool()

p = figure(
    title="Instances of police brutality during George Floyd protests", tools=[highlighty,'tap','wheel_zoom','reset'],
    x_axis_location=None, y_axis_location=None,
    tooltips=[
       ("City", "@name"), ("Recorded instances", "@count")
    ],
    plot_width=1000,
    plot_height=600,
    toolbar_location='below'
)

p.grid.grid_line_color = None

p.hover.point_policy = "follow_mouse"

brutality_cds = bokeh.models.ColumnDataSource(data)

thing = p.circle('x', 'y',
                source=brutality_cds,
                radius='circle_radii',
                fill_color={'field': 'count', 'transform': color_mapper},
                fill_alpha=1, selection_fill_alpha=1, nonselection_fill_alpha=1,
                selection_fill_color={'field': 'count', 'transform': color_mapper},
                nonselection_fill_color={'field': 'count', 'transform': color_mapper},
                line_width=3,
                line_color=None,
                selection_line_color='#000000',
                nonselection_line_color='#666666',
                name='moo')




######
#
# Now want to mimick
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/callbacks.html#customjs-for-user-interaction-events
#
# and generate a block of HTML that will dynamically update
# based on the thing clicked.
#
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

# Create HTML page with map on the left,
# dynamic list and links on the right.
layout=bokeh.layouts.row(p,div)

taptool = p.select(type=bokeh.models.TapTool)
taptool.callback=mooo


# TODO: draw static lines for state boundaries/counties; or
# use color to accentuate state boundaries and de-accentuate counties?


# Draw county/state boundaries...

state_cds = bokeh.models.ColumnDataSource({
    'state_xs': list( load_data.state_xs ),
    'state_ys': list( load_data.state_ys )
})
state_boundaries = bokeh.models.MultiLine(xs='state_xs', ys='state_ys', line_color='#333333', line_width=0.2)
p.add_glyph(state_cds, state_boundaries)


#county_cds = bokeh.models.ColumnDataSource({
#    'county_xs': list( load_data.county_xs ),
#    'county_ys': list( load_data.county_ys ),
#})


#county_boundaries = bokeh.models.MultiLine(xs='county_xs', ys='county_ys', line_color='#aaaaaa', line_width=0.1)
#p.add_glyph(county_cds, county_boundaries)

bokeh.io.show(layout)
