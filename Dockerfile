ARG NODE_VERSION=22.23.5
ARG UMAMI_VERSION=3.5.0

FROM node:${NODE_VERSION}-alpine AS patched-node

FROM ghcr.io/umami-software/umami:${UMAMI_VERSION}

ARG NODE_VERSION

COPY --from=patched-node \
    /usr/local/bin/node \
    /usr/local/bin/node

ENV NODE_VERSION=${NODE_VERSION}

RUN test "$(node --version)" = "v${NODE_VERSION}"
