import bokeh

from bokeh.io import show
from bokeh.models import LinearColorMapper
from bokeh.palettes import Purples4 as palette
from bokeh.plotting import figure

from bokeh.models.callbacks import CustomJS

import numpy as np

###

import utils
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

## my modification - if sample data not downloaded, do it.
#try:
#    from bokeh.sampledata.us_counties import data as counties
#except:
#    raise Exception('could not import data sets; run bokeh.sampledata.download() then re-run script.')
##

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

location_htmls = []
for (location, df_sub) in grouper:
    location_name.append( ', '.join(location) )

#    instance_count.append( df_sub.shape[0] )
#    descriptions.append( list(df_sub['Doucette Text'].values) )
    
    grouper2 = df_sub.groupby('incident')
    incident_htmls = []
    for g2 in grouper2:
        incident_htmls.append( utils.incident_html_formatter(g2) )
    #
#    location_htmls.append( ' '.join(incident_htmls) )
    location_htmls.append( incident_htmls )
    instance_count.append( len(incident_htmls) )
#

#descriptions = np.array(descriptions) # why do i go from array to list to array to list...
#

color_mapper = LinearColorMapper(palette=palette, low=0, high=20)

data=dict(
    name=location_name,
    count=instance_count,
#    descriptions=descriptions,
    html=location_htmls
)

xy = np.array([load_data.latlon_lookup.get(n, (np.nan,np.nan)) for n in data['name']])
data['y'] = xy[:,0]
data['x'] = xy[:,1]
fudge = 0.5
power = 0.25
data['circle_radii'] = [fudge*c**power for c in data['count']]


#TOOLS = "wheel_zoom,reset,hover"
#TOOLS = "wheel_zoom,reset,tap"

# DISABLED HOVER FOR NOW
highlighty = bokeh.models.HoverTool(names=['moo'])
#tappy = bokeh.models.TapTool()

# SUPPOSEDLY - "The United States is 2,800 miles wide when measured horizontally
# from the eastern seaboard to the west coast (West Quoddy Head in the east to
# Point Arena in West) and 1,582 miles from north to south."
# So aim for an aspect ratio of around 0.565.
p = figure(
    title="Audio/video of police brutality/misconduct during protests",
    tools=['tap','wheel_zoom','pan',highlighty],
    x_axis_location=None, y_axis_location=None,
    tooltips=[
       ("City", "@name"), ("Num. cases", "@count")
    ],
    plot_width=800,
    plot_height=500,    #figure padding makes a tad bigger than 452 a better choice.
    sizing_mode='scale_both'
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
state_boundaries = bokeh.models.MultiLine(xs='state_xs', ys='state_ys', line_color='#111111', line_width=0.4)
p.add_glyph(state_cds, state_boundaries)


# put in the good stuff
brutality_cds = bokeh.models.ColumnDataSource(data)

thing = p.circle('x', 'y',
                source=brutality_cds,
                radius='circle_radii',
                fill_color={'field': 'count', 'transform': color_mapper},
                fill_alpha=0.7, selection_fill_alpha=0.7, nonselection_fill_alpha=0.7,
                selection_fill_color={'field': 'count', 'transform': color_mapper},
                nonselection_fill_color={'field': 'count', 'transform': color_mapper},
                line_width=3,
                line_color='#666666',
                selection_line_color='#000000',
                nonselection_line_color='#666666',
                selection_line_alpha=0.7,
                nonselection_line_alpha=0.7,
                name='moo')

color_bar = bokeh.models.ColorBar(color_mapper=color_mapper,
                     label_standoff=12, border_line_color='black',
                     location=(0,0),
                     orientation='horizontal')

#color_bar.major_tick_in = 4 # ONLY WORKS WITH RANGE OF VALUES 0-20 AND 5 COLORS

p.add_layout(color_bar, 'below')

thing.selection_glyph

######
#
# Now want to mimic
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/callbacks.html#customjs-for-user-interaction-events
#
# and generate a block of HTML that will dynamically update
# based on the thing clicked.
#

jem_twitter="https://twitter.com/jasonemiller"

about_text='''
<div class='timestamp'>Documentation since <b>May 29.</b> Last updated: <b>%s</b> </div><br/>

<div class='aboutbox'>
<h1 class='about'>About this visualization</h1>

<ul>
<li> <font class='datasource'>Original Twitter thread by Greg Doucette:</font> <a href='%s' target=_blank>%s</a><br/>
<li> <font class='datasource'>Data in spreadsheet form curated by <a href='%s' target=_blank>@jasonemiller</a>:</font> <a href='%s' target=_blank>%s</a>
<li> <font class='datasource'>To contact me:</font> Find my email at <a href="https://www.math.colostate.edu/~aminian/" target=_blank>my website</a> or
message me on Twitter
<a class='handle' href='https://twitter.com/maaminian' target=_blank>@maaminian</a>
</ul>

<p> This visualization documents cases of
police brutality or misconduct during the nationwide protests
following the murder of George Floyd by a Minneapolis police officer.
This is not comprehensive &mdash; these are only the cases
Tweeted by individuals and broadcasted by Greg Doucette.

<p> <font class='warning'>Warning:</font>
the descriptions and associated video may contain offensive language
or triggering content.

<p> To use this: click on a location, and a list of incidents
along with short descriptions and links to associated Tweets will
update on the right panel. 

<h2>Update log</h2>
<ul>
  <li> July 3:
    <ul>
      <li> Data is up to date as of mid-day on July 3. We're up to <b>687</b> unique cases 
        in the 48 states, plus or minus a few 
        accounting for bookkeeping errors, side notes, etc. Things are getting 
        very busy on the map. I'll likely enable a zoom tool in a future update.
      <li> Tweaked the sizing of circles for slight improvement in visibility
      <li> Miscellaneous fixes for typos, bookkeeping errors
    </ul>
  <li> June 14:
    <ul>
      <li> Data is up to date as of the timestamp shown above. There are roughly 
        <b>503</b> unique incidents documented here.
      <li> Note indicating the rough starting date of collection, measured by 
        the date of Greg Doucette's first numbered tweet is now indicated next 
        to the "Last Updated" date. (That date is May 29.)
    </ul>
  <li> June 7: 
    <ul>
      <li> Data is up to date as of the timestamp shown above.
      <li> Data is now organized by the actual incident
        number &mdash; if there are multiple sources for the same event, 
        they'll now show up in a single sub-list and not accumulate
      <li> Links to Youtube have been included if they exist in the spreadsheet.
      <li> Known typos in cities and associated problems have been fixed.
    </ul>
  <li> June 4: 
    <ul>
      <li> Data updated. 
      <li> The map will scale with the size of the browser window. 
      <li> Overall Layout and CSS has been updated
    </ul>
</uul>


</div>
'''%(dt_str,tweet_number_one,tweet_number_one,jem_twitter,spreadsheet_link,spreadsheet_link)

# Fixed "about" section beneath
div_about = bokeh.models.Div(width=800, height=300, text=about_text, sizing_mode='scale_both')


# initial blank for tweets column.
wrapl = "<div class='avbox'>"
wrapr = "</div>"

pre_header='''
%s<h1 class='city'>Audio/video for <font class='location'>...</font> (select a location)%s
'''%(wrapl,wrapr)

div = bokeh.models.Div(width=500, width_policy="fixed", text=pre_header, sizing_mode='stretch_height')

mooo = CustomJS(args=dict(dat=brutality_cds, page=div, wl=wrapl, wr=wrapr), code='''
var idx = dat.selected.indices[0];
var name = dat["data"]["name"][idx];
var html = dat["data"]["html"][idx];
var nlinks = html.length;

var links_header="<h1 class=\'city\'>Audio/video for <font class=\'location\'>"+name+"</font> ("+ nlinks +" total)</h1>";

var myul="<ol class=\'media_list\'>";

for (var i=0; i<nlinks; i++){
    myul += html[i] + " ";
}

myul += "</ol>\\n"

page.text = wl + links_header+myul + wr;
'''
)

# Create HTML page with map on the left,
# dynamic list and links on the right.
#layout=bokeh.layouts.column(p,div)
#layout=bokeh.layouts.row(p,div)
#layout = bokeh.layouts.gridplot([[p,div],[div_about,None]])
layout = bokeh.layouts.row(
    bokeh.layouts.column(p,div_about, sizing_mode='scale_both'), 
    div
)

taptool = p.select(type=bokeh.models.TapTool)
taptool.callback=mooo




bokeh.io.show(layout)
