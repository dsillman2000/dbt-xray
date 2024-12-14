ARG POSTGRES_VERSION=14
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_PORT

FROM postgres:${POSTGRES_VERSION}
USER ${POSTGRES_USER}

RUN apt-get update && apt-get install -y wget
RUN wget https://github.com/mikefarah/yq/releases/download/v4.44.2/yq_linux_386 -O /usr/bin/yq \
    && chmod +x /usr/bin/yq

COPY dockerfiles/postgres/init /docker-entrypoint-initdb.d/
