#!/bin/bash
# This is an example script for running the litex docker container.
#
# Prior to running this script, the docker image should have been
# created with something like:
#  docker build -t qlitex -f qlitex.docker

# Disable network
DPARAM="--network none"

# Map serial device into container
DEVNAME1=/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0
DPARAM="${DPARAM} --device=${DEVNAME1}"
VMDEVNAME=`readlink -f ${DEVNAME1}`

# Obtain directory of the software (based on the location of this
# script) and map the local firmware directory to /project .
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
DPARAM="${DPARAM} -v ${SRCDIR}:/project:ro -w /project"

# Run container
docker run -it --rm ${DPARAM} localhost/qlitex bash -c "source /litex-venv/bin/activate ; /litex-venv/bin/litex_term ${VMDEVNAME} $@"
