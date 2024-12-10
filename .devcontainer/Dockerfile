FROM library/python:3.11-bookworm

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
	build-essential \
	git \
	curl \
	wrk \
	iputils-ping \
	postgresql \ 
	postgresql-contrib \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT [ "/bin/sh", "-c" ,"while true; do sleep 1000; done" ]