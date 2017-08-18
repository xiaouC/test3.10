#!/bin/sh
python -mplayer.define && python -mpet.define && python -muser.define && python -mmail.define && python -mfaction.define && python -m gen_attributes_proto > ../protocol/protocol/attributes.proto
