# corn_api

## Create Images

    docker build -t corn_serv:latest .

## Run images

    docker run -d -p 8006:8006 --name corn_serv corn_serv:latest
    docker run -d --name corn_serv -p 8006:8006 corn_serv:latest


# New Revise
## Authentication Backend

    http://localhost:8004/login
    header : { Content-Type:application/json}
    {
        "username": "<user>",
        "password": "<password>"
    }

## Authentication database

    http://localhost:3000/api/users/exists?username=<username>


## Unit test
    python -m unittest test_db_operations.py