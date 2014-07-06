def mark_required(table):
    """
    Mark '*' for the required fields in form
    """
    marker = SPAN('*', _class='fld_required', _style='color:red')
    for field in table:
        required = False
        if field.notnull:
            required = True
        elif field.requires:
            required=isinstance(field.requires,(IS_IN_SET, IS_IPV4))
        if required:
            _label = field.label
            field.label = SPAN(_label, ' ', marker, ' ')

def jsonToTable(jsonData, order):
    """
    Converts a JSON dictionary to an HTML table
    """
    if not any(jsonData):
        return None
    output = '<table class="table table-striped table-bordered table-condensed">'
    output += '<thead>'
    for key in order:
        output += '<td><b>%s</b></td>' % key.capitalize()
    output += '</thead>'
    output += '<tbody>'
    for data in jsonData:
        output += '<tr>'
        for key in order:
            output += '<td>%s</td>' % data[key]
        output += '</tr>'
    output += '</tbody>'
    output += '</table>'
    return output
