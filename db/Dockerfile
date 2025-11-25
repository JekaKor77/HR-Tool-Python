FROM postgres:15
COPY init.sql.template /docker-entrypoint-initdb.d/init.sql.template
CMD ["/bin/bash", "-c", "envsubst < /docker-entrypoint-initdb.d/init.sql.template > /docker-entrypoint-initdb.d/init.sql && docker-entrypoint.sh postgres"]
RUN apt-get update && apt-get install -y gettext-base
