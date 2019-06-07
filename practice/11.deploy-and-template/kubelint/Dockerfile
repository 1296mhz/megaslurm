FROM python:3.7-alpine

ARG HELM_VERSION=2.13.0
ARG KUBECTL_VERSION=1.12.5

RUN set -ex && \
    apk --update add --no-cache --virtual build_deps curl && \
    curl -L -s https://storage.googleapis.com/kubernetes-helm/helm-v${HELM_VERSION}-linux-amd64.tar.gz |tar xvz && \
    mv linux-amd64/helm /usr/bin/helm && \
    chmod +x /usr/bin/helm && \
    rm -rf linux-amd64 && \
    curl -L -s https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl -o /usr/bin/kubectl && \
    chmod +x /usr/bin/kubectl && \
    apk del build_deps && \
    rm -rf /var/cache/apk/*

WORKDIR /opt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["./lint.sh"]
