#!/bin/bash
# This is an example script for running the "Quartus" graphical
# interface in a docker container.  This is an example - you may need
# to copy this file and modify it so that it works in your
# environment.
#
# Prior to running this script, the docker image should have been
# created with something like:
#  docker build -t qlitex -f qlitex.docker

# Map x-windows socket into container
DPARAM="--network none"
DPARAM="${DPARAM} -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=${DISPLAY}"

# If passing the x-windows socket doesn't work, then the following may
# work instead:
#xhost +localhost
#DPARAM="${DPARAM} --net=host -e DISPLAY=host.docker.internal:0"

# Obtain directory of the software (based on the location
# of this script) and map the local firmware directory to /build .
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
DPARAM="${DPARAM} -v ${SRCDIR}:/project:ro"
DPARAM="${DPARAM} -v ${SRCDIR}/build:/build -w /build"

# Run Quartus in container
docker run -it --rm ${DPARAM} localhost/qlitex quartus "$@"

# If "xhost +localhost" was used above then reenable security here.
#xhost -localhost
