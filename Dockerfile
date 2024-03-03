FROM python:3.11 AS build
WORKDIR /build
RUN apt-get update
RUN apt-get install build-essential
COPY requirements.txt .
ENV VIRTUAL_ENV=/build/venv
RUN python -m venv venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt
FROM python:3.11 AS final
WORKDIR /app
COPY . .
COPY --from=build /build/venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
CMD ["/app/venv/bin/python", "main.py"]
