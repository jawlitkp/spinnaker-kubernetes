import yaml
import os
import time
import collections
import subprocess

def runHealth(name, port):
  portOpen = False
  while portOpen == False:
    result = subprocess.check_output("docker exec -it spinnakerkubernetes_pingbox_1 nmap -p " + str(port) + ' ' + name + '-alias', shell=True)
    if "open" in result:
      print name + " is running."
      portOpen = True
    else:
      print "waiting for " + name + " to start..."
      time.sleep(2)

def startContainer(name, port):
  os.system("docker-compose up -d " + name)
  runHealth(name, port)

os.system("python config.py")

#install minikube
os.system("curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.5.0/minikube-darwin-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/")

#cleanup
os.system("docker-compose down")
os.system("minikube stop")
os.system("minikube delete")

os.system("minikube start")
ip = os.popen('minikube ip').read().rstrip()

kubeConfig = """\
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /root/.kube/apiserver.crt
    server: https://""" + ip + """:443
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users:
- name: minikube
  user:
    client-certificate: /root/.kube/apiserver.crt
    client-key: /root/.kube/apiserver.key
"""

with open("minikube.config", "w") as text_file:
  text_file.write(kubeConfig)

os.system("docker-compose up -d pingbox")
os.system("docker-compose up -d configdata")
time.sleep(5)
startContainer("redis",6379)
startContainer("cassandra",9160)
time.sleep(1)
os.system("docker exec -it spinnakerkubernetes_cassandra_1 cqlsh -e \"CREATE KEYSPACE IF NOT EXISTS front50 WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };\"")
os.system("docker exec -it spinnakerkubernetes_cassandra_1 cqlsh -e \"CREATE KEYSPACE IF NOT EXISTS echo WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };\"")
os.system("docker exec -it spinnakerkubernetes_cassandra_1 nodetool enablethrift")
startContainer("front50",8080)
startContainer("clouddriver",7002)
startContainer("rosco",8087)
startContainer("orca",8083)
startContainer("gate",8084)
os.system("docker-compose up -d deck")
time.sleep(2)
os.system("open http://localhost:9000")
os.system("minikube dashboard")
