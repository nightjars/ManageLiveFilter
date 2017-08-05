import requests

host = '127.0.0.1'
port = '5002'

base_url = 'http://'+host+':'+port
status_url = base_url + '/status'
single_inversion_url = base_url + '/inversion/{}'
faults_url = base_url + '/faults'

def get_status_api():
    status = requests.get(status_url)
    return status.json()


def toggle_state_api(inversion_id, state):
    requests.put(status_url, json={
        'inversion': int(inversion_id),
        'active': state
    })

def replace_faults(inversion_id, faults):
    requests.post(faults_url, json={'inversion': int(inversion_id),
                                    'faults': faults})

def get_inversion_api(inversion_id):
    inversion = requests.get(single_inversion_url.format(inversion_id))
    return inversion.json()