FROM alpine:latest

ENV PYENV_ROOT /opt/pyenv
ENV POETRY_HOME /opt/poetry
ENV PATH /opt/python/bin:/opt/poetry/bin:/opt/pyenv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=en_US.UTF-8

RUN apk add --no-cache --virtual .build-deps \
        abuild \
        bash \
        bash-completion \
        binutils \
        bzip2-dev \
        build-base \
        cmake \
        coreutils \
        curl \
        dpkg-dev dpkg \
        expat-dev \
        extra-cmake-modules \
        findutils \
        gcc \
        gdbm-dev \
        git \
        grep \
        less \
        libc-dev \
        libffi-dev \
        libnsl-dev \
        libressl-dev \
        libstdc++ \
        libtirpc-dev \
        linux-headers \
        make \
        man \
        man-pages \
        mdocml-apropos \
        ncurses-dev \
        pax-utils \
        pciutils \
        postgresql-dev \
        readline-dev \
        shadow \
        sqlite-dev \
        tcl-dev \
        tk \
        tk-dev \
        usbutils \
        util-linux \
        util-linux-dev \
        vim \
        xz-dev \
        zlib-dev; \
    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash; \
    git clone https://github.com/momo-lab/xxenv-latest.git "$(pyenv root)"/plugins/xxenv-latest; \
    # Install the lastest Python 3.8
    pyenv latest install -v; \
    ln -s "${PYENV_ROOT}/versions/$(pyenv latest --print)" /opt/python; \
    pip install --upgrade pip setuptools; \
    pip install wheel; \
    pip install pipenv; \
    pip install tox; \
    pip install tox-pyenv; \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python; \
    echo "export PATH=\"${PATH}\"" >> /root/.profile; \
    echo "export LANG=\"${LANG}\"" >> /root/.profile; \
    echo "export PYENV_ROOT=\"${PYENV_ROOT}\"" >> /root.profile; \
    echo "export POETRY_HOME=\"${POETRY_HOME}\"" >> /root.profile; \
    echo 'source /root/.profile' >> /root/.bashrc; \
    echo 'source /etc/profile.d/bash_completion.sh' >> /root/.bashrc; \
    echo "alias ll='ls -Flap --color'" >> /root/.bashrc; \
    # Install the latest Python 3.7
    pyenv latest install -v 3.7; \
    cd "${PYENV_ROOT}"/versions/$(pyenv latest -p 3.7)/bin && ./pip install --upgrade pip setuptools; \
    cd "${PYENV_ROOT}"/versions/$(pyenv latest -p 3.7)/bin && ./pip install wheel; \
    # Install the latest Python 3.6
    pyenv latest install -v 3.6; \
    cd "${PYENV_ROOT}"/versions/$(pyenv latest -p 3.6)/bin && ./pip install --upgrade pip setuptools; \
    cd "${PYENV_ROOT}"/versions/$(pyenv latest -p 3.6)/bin && ./pip install wheel; \
    # Build bash files
    echo "export PATH=\"${PATH}\"" >> /root/.profile; \
    echo "export LANG=\"${LANG}\"" >> /root/.profile; \
    echo "export PYENV_ROOT=\"${PYENV_ROOT}\"" >> /root.profile; \
    echo "export POETRY_HOME=\"${POETRY_HOME}\"" >> /root.profile; \
    echo 'source /root/.profile' >> /root/.bashrc; \
    echo 'source /etc/profile.d/bash_completion.sh' >> /root/.bashrc; \
    echo "alias ll='ls -Flap --color'" >> /root/.bashrc

CMD ["python"]
