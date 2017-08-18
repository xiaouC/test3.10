#!/bin/sh
root=../../win32_client
echo $root
rm -r lua
mkdir -p lua/config lua/utils lua/win/Fight
#for name in C_UNITS C_LARGE_UNITS C_SKILL_CONFIG C_SKILL_EFFECT_CONFIG C_BUFF; do
#for name in C_LARGE_UNITS; do
#    cp $root/config/$name.lua lua/config/
#done
cp $root/config/*.pb lua/config/
for name in string table enums stack class random_number protobuf; do
    cp $root/utils/$name.lua lua/utils/
done
cp $root/win/Fight/verify_*.lua lua/win/Fight
for name in fightConst fight_debug; do
    cp $root/win/Fight/$name.lua lua/win/Fight/
done
