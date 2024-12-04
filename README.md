# 24/25 ASE project

|    Collaborators   |
|:------------------:|
|     Luca Rizzo     |
| Leonardo Scoppitto |
|  Simone Stanganini |
|   Filippo Fornai   |


# Get started

To start the project just clone the repo and:

```bash
cd ase-project/src
docker compose up --build
```
By default the two gateways will listen on port `8080` (normal users) and `8180` (admins). Now you can start locust in the same directory to start the performance testing.
To start the integration tests, stop all running containersm head over `src/integration_tests` and execute the `run_tests.sh` script.
This will start the dockerized version of `newman` along with the service container and will perform the integration tests in a production environment.
To run individual tests, just move inside the service directory of choice and type:

```bash
# From the root directory of the project
cd src/tux_service # replace tux_service with auction_service, authentication_service, gacha_service
bash run_tests.sh
```
This will start the dockerized version of `newman` along with the service container and will perform the unit/feature tests in a mocked/test environment.
