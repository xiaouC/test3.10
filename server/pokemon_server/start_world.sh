#!/bin/bash
argparse(){
    argparser=$(mktemp)
    cat > "$argparser" <<EOF
from __future__ import print_function
import sys
import argparse
import os
class MyArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        """Print help and exit with error"""
        super(MyArgumentParser, self).print_help(file=file)
        sys.exit(1)
parser = MyArgumentParser(prog=os.path.basename("$0"))
EOF

    # stdin to this function should contain the parser definition
    cat >> "$argparser"

    cat >> "$argparser" <<EOF
# args = parser.parse_args()
for arg in [a for a in dir(args) if not a.startswith('_')]:
    value = getattr(args, arg, None)
    if value is None:
        value = ''
    print('{}="{}";'.format(arg, value))
EOF

    # Define variables corresponding to the options if the args can be
    # parsed without errors; otherwise, print the text of the error
    # message.
    if python "$argparser" "$@" &> /dev/null; then
        eval $(python "$argparser" "$@")
        retval=0
    else
        python "$argparser" "$@"
        retval=1
    fi

    rm "$argparser"
    return $retval

}

if echo $0 | grep -q argparse.bash; then
    cat <<FOO
#!/bin/bash
source \$(dirname \$0)/argparse.bash || exit 1
argparse "\$@" <<EOF || exit 1
parser.add_argument('infile')
parser.add_argument('-o', '--outfile')
EOF
echo "INFILE: \${INFILE}"
echo "OUTFILE: \${OUTFILE}"
FOO
fi


argparse "$@" <<EOF || exit 1
import os
import errno
import os.path
parser.add_argument("--port", required=True, type=int)
parser.add_argument("--managehost", required=True, type=str)
parser.add_argument("--manageport", required=True, type=int)
parser.add_argument("--backdoorport", required=True, type=int)
parser.add_argument("--src",  required=True, type=str)
parser.add_argument("--game", required=True, type=str)
args = parser.parse_args()
args.src = os.path.abspath(args.src)
args.game = os.path.abspath(args.game)
EOF

docker run --user="$(id -u):$(id -g)" \
           -v $src:/opt/src \
           -v $game:/opt/game \
           -e "DOCKER_MANAGEHOST=$managehost" \
           -p $port:$port \
           -p $managehost:$manageport:$manageport \
           -p 127.0.0.1:$backdoorport:$backdoorport\
           -d pokemon:lastest "python" "-m" "world.main"\
