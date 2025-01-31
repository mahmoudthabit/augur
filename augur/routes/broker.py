#SPDX-License-Identifier: MIT
"""
Creates routes for the broker
"""
from flask import request, jsonify, Response
import logging
import json, requests, time

def worker_start(worker_name=None):
    process = subprocess.Popen("cd workers/{} && {}_start".format(worker_name,worker_name), shell=True)

def send_task(worker_proxy):

    # Defining local variables for convenience/readability
    user_queue = worker_proxy['user_queue']
    maintain_queue = worker_proxy['maintain_queue']
    worker_id = worker_proxy['id']
    task_endpoint = worker_proxy['location'] + '/AUGWOP/task'

    # Check if worker is alive
    r = requests.get('{}/AUGWOP/heartbeat'.format(
        worker_proxy['location']))
    j = r.json()

    if 'status' not in j:
        logging.info("Worker: {}'s heartbeat did not return a response, setting worker status as 'Disconnected'".format(worker_id))
        worker_proxy['status'] = 'Disconnected'
        return

    if j['status'] != 'alive':
        logging.info("Worker: {} is busy, setting its status as so.".format(worker_id))
        return

    # Want to check user-created job requests first
    if len(user_queue) > 0:
        new_task = user_queue.pop(0)
    
    # If no user-created job requests, move on to regulated/maintained ones
    elif len(maintain_queue) > 0:
        new_task = maintain_queue.pop(0)

    else:
        logging.info("Both queues are empty for worker {}".format(worker_id))
        worker_proxy['status'] = 'Idle'
        return     

    logging.info("Worker {} is idle, preparing to send the {} task to {}".format(worker_id, new_task['display_name'], task_endpoint))
    try:
        requests.post(task_endpoint, json=new_task)
        worker_proxy['status'] = 'Working'
    except:
        logging.info("Sending Worker: {} a task did not return a response, setting worker status as 'Disconnected'".format(worker_id))
        worker_proxy['status'] = 'Disconnected'
        # If the worker died, then restart it
        worker_start(worker_id.split('.')[len(worker_id.split('.')) - 2])
    

def create_broker_routes(server):

    @server.app.route('/{}/task'.format(server.api_version), methods=['POST'])
    def task():
        """ AUGWOP route that is hit when data needs to be added to the database
        Retrieves a json consisting of task specifications that the broker will use to assign a worker
        """
        task = request.json

        given = []
        for given_component in list(task['given'].keys()):
            given.append(given_component)
        model = task['models'][0]
        if task['job_type'] != 'MAINTAIN':
            logging.info("Broker recieved a new user task ... checking for compatible workers for given: " + str(given) + " and model(s): " + str(model) + "")

        worker_found = False
        compatible_workers = {}
        for worker_id in [id for id in list(server.broker._getvalue().keys()) if model in server.broker[id]['models'] and given in server.broker[id]['given']]:
            if type(server.broker[worker_id]._getvalue()) != dict:
                continue
            compatible_workers[worker_id.split('.')[len(worker_id.split('.'))-2]] = compatible_workers[worker_id.split('.')[len(worker_id.split('.'))-2]] if worker_id.split('.')[len(worker_id.split('.'))-2] in compatible_workers else {'task_load': len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue']), 'worker_id': worker_id}
            if (len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue'])) < min([compatible_workers[w]['task_load'] for w in compatible_workers.keys() if worker_id.split('.')[len(worker_id.split('.'))-2] == w]):
                compatible_workers[worker_id.split('.')[len(worker_id.split('.'))-2]]['task_load'] = len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue'])
                compatible_workers[worker_id.split('.')[len(worker_id.split('.'))-2]]['worker_id'] = worker_id

        for worker_type in compatible_workers.keys():
            worker_id = compatible_workers[worker_type]['worker_id']
            worker = server.broker[worker_id]
            logging.info("Compatible worker: {} with smallest task load: {} found to work on task: {}".format(worker_id, len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue']), task))

            if task['job_type'] == "UPDATE":
                worker['user_queue'].append(task)
                logging.info("Added task for model: {}. New length of worker {}'s user queue: {}".format(model, worker_id, str(len(server.broker[worker_id]['user_queue']))))
            elif task['job_type'] == "MAINTAIN":
                worker['maintain_queue'].append(task)
                logging.info("Added task for model: {}. New length of worker {}'s maintain queue: {}".format(model, worker_id, str(len(server.broker[worker_id]['maintain_queue']))))

            if worker['status'] == 'Idle':
                send_task(worker)
            worker_found = True
        # Otherwise, let the frontend know that the request can't be served
        if not worker_found:
            logging.info(f"Augur does not have knowledge of any workers that are capable of handing the request: " + str(task))

        return Response(response=task,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers'.format(server.api_version), methods=['POST'])
    def worker():
        """ AUGWOP route responsible for interpreting HELLO messages
            and telling the broker to add this worker to the set it maintains
        """
        worker = request.json
        logging.info("Recieved HELLO message from worker: " + worker['id'])
        if worker['id'] not in server.broker:
            server.broker[worker['id']] = server.manager.dict()
            server.broker[worker['id']]['id'] = worker['id']
            server.broker[worker['id']]['user_queue'] = server.manager.list()
            server.broker[worker['id']]['maintain_queue'] = server.manager.list()
            server.broker[worker['id']]['given'] = server.manager.list()
            server.broker[worker['id']]['models'] = server.manager.list()
            for given in worker['qualifications'][0]['given']:
                server.broker[worker['id']]['given'].append(given)
            for model in worker['qualifications'][0]['models']:
                server.broker[worker['id']]['models'].append(model)
            server.broker[worker['id']]['status'] = 'Idle'
            server.broker[worker['id']]['location'] = worker['location']
        else:
            logging.info("Worker: {} has been reconnected.".format(worker['id']))
            models = server.broker[worker['id']]['models']
            givens = server.broker[worker['id']]['given']
            user_queue = server.broker[worker['id']]['user_queue']
            maintain_queue = server.broker[worker['id']]['maintain_queue']

            time.sleep(10)
            server.broker[worker['id']]['status'] = 'Idle'
            send_task(server.broker[worker['id']])

        return Response(response=worker['id'],
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/completed_task'.format(server.api_version), methods=['POST'])
    def sync_queue():
        task = request.json
        worker = task['worker_id']
        logging.info("Message recieved that worker " + worker + " completed task: " + str(task))
        try:
            models = server.broker[worker]['models']
            givens = server.broker[worker]['given']
            user_queue = server.broker[worker]['user_queue']
            maintain_queue = server.broker[worker]['maintain_queue']

            if server.broker[worker]['status'] != 'Disconnected':
                send_task(server.broker[worker])
        except Exception as e:
            logging.info("Ran into error: {}".format(repr(e)))
            logging.info("A past instance of the {} worker finished a previous leftover task.".format(worker))

        return Response(response=task,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers/status'.format(server.api_version), methods=['GET'])
    def get_status():
        status = {}
        for worker in list(server.broker._getvalue().keys()):
            if type(server.broker[worker]._getvalue()) == dict:
                status[worker] = worker
                status[worker]['user_queue'] = server.broker[worker]['user_queue']._getvalue()
                status[worker]['maintain_queue'] = server.broker[worker]['maintain_queue']._getvalue()

        return Response(response=status,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers/remove'.format(server.api_version), methods=['POST'])
    def remove_worker():
        worker = request.json
        logging.info("Recieved a message to disconnect worker: {}".format(worker))
        server.broker[worker['id']]['status'] = 'Disconnected'
        return Response(response=worker,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/task_error'.format(server.api_version), methods=['POST'])
    def task_error():
        task = request.json
        worker_id = task['worker_id']
        logging.info("Recieved a message that {} ran into an error on task: {}".format(worker_id, task))
        if worker_id in server.broker:
            if server.broker[worker_id]['status'] != 'Disconnected':
                logging.info("{} ran into error while completing task: {}".format(worker_id, task))
                send_task(server.broker[worker_id])
        else:
            logging.info("A previous instance of {} ran into error while completing task: {}".format(worker_id, task))
        return Response(response=request.json,
                        status=200,
                        mimetype="application/json")