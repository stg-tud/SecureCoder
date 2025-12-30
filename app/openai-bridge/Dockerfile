FROM eclipse-temurin:21-jdk AS builder
WORKDIR /work

COPY . .

RUN chmod +x ./gradlew && ./gradlew --no-daemon :app:openai-bridge:installDist -x test

FROM eclipse-temurin:21-jdk
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

ENV CODEQL_VERSION=2.16.6
RUN mkdir -p /opt/codeql \
 && curl -L "https://github.com/github/codeql-action/releases/download/codeql-bundle-v${CODEQL_VERSION}/codeql-bundle-linux64.tar.gz" \
    -o /tmp/codeql.tgz \
 && tar -xzf /tmp/codeql.tgz -C /opt/codeql --strip-components=1 \
 && rm /tmp/codeql.tgz
ENV PATH="/opt/codeql:${PATH}"

COPY --from=builder /work/app/openai-bridge/build/install/openai-bridge /opt/openai-bridge

ENV PORT="8080"
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"
ENV OLLAMA_KEEP_ALIVE="5m"

EXPOSE 8080

ENTRYPOINT ["/opt/openai-bridge/bin/openai-bridge"]
