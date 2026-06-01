FROM eclipse-temurin:21-jdk-jammy
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        clang \
        curl \
        g++ \
        golang-go \
        nodejs \
        python3 \
        unzip \
    && rm -rf /var/lib/apt/lists/*

ENV CODEQL_VERSION=2.16.6
RUN mkdir -p /opt/codeql \
 && curl -L "https://github.com/github/codeql-action/releases/download/codeql-bundle-v${CODEQL_VERSION}/codeql-bundle-linux64.tar.gz" \
    -o /tmp/codeql.tgz \
 && tar -xzf /tmp/codeql.tgz -C /opt/codeql --strip-components=1 \
 && rm /tmp/codeql.tgz
ENV PATH="/opt/codeql:${PATH}"
ENV CODEQL_BIN="/opt/codeql/codeql"
ENV PYTHON_BIN="python3"
ENV NODE_BIN="node"
ENV GOFMT_BIN="gofmt"
ENV CLANG_BIN="clang"
ENV CLANGXX_BIN="clang++"

COPY app/openai-bridge/build/install/openai-bridge /opt/openai-bridge

ENV PORT="8080"
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"
ENV OLLAMA_KEEP_ALIVE="5m"

EXPOSE 8080

ENTRYPOINT ["/opt/openai-bridge/bin/openai-bridge"]
