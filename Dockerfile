FROM python:3.8-slim AS compile-image

# Install dependencies.
# rm -rf /var/lib/apt/lists/* cleans up apt cache. See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
     python3-pip \
     locales \
     && rm -rf /var/lib/apt/lists/*


# Configure UTF-8 encoding.
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8 

# Make python3 default
RUN rm -f /usr/bin/python \
     && ln -s /usr/bin/python3 /usr/bin/python

#RUN python -m venv /opt/venv
#ENV PATH="/opt/venv/bin:$PATH"
# Install cirq
RUN pip3 install cirq

#FROM python:3.8-slim AS build-image
#COPY --from=compile-image /opt/venv /opt/venv
## Make sure scripts in .local are usable:
#EXPOSE 8888
