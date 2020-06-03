# What is this?

Dashboard to find instances of (alleged) police brutality near you!

# What to do?

The main webpage is generated with brutality_vis.py, with 
a few small tweaks to the html file generated to add a 
custom css file and house the bokeh .js files locally.

# prerequisites

* bokeh
* numpy
* pandas
* opencage (optional, if for some reason you need to re-fetch lat/lon for cities)

# data sources

* Original Twitter thread: https://twitter.com/greg_doucette/status/1266752393556918273
* Compiled spreadsheet from that thread: https://docs.google.com/spreadsheets/d/1YmZeSxpz52qT-10tkCjWOwOGkQqle7Wd1P7ZM1wMW0E/edit#gid=0

# Credit/reuse?

Right now this is a quick personal project, so I only politely ask that you acknowledge 
me (Manuchehr Aminian) if you use this or modify it in any simple way. 
But the license attached to the repository says the rest (GNU GPLv3). 
It would warm my heart if you told me that 
this helped you in any way (you can find me at @maaminian on Twitter). 
Don't hesitate to message/email me if you have questions.


# Random notes

US shapefiles can be found at:

https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html

Lowest resolution available is good enough. I didn't attach these to the git repo.
