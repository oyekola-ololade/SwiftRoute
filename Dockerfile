FROM python:3.12-alpine

WORKDIR /app
COPY swiftroute ./swiftroute

RUN mkdir -p /app/data && adduser -D -u 10001 swiftroute \
    && chown -R swiftroute:swiftroute /app

USER swiftroute
EXPOSE 8080

CMD ["python", "-m", "swiftroute.api", "--host", "0.0.0.0", "--port", "8080"]
