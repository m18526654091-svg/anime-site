FROM node:20-alpine
WORKDIR /app

# Build args for Docker deployment (overridden by docker-compose.yml).
# .env.local is excluded by .dockerignore, so these defaults are required
# for the Next.js build to produce correct SSR/SSG output.
ARG NEXT_PUBLIC_API_URL=http://backend:8000
ARG NEXT_PUBLIC_SITE_URL=http://localhost:3000
ARG NEXT_PUBLIC_APP_VERSION=1.7.0
ARG NEXT_PUBLIC_APP_BUILD_TIME=unknown
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL
ENV NEXT_PUBLIC_APP_VERSION=$NEXT_PUBLIC_APP_VERSION
ENV NEXT_PUBLIC_APP_BUILD_TIME=$NEXT_PUBLIC_APP_BUILD_TIME

COPY . .
RUN npm ci && npm run build
CMD ["npm","start"]
