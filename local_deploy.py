import os
import sys
import argparse
from collections import deque

config_path = os.path.dirname(os.path.abspath(__file__)) + "/config/"


def kubectl_build_command(config_name):
    return 'cat ' + resolve_config(config_name) + ' | sed "s#{{PWD}}#$PWD#g" | kubectl apply -f -'


def resolve_config(config_name):
    filename = config_name if config_name.endswith(".yaml") else config_name + ".yaml"
    return config_path + filename


def command_run(command):
    res = os.system(command)
    if res != 0:
        raise Exception("Command failed to execute, given command: " + command)


ingress = "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml"
parser = argparse.ArgumentParser(description='Configuration file names.')
parser.add_argument('configs', type=str, nargs='*')
parser.add_argument('--all', action='store_true', help="Apply all config files from config subdirectory.")
parser.add_argument('--ingress', action='store_true', help="Create ingress pod")
parser.add_argument('--start', action='store_true', help="Start minikube for you")
parser.add_argument('--dropall', action='store_true', help="Delete all pods, services and deployment apps.")
args = parser.parse_args()
if args.all:
    args.configs = [filename for filename in os.listdir(config_path) if filename.endswith(".yaml")]

commands = [kubectl_build_command(name) for name in args.configs if os.path.exists(resolve_config(name))]

if args.ingress:
    commands.append(ingress)
try:
    if args.dropall:
        command_run('kubectl delete pod --all')
        command_run('kubectl delete service --all')
        command_run('kubectl delete deployment.apps --all')
        command_run('kubectl delete ingresses --all')
        command_run('kubectl delete pvc --all')
        command_run('kubectl delete pv --all')
        #command_run('minikube delete')
    if args.start:
        command_run('minikube start')
        command_run('minikube addons enable ingress')
        command_run('minikube ip')
    deque(map(command_run, commands))
except Exception as e:
    print(str(e))
