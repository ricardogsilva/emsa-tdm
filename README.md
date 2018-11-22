# EMSA TDMS

## Development

Use the provided docker stack file in order to setup a dev environment. This 
needs to be deployed on a one-host docker swarm because the local code dir
is bind mounted inside the relevant containers.

-  Create a docker swarm locally

-  Build the docker image with:

   ```bash
   docker build -t emsa_tdm -f docker/Dockerfile .
   ```

-  Start a new stack on the swarm

   ```bash
   STACK_NAME=emsa-tdms-dev
   docker stack deploy \
       --prune \
       --compose-file docker/docker-cloud-dev.yml \
       ${STACK_NAME}
   ```
   
-  After a while, the airflow admin should be available at 
   `http://localhost:8080`

-  Open a shell on one of the containers used in the stack

   ```bash
   # first get the names of existing containers on the stack
   docker ps $STACK_NAME
   docker exec -ti <container-name> /bin/bash
   
   ```

-  Test some airflow task in a running container

   ```bash
   # first get the names of existing containers on the stack
   docker ps $STACK_NAME
   docker exec -ti <container-name> airflow test <dag-id> <task-id> <execution-date>
   
   ```
   
   Alternatively, you can open a shell in the container and just call 
   `airflow test` inside it
