# syntax=docker/dockerfile:1
FROM python:3.12-bookworm

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh
RUN /root/.cargo/bin/uv pip install --system --no-cache supervisor

WORKDIR /user_pinger

COPY requirements.txt /user_pinger/requirements.txt
RUN /root/.cargo/bin/uv pip install --system --no-cache -r /user_pinger/requirements.txt

COPY --link supervisord.conf *.py sql templates www /user_pinger/

CMD [ "supervisord", "-c", "/user_pinger/supervisord.conf" ]
