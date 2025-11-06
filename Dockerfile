FROM debian:trixie

RUN apt update
RUN apt install -y make git procps sudo ca-certificates nginx ssl-cert uwsgi uwsgi-plugin-python3 python3-venv munin munin-node

ENV VIRTUAL_ENV="/opt/homesite/venv"
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:/usr/sbin:/usr/bin:/sbin:/bin"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

ARG DOCKER_WORK_DIR
RUN mkdir -p ${DOCKER_WORK_DIR}
WORKDIR ${DOCKER_WORK_DIR}

RUN mkdir -p /opt/homesite
RUN ln -s ${DOCKER_WORK_DIR} /opt/homesite/repo
RUN ln -s ${DOCKER_WORK_DIR}/data /opt/homesite/data

# Nginx
RUN echo 'ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;' > /etc/nginx/conf.d/ssl.conf
RUN echo 'ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;' >> /etc/nginx/conf.d/ssl.conf
RUN ln -s /opt/homesite/repo/deployment/nginx.conf /etc/nginx/sites-enabled/app.conf

COPY pyproject.toml pyproject.toml
COPY homesite homesite
RUN pip install --no-cache-dir --editable '.[dev]'

# Add user matching local uid/gid
ARG USER_UID
ARG USER_GID
RUN groupadd --gid ${USER_GID} homesite
RUN useradd --uid ${USER_UID} --gid ${USER_GID} --system --shell /usr/sbin/nologin --home /opt/homesite/data homesite
RUN echo "homesite ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER homesite
EXPOSE 443
ENTRYPOINT ["/bin/make"]
