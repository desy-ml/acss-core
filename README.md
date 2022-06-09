# ACSS Core

ACSS (Accelerator Control and Simulation Services) provides an environment for scheduling and orchestrating of multiple intelligent agents, training and tuning of ML models, handling of data streams and for software testing and verification.

User specific services are located at github (https://github.com/desy-ml/ml-pipe-services).

# Dependencies

Docker and docker-compose >= 1.28.0 are required.

# Install Core Services

Clone the acss-services repository.
```
git clone https://github.com/desy-ml/ml-pipe-services
```

## Build Docker images
Open the root folder of the accs-core project:
```
cd /path/to/project
```

To build all docker images run:
```bash
make build-all
``` 
This can take a while...

Notes: After changing code you just need to rebuild the service images, which is much faster.
```
make build-service-images
```

## Start Core Services
To Start the core services of ACSS you need to set the following environment values in a .env file.
```
ACSS_EXTERNAL_HOST_ADDR=localhost
ACSS_DB_PW=xxxx
ACSS_DB_USER=xxxx
ACSS_CONFIG_FILEPATH = /path/to/ml-pipe-config.yaml
PATH_TO_ACSS_SERVICES_ROOT=/path/to/ml-pipe-services
```

ACSS_CONFIG_FILEPATH is the path to the yaml config file, which look like this:

```yml
observer:
  # used to check if jbb is done
  url: observer:5003
  event_db_pw: xxxx
  # event_db_url:
  event_db_usr: xxxx
register:
  # registers all services
  url: register:5004
simulation:
  # sql database which maps the machine parameter
  sim_db_pw: xxxx
  sim_db_usr: xxxx
  sim_db_url: simulation_database:3306
msg_bus:
  # message bus
  # external_host_addr: localhost
  broker_urls: kafka_1:9092,kafka_2:9096
```

In production replace ACSS_EXTERNAL_HOST_ADDR=localhost with the server url and set PATH_TO_ACSS_SERVICES_ROOT to the location of the cloned ml-pipe-services repository.
The environment values ACSS_DB_PW and ACSS_DB_USER define the credentials for the databases used by ACSS.

You can check if all core services are started correctly by executing:

```
docker-compose -p pipeline ps
```
In the project root folder.

## Stop Core Services
To stop de Core Services just run
``` bash
make down
```

## Tests locally
Note: Docker and docker-compose => 2.80 is required to run tests locally

Run all tests:
```
make tests ENV_FILE=.env
```
Run end to end tests:
```
make e2e-tests ENV_FILE=.env
```
Run integration tests:
```
make integration-tests ENV_FILE=.env
```
Run unit tests
```
make unit-tests ENV_FILE=.env
```
## Additional Stuff
### Maxwell
Log in via ssh to max-wgs.desy.de

Install python 3.8.8 
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh
sh Anaconda3-2021.05-Linux-x86_64.sh
export PATH=$HOME/anaconda3/bin:$PATH
```

### PyTine and K2I2K_os on Machine PETRA III
The machine observer and controller for PETRA III are using the PetraAdapter which is using the libs PyTine and K2I2K_os.
The Path to this libs have to be added to the PYTHONPATH. 

For PyTine have a look at https://confluence.desy.de/display/HLC/Developing+with+Python. 

K2I2K_os can be cloned via git from: 
```bash
git clone https://username@stash.desy.de/scm/pihp/petra3.optics.tools.git
```


### Jupyter notebook
To use KafkaPipeClient in a Jupyter notebook you need to add the virtual environment to Jupyter.

First activate the python virtual environment.

For Pipenv
``` bash
pipenv shell
```

Start the jupyter notebook:
```bash
pip install --user ipykernel
```

Note: You have to add the virtual environment to jupyter. First, activate the virtual environment. Then run:
```bash
python -m ipykernel install --user --name=<myenv> 
```
