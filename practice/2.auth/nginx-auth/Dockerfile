FROM python:2.7-slim

RUN set -xe && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends libsasl2-dev \
                                               python-dev \
                                               libldap2-dev \
                                               gcc \
                                               libssl-dev && \
    pip install --no-cache-dir python-ldap \
                               cookies && \
    apt-get purge -y --auto-remove libsasl2-dev \
                                   python-dev \
                                   gcc \
                                   libssl-dev && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY nginx-ldap-auth-daemon.py .

EXPOSE 8888/tcp

ENTRYPOINT ["python", "nginx-ldap-auth-daemon.py"]
