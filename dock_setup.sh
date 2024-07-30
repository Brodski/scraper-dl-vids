#!/bin/bash

if [ "$ENV" = "dev" ] || [ "$ENV" = "local" ]; then
    git fetch origin dev ;
    git checkout dev ;
    git reset --hard origin/dev ; 
    git pull origin dev --force ;
    echo "Running in development mode"
else
    git checkout master ;
    git reset --hard origin/master ;
    git pull origin master --force ; 
    echo "Running in production mode"
fi

# exec "$@"
