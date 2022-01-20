# ShippingChallenge2021

- **Name**: Princewell Baffour Awuah


## My Stack
| **Webserver** | **Database** | **Script Language** |   **Extra**   |
|:-------------:|:------------:|:-------------------:|:-------------:|
|    Lighttpd   |    MongoDb   |  Python/Flask       |   Portainer   |

## The Challenge
- Create your own kubernetes stack with 1 worker.
- Containerized application on worker is the following.
    ![Challenge](images/challenge.png)
    - When surname changes in Db, webpage changes automatically.
    - When  layout of webpage changes, the worker will display the new layout automatically.
    - Use the webstack which is assigned to you.

### How to earn points?
- 0/20 - be like Homer Simpson or Al Bundy
- 10/20 - stack in Docker
- 14/20 - mk8s cluster with 1 worker

### Extra points
- Vagrant
- Extra worker
- Management webplatform for containers, see Extra in [My Stack](#my-stack).
- Something else than mk8s with the same purpose.

### Nice to haves - Fun Factor
- A practical linux joke for docents.
- A linux koan to enlighten your docents.

## My Setup
### Dockerfile
```Dockerfile
# The line below states we will base our new image on debian buster 
FROM debian:buster
MAINTAINER  Princewell <princewell.ba@gmail.com>

# Update the image to the latest packages, install python, python-pip, pymongo, flask and enabled CGI module in lighttpd
RUN apt-get update\
        && apt-get -y upgrade\
        && apt-get -y install python lighttpd nano python-pip python-memcache\
        && pip install pymongo==3.11\
        && pip install flask\
        && pip install waitress\
        && lighty-enable-mod cgi

# Copy the configuration files to the container
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY 10-cgi.conf /etc/lighttpd/conf-available/10-cgi.conf

# Copy the index file to the correct directory on the container
COPY app/index.py /var/www/html/
# Copy the start script to the container and make it executable 
ADD start.sh /
RUN chmod +x /start.sh
# Expose ports 80 and 443
EXPOSE 80
EXPOSE 443

# Run the script
CMD ["/start.sh"]

```
#### Main steps
- Get the Bedian: buster base image.
- Update everything
- Install [My Stack](#my-stack)
- Copy the configuration files
- Copy the executable python file 'flask' Application
- Copy the start script and make it executable
- Expose port 80 and 443 for lighttpd
- Run the start script

### Start Script
```start.sh
#!/bin/bash
# The lighttpd configuration file is enabled and the flask app is started with python
exec lighttpd -D -f /etc/lighttpd/lighttpd.conf &
exec python  /var/www/html/index.py

```

### Start Script
```index.py
from flask import Flask
from pymongo import MongoClient
import pymongo
app = Flask(__name__)

@app.route('/')
def index():
    client = MongoClient("mongodb://username:password@mongodb-service")
    db = client["milestone3"]
    col = db["data"]
    cursor = col.find()
    for text_fromDB in cursor:
        text = str(text_fromDB['name'].encode('utf-8'))
    print(text)
    return("<h1>"+text+" has reached Milestone 3 and is king of the mountain!</h1>")

if __name__ == "__main__":
    from waitress import serve
    app.run(host="0.0.0.0",debug=True)
```
### DockerHub
My custom Shipping Challenge image is hosted on DockerHub and is accessible in the repo:  
[princewell/debian-lighttpd-flask](https://hub.docker.com/repository/docker/princewell/debian-lighttpd-flask)

If i want to make changes to my page layout, it's made and the new changes is pushed to DockerHub

### Kubernetes
#### Deployment
The deployment downloads the [princewell/debian-lighttpd-flask](https://hub.docker.com/repository/docker/princewell/debian-lighttpd-flask) image  and creates 3 pods of it. This has also been set up to keep the pods always up-to-date on a restart.
```webserver.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  #annotations:
    #reloader.stakater.com/auto: "true"
  name: webserver
  labels:
    app: lighttpd
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lighttpd
  template:
    metadata:
      labels:
        app: lighttpd
    spec:
      containers:
      - name: flask-lighttpd
        image: princewell/debian-lighttpd-flask:latest
        imagePullPolicy: Always
        # this will always check for a newer image when a pod starts

        ports:
        - containerPort: 5000

```        
# The service gives the webserver pods the correct IP and Port.
```
apiVersion: v1
kind: Service
metadata:
  name: web-service
  labels:
    run: web-service
spec:
  type: LoadBalancer
  ports:
  - port: 5000
    protocol: TCP
    targetPort: 5000
    nodePort: 30010
  selector:
    app: lighttpd

```

#### MongoDb Deployment
```mongodb-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-deployment
  labels:
    app: mongodb
spec:                        # a deployment's specification
  replicas: 1                # tells deployment to run 1 pod
  selector:
    matchLabels:
      app: mongodb
  template:                  # regular pod configuration
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo
        ports:
          - containerPort: 27017   # The default port of mongo db
        env:
            - name: MONGO_INITDB_ROOT_USERNAME
              value: 'username'
              #valueFrom:
                #secretKeyRef:
                  #name: mongodb-secret
                  #key: mongo-root-username
            - name: MONGO_INITDB_ROOT_PASSWORD
              value: 'password'
              #valueFrom:
                #secretKeyRef:
                  #name: mongodb-secret
                  #key: mongo-root-password
                  
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
spec:
  selector:
    app: mongodb
  ports:
    - protocol: TCP
      port: 27017
      targetPort: 27017


```
#### Mongo-Express Deployment
```mongo-express-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongo-express-deployment
  labels:
    app: mongo-express
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongo-express
  template:
    metadata:
      labels:
        app: mongo-express
    spec:
      containers:
      - name: mongo-express
        image: mongo-express
        ports:
          - containerPort: 8081
        env:
          - name: ME_CONFIG_MONGODB_ADMINUSERNAME
            value: 'username'
            #valueFrom:
              #secretKeyRef:
                #name: mongodb-secret
                #key: mongo-root-username
          - name: ME_CONFIG_MONGODB_ADMINPASSWORD
            value: 'password'
            #valueFrom:
              #secretKeyRef:
                #name: mongodb-secret
                #key: mongo-root-password
          - name: ME_CONFIG_MONGODB_SERVER
            value: 'mongodb-service'
            #valueFrom:
              #configMapKeyRef:
                #name: mongodb-configmap
                #key: database_url
---
apiVersion: v1
kind: Service
metadata:
  name: mongo-express-service
spec:
  selector:
    app: mongo-express
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 8081
      targetPort: 8081
      nodePort: 30000
      
```

#### Mongo-configMap
```mongo-configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: mongodb-configmap
data:
  database_url: mongodb-service

```


## Sources

### Docker Repository
  - https://docs.docker.com/docker-hub/repos/
  - https://docs.docker.com/docker-hub/builds/

### Kubernetes
  - A-Van-Gestel/2APPAI1-LinuxWS-Shipping_Challenge
    - https://github.com/A-Van-Gestel/2APPAI1-LinuxWS-Shipping_Challenge
  - Deployment File
    - https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

### Portainer
  - https://documentation.portainer.io/v2.0/deploy/linux/
  - https://github.com/portainer/portainer-k8s/blob/master/charts/portainer-beta/README.md

### Bash Script
 - http://matt.might.net/articles/bash-by-example/
