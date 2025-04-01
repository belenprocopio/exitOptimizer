ARG BUILD_FROM
FROM ${BUILD_FROM}

#instalem python, pip i llibreries que necessitarem
RUN apt update \
    && apt install -y dos2unix python3 python3-pip \
    && pip install --upgrade pip \
    && pip install requests pandas scikit-learn psutil numpy holidays tomli func_timeout schedule plotly

#afegim els fitxers del servidor dins el container de docker
# ADD ./rootfs/server.py .
# ADD ./rootfs/bottle.py .
# ADD ./rootfs/sqlDB.py .
ADD ./rootfs/BESS_lab.py .
ADD ./rootfs/OS_lab.py .
ADD ./rootfs/test_OS.py .
# ADD ./rootfs/download_intern.py .
ADD ./rootfs/download_state.py .
ADD ./rootfs/post_state.py .
ADD ./rootfs/elec_price.py .
# COPY ./rootfs/www /www/
# COPY ./rootfs/images/ /images/
#COPY ./rootfs/optimalScheduler /optimalScheduler/

COPY config.yaml config.yaml

# posem l'script d'inici i li donem permisos de execucio
COPY ./rootfs/run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
