init_user() {
    # Create a new postgres database called "$DBT_DB"
    createdb -e $DBT_DB
    createuser --no-password --superuser -e $DBT_USER
}

init_landing() {
    # Create a new schema called "$LANDING_SCHEMA"
    psql -d $DBT_DB -U $DBT_USER -c "CREATE SCHEMA $LANDING_SCHEMA;"

    landing_yml="/docker-entrypoint-initdb.d/landing.yml"
    landing_tables=$(yq 'keys' < $landing_yml | cut -d ' ' -f 2)
    for table in $landing_tables; do
        landing_columns=$(yq ".$table | keys" < $landing_yml | cut -d ' ' -f 2)
        landing_types=$(yq ".$table | .[]" < $landing_yml)
        i=1
        stmt="create table $LANDING_SCHEMA.$table ("
        for column in $landing_columns; do
            stmt="$stmt$column $(echo $landing_types | cut -d ' ' -f $i)"
            column_count=$(echo $landing_columns | wc -w)
            ((column_count--))
            if [ $i -le $column_count ]; then
                stmt="$stmt,"
            fi
            ((i++))
        done
        stmt="$stmt);"
        psql -d $DBT_DB -U $DBT_USER -c "$stmt"
    done
}

finalize_user() {
    # Assign password to the user
    psql -d $DBT_DB -U $DBT_USER -c "ALTER USER $DBT_USER WITH PASSWORD '$DBT_PASSWORD';"
}

init_user
init_landing
finalize_user