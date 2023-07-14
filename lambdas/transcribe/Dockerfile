FROM public.ecr.aws/lambda/python:3.9
# RUN yum -y update expat curl libblkid libcom_err libcurl libmount libuuid ncurses ncurses-base ncurses-libs glib2 libssh2 && \
#     yum clean all && \
#     rm -rf /var/cache/yum

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt


COPY lambda.py .

CMD ["lambda.lambda_handler"]
