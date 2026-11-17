# Patched Umami images: upstream PostgreSQL and SQLite fork

Minimal derivative of the official Umami image, replacing only the Node.js executable to include security fixes.

- Umami base: `ghcr.io/umami-software/umami:3.5.0`
- Node.js source: `node:22.23.5-alpine`
- Resulting local tag: `umami:3.5.0-node22.23.5`
- Runtime user inherited from Umami: `nextjs` / UID `1001`
- Umami application, packaged dependencies, shell scripts, `CMD`, environment (except `NODE_VERSION`), and exposed port remain unchanged.
