#@requires_login()
import json
from datetime import datetime
def check_add_form(form):
    """
    Checks if the fields are in good shape
    """
    name = form.vars.name
    mobile = form.vars.mobile
    age = form.vars.age
    dups = db(db.patients.name == name)(db.patients.mobile == mobile).select()
    if any(dups):
        form.errors.name = 'Record already exists. PID: %s' % (dups[0]['id'])

def add_patient():
    """
    Adds new patient
    """
    mark_required(db.patients)
    form = SQLFORM(db.patients)
    if request.vars.name:
        form.vars.name = request.vars.name
    if form.process(onvalidation=check_add_form).accepted:
        pid = db(db.patients.name == form.vars.name)(db.patients.age == form.vars.age)(db.patients.mobile == form.vars.mobile).select()
        response.flash = '%s added. ID: %s' % (form.vars.name, pid[0]['id'])
        redirect(URL('add_visit', vars=dict(pid=pid[0]['id'])))
    elif form.errors:
        response.flash = 'Form has errors'
    return dict(form=form)

def edit_patient():
    """
    Update an existing patient
    """
    mark_required(db.patients)
    pid = request.args(0)
    record = db.patients(pid)
    form = SQLFORM(db.patients, record, submit_button='Update', deletable=True)
    if form.process(onvalidation=check_add_form).accepted:
        exists = db(db.patients.id == pid).select()
        if not any(exists):
            response.flash = '%s deleted' % (form.vars.name)
            redirect(URL('search'))
        else:
            response.flash = '%s updated. ID: %s' % (form.vars.name, pid)
    elif form.errors:
        response.flash = 'Form has errors'
    return dict(form=form, pid=pid)

def search():
    """
    Dummy search form
    """
    response.flash = 'Fill in name or mobile number'
    return dict()

def search_patient():
    """
    Search patient form
    """
    pid = request.args[0] if any(request.args) else None
    if not pid:
        return None
    pid = int(pid)
    records = db(db.visits.pid == pid).select(limitby=(0,15), orderby=~db.visits.id)
    jsonResults = []
    order = ['id', 'date', 'diagnosis', 'treatment', 'remarks']
    for record in records:
        info = {'id':record['id'], 'date':str(record['currentdate']),
                'diagnosis':record['diagnosis'], 'treatment':record['treatment'],
                'remarks':record['remarks']}
        jsonResults.append(info)
    if any(jsonResults):
        return jsonToTable(jsonResults, order, repeatBtn=True)
    else:
        return None

def add_visit():
    """
    Adds new treatment details for a patient visit
    """
    mark_required(db.visits)
    details = {}
    records = []
    pid = None
    if request.vars.pid or request.vars.visit_id:
        db.visits.pid.readable = False
        db.visits.pid.writable = False
        pid = request.vars.pid
    form = SQLFORM(db.visits)
    if request.vars.pid:
        form.vars.pid = request.vars.pid
    if request.vars.visit_id:
        visit_id = request.vars.visit_id
        visit_record = db(db.visits.id == visit_id).select()[0]
        pid = visit_record['pid']
        form.vars.pid = visit_record['pid']
        form.vars.diagnosis = visit_record['diagnosis']
        form.vars.treatment = visit_record['treatment']
        form.vars.next_visit = visit_record['next_visit']
        form.vars.remarks = visit_record['remarks']
    if form.process().accepted:
        session.flash = 'Visit added for PID %s' % str(pid)
        pid = form.vars.pid
        redirect(URL('search'))
    elif form.errors:
        response.flash = 'Form has errors'
    if pid:
        details = db(db.patients.id == pid).select()[0]
        records = db(db.visits.pid == pid).select(orderby=~db.visits.id)
    return dict(form=form,details=details,records=records[0:15],morerecords=records[15:])

def edit_visit():
    """
    Update an existing visit of a patient
    """
    mark_required(db.visits)
    details = {}
    vid = request.vars.vid
    record = db.visits(vid)
    pid = db(db.visits.id == vid).select()[0]['pid']
    db.visits.pid.readable = False
    db.visits.pid.writable = False
    db.visits.id.readable = False
    db.visits.id.writable = False
    form = SQLFORM(db.visits, record, submit_button='Update', deletable=True)
    if form.process().accepted:
        session.flash = 'Visit updated for PID %s' % str(pid)
        redirect(URL('add_visit', vars=dict(pid=pid)))
    elif form.errors:
        response.flash = 'Form has errors'
    details = db(db.patients.id == pid).select()[0]
    return dict(form=form,details=details)

def search_patient_name_mobile():
    """
    Creates search form for looking into patients database
    A string containing # in the beginning means search for id
    """
    pattern = request.vars.term
    results = []
    if pattern.find('#') >= 0:
        pid = pattern.strip('#. ')
        results = db(db.patients.id.like(pid)).select(limitby=(0,15))
    else:
        partialstr = '%' + pattern + '%'
        results = db( db.patients.name.like(partialstr) | db.patients.mobile.like(partialstr) ).select(limitby=(0,15))
    jsonResults = []
    for result in results:
        label = '#%d. %s (%s, %s)' % (result['id'], result['name'], result['mobile'], result['age'])
        info = {'label':label, 'value':label}
        jsonResults.append(info)
    return json.dumps(jsonResults)

def get_visits_by_date():
    """
    Gets the visits of a given date
    """
    visits_date = request.now.date()
    if request.vars.date:
        visits_date = datetime.strptime(request.vars.date, '%Y-%m-%d').date()
    results = db((db.visits.currentdate.year() == visits_date.year)
                 & (db.visits.currentdate.month() == visits_date.month)
                 & (db.visits.currentdate.day() == visits_date.day)
		     & (db.visits.pid == db.patients.id)).select()
    return dict(visits=results,visits_date=visits_date)

def aboutme():
    """
    Render about me page
    """
    return dict()

def clear_data():
    """
    Clear all the medicines record
    """
    records = db(db.visits.id >= 0).select()
    for record in records:
        content = record.as_dict()
        content.pop('id')
        db.visits_backup.insert(**content)
        data = record['treatment'].split('(')
        if len(data)>1:
            newData = '(' + data[1]
        else:
            newData = 'N/A'
        record.update_record(treatment = newData)
    session.flash = 'Data Cleared'
    redirect(URL('aboutme'))