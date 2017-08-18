python -mplayer.define
python -mpet.define
python -muser.define
python -mmail.define
python -mfaction.define
python -mequip.define

cython player\c_player.pyx
cython pet\c_pet.pyx
cython user\c_user.pyx
cython mail\c_mail.pyx
cython faction\c_faction.pyx
cython equip\c_equip.pyx

python setup.py build_ext --inplace
