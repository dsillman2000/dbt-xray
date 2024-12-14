# Usage: source connect-docker.sh
# Allows you to run `poetry run dbt run` from host machine.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DOTENV=$SCRIPT_DIR/.env
source $DOTENV
export POSTGRES_HOST=0.0.0.0
export DBT_DB=$DBT_DB
export POSTGRES_PORT=$POSTGRES_PORT
export DBT_USER=$DBT_USER
export DBT_PASSWORD=$DBT_PASSWORD
export LANDING_SCHEMA=$LANDING_SCHEMA