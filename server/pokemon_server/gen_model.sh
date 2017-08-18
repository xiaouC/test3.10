#!/bin/sh
python -mplayer.define && \
python -mpet.define && \
python -muser.define && \
python -mmail.define && \
python -mfaction.define && \
python -mequip.define && \
python -mgroup.define && \
python -mtower.define && \
find -name "*.pyx"|xargs cython && python setup.py build_ext --inplace
