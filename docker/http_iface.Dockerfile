FROM  acss/acss-base-server

COPY docker-compose.yaml pipe/

COPY src/ pipe/src/


WORKDIR /pipe