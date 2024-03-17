#!/bin/bash

if [ "$ENV" = "dev" ] || [ "$ENV" = "local" ]; then
    git reset --hard origin/dev ; 
    git pull origin dev --force ;
    git checkout dev ;
    echo "Running in development mode"
else
    git reset --hard origin/master ;
    git pull origin master --force ; 
    echo "Running in production mode"
fi

# exec "$@"
