#!/bin/bash
# This is an example script for running openFPGAloader in a docker
# container.
#
# Prior to running this script, the docker image should have been
# created with something like:
#  docker build -t qlitex -f qlitex.docker

# Disable network
DPARAM="--network none"

# Map "USB Blaster" into container
USBBLASTER_VIDPID="09fb:6001"
BD="`lsusb -d ${USBBLASTER_VIDPID}`" # "Bus 003 Device 043: ..."
BUS="${BD:4:3}"
DEV="${BD:15:3}"
DPARAM="${DPARAM} --device=/dev/bus/usb/${BUS}/${DEV}"

# Obtain directory of the software (based on the location of this
# script) and map the local firmware directory to /project .
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
DPARAM="${DPARAM} -v ${SRCDIR}:/project:ro"

# Create build directory
mkdir -p "${SRCDIR}/build"
DPARAM="${DPARAM} -v ${SRCDIR}/build:/build"
DPARAM="${DPARAM} -w /build"

# Run Quartus in container
docker run -it --rm ${DPARAM} localhost/qlitex openFPGALoader -c usb-blaster "$@"
