#!/usr/bin/env bash
apt-get update
apt-get install -y \
    python3-dev \
    python3-pip \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev

pip install --upgrade pip
pip install -r requirements.txt