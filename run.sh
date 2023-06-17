#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR=$(cd $(dirname $0); pwd)
export WORK_DIR=${SCRIPT_DIR}

# echo "SCRIPT_DIR: ${SCRIPT_DIR}"
python -m venv ${SCRIPT_DIR}/.venv
source ${SCRIPT_DIR}/.venv/bin/activate
pip install -r ${SCRIPT_DIR}/requirements.txt
python ${SCRIPT_DIR}/main.py

