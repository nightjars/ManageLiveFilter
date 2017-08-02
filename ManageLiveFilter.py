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
        return redirect('/')

    return render_template('edit_inversion.html', form=form)


@app.route('/faults/<int:inv_id>', methods=['GET'])
@app.route('/faults', methods=['POST'])
def edit_faults(inv_id=None):
    if inv_id is not None:
        inversion = client_api.get_inversion_api(inv_id)
        if inversion:
            faults = inversion['faults']
            fault_data = str(faults['length']) + " " + \
                         str(faults['width']) + "\n"
            for fault in faults['subfault_list']:
                for float_entry in fault:
                    fault_data += str(float_entry) + " "
                fault_data += "\n"
            fault_data = fault_data[:-1]    # remove last newline
        form = FaultForm(request.values, fault_data=fault_data, id=inv_id)
    else:
        form = FaultForm(request.values)

    if request.method == 'POST' and form.validate():
        line_num = 1
        fault_data = form.fault_data.data.split('\n')
        try:
            fault_data[0] = fault_data[0].split()
            print (fault_data[0])
            faults = {
                'length': float(fault_data[0][0]),
                'width': float(fault_data[0][1]),
                'subfault_list': []
            }
            print(faults)
            for fault in fault_data[1:]:
                line_num += 1
                fault_entries = fault.split()
                if len(fault_entries) < 7:
                    raise Exception
                elif len(fault_entries) > 8:
                    raise Exception
                elif len(fault_entries) == 7:
                    fault_entries.append(0.)
                fault_entries = [float(x) for x in fault_entries]
                faults['subfault_list'].append(fault_entries)
                print (fault_entries)
            return redirect('/')
        except:
            # error on line line # - add error message
            print ("error line {}".format(line_num))
            pass

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
