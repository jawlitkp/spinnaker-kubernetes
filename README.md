# Details

This is a collection of scripts and a docker-compose file that helps streamline setting up Spinnaker.

`config.py` pulls the the most recent configs from the metapackage config folder. It then injects various config options needed to be able to run each service in an independant container. This is helpful because as config files change, they will not be overwritten and break. Once the configs are injected they are saved to a config folder. These configs are then the "source of truth" if they need to be modified further. `config.py` also builds the most recent version of deck, and sets up settings.js to point to the correct bakery and gate endpoints.

`docker-compose.yml` is a compose file set up to run every service and dependency in a container. It creates a shared config volume for all services to use, as well as a user-defined private network. Services are referenced via a network alias for maximum flexibility.

`launch.py` first runs `config.py`. Once the configs are written, it launches each service container in the correct order. docker-compose only respects container dependencies when they "up" not "running". For example Cassandra takes a few seconds to launch but is not truly "running" for about 15 seconds. `launch.py` uses a container running netstat to pause the next container until it's specified port is listening.

# Dependencies
1. Docker https://www.docker.com/products/overview#/install_the_platform
2. Docker-compose (this is included in the docker for mac beta) https://docs.docker.com/compose/install/
3. Ensure you have 8GB memory provisioned for the vm if using docker for mac beta.

# Instructions
1. Clone repo and checkout the exp-dsb branch, navigate to experimental/docker-dsb
1. Fill out key and secret inside `env.env` and rename to `.env`
2. Run `python launch.py`
3. Once complete a browser will launch with spinnaker running at `http://localhost:9000`
4. To stop all of the Spinnaker services, run `docker-compose down`
