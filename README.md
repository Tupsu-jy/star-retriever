# star-retriever

Retrieves starred github repos based with github oauth. Done using fastapi. It has 2 endpoints first one of which redirects the user to github oauth login and then to callback route which gets the repos from github api and then returns them to user in neat json. It has sphinx documentation at docs/build and also
swagger ui
http://localhost:8000/docs

redoc
http://localhost:8000/redoc

are available if its run in dev mode.

docker and docker compose is used.

the project is in backend folder because there was an aspiration to do both frontend and backend but i needed to work on my thesis. please be aware that any imperfections that might theoretically possibly be in the code would not be there if i had more time to spend on this. i think its pretty clean code overall though

## configuration

there are 4 env variables but 2 of them have default values allowing you to start the project without defining them. The 2 envvariables that have to defined are CLIENT_SECRET and CLIENT_ID. These can be defined in .env file in project root from where docker compose will pick them up.

example .env:
CLIENT_ID=your client id
CLIENT_SECRET=your client secret

if these 2 are not defined the app will not start. they are related to github OAuth apps. https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app

you can also config it by including the env variables in the docker compose start command

CLIENT_ID=your_client_id CLIENT_SECRET=your_client_secret docker-compose -f docker-compose-dev.yml up --build

also by adding this launch config to your .vscode/launch.json you can attach the vsc debugger to the docker container

    {
      "name":"Python Debugger: Remote Attach",
      "type":"debugpy",
      "request":"attach",
      "connect":{"host":"localhost","port":5678},
      "logToFile": true,
      "justMyCode": true,
      "pathMappings":[
        {
          "localRoot":"${workspaceFolder}/backend",
          "remoteRoot": "/usr/src/app"
        }
      ]
    },

## running

the project is meant to be started using docker compose. for that purpose there are 2 docker compose files. one for production environment and one for development environment

prod version can be started with command:
docker-compose -f docker-compose-prod.yml up --build

this mode means that error logs are more limited and that the api documentation is not available to user and that reload is not used for uvicorn

dev version can be started with command:
docker-compose -f docker-compose-dev.yml up --build

this mode means that error logs are more informative, that the local and container code are mapped so that local changes are reflected inside container, there is debugpy listening on port 5678 to enable debugger attachment to container and that uvicorn reload is enabled so that changes are instanlty reflected in running instance and also api documentation is available at routes mentioned in introduction

## testing

for manual "testing" after starting the api just go to url http://localhost:8000/api/getStarredRepos in browser and you will be redirected to github login and then you will get the starred repos

testing can be done by running command pytest in backend folder, provided that pytest is installed. also github actions is included and the tests are run on every push. nothing is really done with the result of those tests in github actions atm but im well aware of how to use those actions to implement proper integration testing and to prevent bad merges to main branch
