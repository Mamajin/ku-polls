FROM python:3-alpine
# An argument needed to be passed
ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=Asia/Bangkok
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}


COPY ./requirements.txt .
# Install dependencies in Docker container
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Apply fixtures
RUN chmod +x ./entrypoint.sh

EXPOSE 8000
# Run application
CMD [ "./entrypoint.sh" ]