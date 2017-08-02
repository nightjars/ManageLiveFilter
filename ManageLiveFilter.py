from flask import Flask, render_template, redirect, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, DecimalField, IntegerField, HiddenField
from wtforms.widgets import TextArea

import client_api

app = Flask(__name__)


class InversionForm(Form):
    model = StringField('Model', validators=[validators.input_required()])
    label = StringField('Label', validators=[validators.input_required()])
    tag = StringField('Tag', validators=[validators.input_required()])
    minimum_offset = DecimalField('Minimum Offset for Station Consideration', places=10, validators=[validators.input_required()])
    convergence = DecimalField("Convergence", validators=[validators.input_required()])
    eq_pause = IntegerField("EQ Pause", validators=[validators.input_required()])
    eq_threshold = DecimalField('EQ Threshold', places=10, validators=[validators.input_required()])
    mes_wait = IntegerField("Wait", validators=[validators.input_required()])
    max_offset = DecimalField('Max Offset', places=10, validators=[validators.input_required()])
    min_r = DecimalField('Min_R / Minimum Offset in Calculations', places=10, validators=[validators.input_required()])
    id = HiddenField('id')


class FaultForm(Form):
    fault_data = StringField('Fault Data', widget=TextArea())
    id = HiddenField('id')


@app.route('/')
def status():
    s = client_api.get_status_api()
    return render_template('status.html', status=s)


@app.route('/edit/<int:inv_id>', methods=['GET'])
@app.route('/edit', methods=['POST', 'GET'])
def edit_inversion(inv_id=None):
    if inv_id is None:
        inversion = {
                'model': 'Model',
                'label': 'Label',
                'tag': 'Tag',
                'minimum_offset': 0.001,
                'convergence': 0,
                'eq_pause': 60,
                'eq_threshold': 1,
                'mes_wait': 2,
                'max_offset': 200,
                'min_r': 0.001}
    else:
        inversion = client_api.get_inversion_api(inv_id)

    form = InversionForm(request.values, **inversion)
    if request.method == 'POST' and form.validate():
        print (str(form.data))
        print ("passed")
    else:
        print ("failed")
        print (request.method)
        print ((str(form.data)))

    return render_template('edit_inversion.html', form=form)


@app.route('/faults/<int:inv_id>', methods=['GET'])
@app.route('/faults', methods=['POST'])
def edit_faults(inv_id=None):
    inversion = client_api.get_inversion_api(inv_id)
    if inversion:
        faults = inversion['faults']
        fault_data = str(faults['length']) + " " + \
                     str(faults['width']) + "\n"
        for fault in faults['subfault_list']:
            for float_entry in fault:
                fault_data += str(float_entry)
            fault_data += "\n"
    form = FaultForm(request.values, fault_data=fault_data)
    return render_template('edit_faults.html', form=form)

@app.route('/enable/<int:inv_id>')
def enable_inversion(inv_id):
    client_api.toggle_state_api(inv_id, True)
    return redirect('/')


@app.route('/disable/<int:inv_id>')
def disable_inversion(inv_id):
    client_api.toggle_state_api(inv_id, False)
    return redirect('/')

if __name__ == '__main__':
    app.run()
