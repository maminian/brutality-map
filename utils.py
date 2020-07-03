def incident_html_formatter(groupby_entry, export=None, debug=False):
    '''
    Given an entry of df.groupby(...) coming from 
    the Doucette dataframe, process the stuff and 
    output a block of HTML for the entry.
    
    You should expect the output block to be a **list entry**, 
    i.e., something beginning with <li>.
    If there are multiple recordings of a single incident, 
    there will be a second level <ol> for this.
    
    Input:
        groubpy_entry : a tuple of length 2; 
            groupby_entry[0] is a string indicating the incident number
            groubpy_entr[1] is the associated dataframe of observations.
            
    Output:
        incident_html : string of associated HTML for the case.
        
    Optional input:
        export : if not None, saves the example to an HTML file indicated
            to help with the CSS development process. BE CAREFUL - 
            this will silently overwrite whatever else is in that file.
        debug : if True, sets a pdb.set_trace() at the top of the function.
    '''
    if debug:
        import pdb
        pdb.set_trace()
    #
    
    prefix = "<li class=\'incident\'>"
    suffix = "</li>"
    
    gdid,df_s = groupby_entry
    
    if df_s.shape[0]==1:
        # handle a singleton separately.
        # amounts to [description]<br/>[url]
        descr = df_s.iloc[0]['Doucette Text']
#        tw_url = df_s.iloc[0]['Tweet URL']
        tw_html = build_url_html(df_s.iloc[0])
        
        middle = "%s<br/> %s"%(descr,tw_html)
        
    else:
        # need to build another ordered list.
        incident_header = "Incident number %s"%gdid
        prefix = prefix + incident_header + "\n<ol class=\'incident_obs\'>\n"
        suffix = "</ol> " + suffix
        
        entries = []
        for j in range(df_s.shape[0]):
            row = df_s.iloc[j]
            
            descr = row['Doucette Text']
#            tw_url = row['Tweet URL']
            tw_html = build_url_html(row)
            
            entries.append( "    <li class=\'row_entry\'><font class=\'brutality_descr\'> %s<br/>\n  %s</font>\n"%(descr,tw_html) )
        #
        middle = ' '.join(entries)
    #
    
    incident_html = prefix + middle + suffix

    if isinstance(export, str):
        exportable = '<html><head>\n<link rel=\'stylesheet\' href=\'style.css\'>\n</head><body>\n' + incident_html + '</body></html>'
        with open(export, 'w') as f:
            f.write(exportable)
    #
    
    return incident_html
#

def build_url_html(df_row):
    # TODO: class? fancier formatting?
    links = []
    for kw,column in zip(['source','yt'], ['Tweet URL', 'YouTube']):
        entry = df_row[column]
        if isinstance(entry, str):
            clname = kw+'_link'
            links.append( "<a href='%s' class='%s' target='_blank'>(%s)</a>\n"%(entry, clname, kw) )
    #
    out_html = ' '.join(links)
    return out_html
