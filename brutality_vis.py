import bokeh

from bokeh.io import show
from bokeh.models import LinearColorMapper
from bokeh.palettes import Purples8 as palette
from bokeh.plotting import figure

from bokeh.models.callbacks import CustomJS

import numpy as np


####
# resource links
tweet_number_one = 'https://twitter.com/greg_doucette/status/1266752393556918273'
spreadsheet_link = 'https://docs.google.com/spreadsheets/d/1YmZeSxpz52qT-10tkCjWOwOGkQqle7Wd1P7ZM1wMW0E/edit#gid=0'

####
# timestamp
import datetime
import pytz
dt = pytz.datetime.datetime.now( pytz.timezone('US/Mountain') )
dt_str = dt.strftime('%H:%M %Z, %B %d, %Y')

####
# file to export
bokeh.plotting.output_file('index.html', title='Police Brutality Map')

###
import load_data

# my modification - if sample data not downloaded, do it.
try:
    from bokeh.sampledata.us_counties import data as counties
except:
    raise Exception('could not import data sets; run bokeh.sampledata.download() then re-run script.')
#

palette = list(reversed(palette))

#palette[0] = '#ffffff'
palette = tuple(palette)


# lower 48 plus dc for now
excludes = load_data.excludes

#

df = load_data.df_cases
grouper = df.groupby(['City', 'State'])

descriptions=[]

location_name = []
instance_count = []
instance_list = []
for (location, df_sub) in grouper:
    location_name.append( ', '.join(location) )
    instance_list.append( list( df_sub['Tweet URL'].values ) )
    instance_count.append( df_sub.shape[0] )
    descriptions.append( list(df_sub['Description'].values) )
#
instance_list = np.array(instance_list)
descriptions = np.array(descriptions) # why do i go from array to list to array to list...
#

color_mapper = LinearColorMapper(palette=palette, low=0, high=16)

data=dict(
    name=location_name,
    count=instance_count,
    media=instance_list,
    descriptions=descriptions
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
    title="Audio/video of police brutality during protests (CLICK FOR INFO)",
    tools=[highlighty,'tap','reset'],
    x_axis_location=None, y_axis_location=None,
    tooltips=[
       ("City", "@name"), ("Recorded instances", "@count")
    ],
    plot_width=800,
    plot_height=470,
    toolbar_location='right'
)

# hide toolbar for now
p.toolbar_location=None

# TODO: can't figure out how to add patches for states to make a background color work.
#p.background_fill_color='#BBCCDD'
p.title.text_font_size="24px"
p.grid.grid_line_color = None

p.hover.point_policy = "follow_mouse"

# Draw county/state boundaries...

state_cds = bokeh.models.ColumnDataSource({
    'state_xs': list( load_data.state_xs ),
    'state_ys': list( load_data.state_ys )
})
state_boundaries = bokeh.models.MultiLine(xs='state_xs', ys='state_ys', line_color='#333333', line_width=0.2)
p.add_glyph(state_cds, state_boundaries)


# put in the good stuff
brutality_cds = bokeh.models.ColumnDataSource(data)

thing = p.circle('x', 'y',
                source=brutality_cds,
                radius='circle_radii',
                fill_color={'field': 'count', 'transform': color_mapper},
                fill_alpha=1, selection_fill_alpha=1, nonselection_fill_alpha=1,
                selection_fill_color={'field': 'count', 'transform': color_mapper},
                nonselection_fill_color={'field': 'count', 'transform': color_mapper},
                line_width=3,
                line_color='#666666',
                selection_line_color='#000000',
                nonselection_line_color='#666666',
                selection_line_alpha=1,
                nonselection_line_alpha=1,
                name='moo')

color_bar = bokeh.models.ColorBar(color_mapper=color_mapper,
                     label_standoff=12, border_line_color='black',
                     location=(0,0),
                     orientation='horizontal')

p.add_layout(color_bar, 'below')

######
#
# Now want to mimic
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/callbacks.html#customjs-for-user-interaction-events
#
# and generate a block of HTML that will dynamically update
# based on the thing clicked.
#

master_header='''
<div class='timestamp'>Last updated: %s </div><br/>
Original Twitter thread: <a href='%s' target=_blank>%s</a><br/>
Compiled data powering this: <a href='%s' target=_blank>%s</a><br/><br/>
Reach out to me <a class='handle' href='https://twitter.com/maaminian' target=_blank>@maaminian</a> on Twitter if you have any questions about this widget.
'''%(dt_str,tweet_number_one,tweet_number_one,spreadsheet_link,spreadsheet_link)

div = bokeh.models.Div(width=int(0.9*p.plot_width), width_policy="fixed", text=master_header)


mooo = CustomJS(args=dict(dat=brutality_cds, page=div, header=master_header), code='''
var idx = dat.selected.indices[0];
var name = dat["data"]["name"][idx];
var links = dat["data"]["media"][idx];
var descrs = dat["data"]["descriptions"][idx];
var nlinks = links.length;

var links_header="<h1 class=\'city\'>Audio/video for <font class=\'location\'>"+name+"</font> ("+ nlinks +" total)</h1>";

var myul="<ol class=\'media_list\'>";
for (var i=0; i<nlinks; i++){
    var linky=links[i];
    myul += "<li><font class=\'brutality_descr\'>" + descrs[i] + "</font><br/>";
    myul += "<a href=\'"+linky+"\' target=_blank>" + linky + "</a>\\n";
}
myul += "</ol>\\n"

page.text = header+links_header+myul;
'''
)

# Create HTML page with map on the left,
# dynamic list and links on the right.
layout=bokeh.layouts.column(p,div)

taptool = p.select(type=bokeh.models.TapTool)
taptool.callback=mooo




bokeh.io.show(layout)
