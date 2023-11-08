FROM public.ecr.aws/lambda/python:3.11

# Install pip and other dependencies
RUN pip3 install --upgrade pip \
    && yum install gcc gcc-c++ git -y

RUN git clone --depth 1 --branch v0.9.0 https://github.com/duckdb/duckdb
ENV BUILD_PYTHON=1
ENV GEN=ninja
RUN cd duckdb/tools/pythonpkg && python setup.py install

ENV HOME=/home/aws

RUN mkdir /home/aws && python3 -c "import duckdb; duckdb.query('INSTALL httpfs;');"

# Copy function code
COPY test.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "test.handler" ]