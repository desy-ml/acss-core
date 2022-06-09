FROM acss/acss-base:latest as build-python-env

#build python env
RUN mkdir -p /pipe
COPY Pipfile /pipe
COPY Pipfile.lock /pipe
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv
RUN cd pipe && mkdir .venv && pipenv install --dev

# build acss_core lib from src
ADD README.md /pipe
ADD setup.py /pipe
ADD pyproject.toml /pipe
ADD LICENSE /pipe
ADD src /pipe/src
RUN cd pipe && .venv/bin/python3 setup.py install

FROM acss/acss-base:latest
COPY --from=build-python-env /pipe/.venv /pipe/.venv
COPY src /pipe/src