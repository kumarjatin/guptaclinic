from datetime import datetime

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
        if key == 'id':
            output += '<td><b>Actions</b></td>'
        else:
            output += '<td><b>%s</b></td>' % key.capitalize()
    output += '</thead>'
    output += '<tbody>'
    for data in jsonData:
        output += '<tr>'
        for key in order:
            btnHtml = ''
            if key=='id':
                btnHtml = '<a href="' + URL('add_visit', vars=dict(visit_id=data[key])) + '"><img src="' + URL('static', 'images/repeat.png') + '" class="repeat_btn" title="Repeat"/></a>'
                btnHtml += '<a href="'+ URL('edit_visit', vars=dict(vid=data[key])) + '"><img title="Update" src="' + URL('static', 'images/update.png') + '" class="repeat_btn"/></a>'
            output += '<td>%s</td>' % (btnHtml)
        output += '</tr>'
    output += '</tbody>'
    output += '</table>'
    return output

def getCurrentAge(age, entryTime):
    """
    Given two strings returns current age
    """
    FORMAT = '%Y-%m-%d %H:%M:%S'
    currentTime = datetime.now()
    if isinstance(entryTime, datetime):
        entryObject = entryTime
    else:
        entryObject = datetime.strptime(entryTime, FORMAT)
    grownUp = currentTime - entryObject
    print grownUp.days
    currentAge = round(float(age) + float(grownUp.days)/365, 1)
    return str(currentAge)
