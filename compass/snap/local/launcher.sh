#!/bin/bash
# Wrapper script for mongodb-compass applications to be run with restricted privileges

connect_text="MongoDB Compass requires access to the password-manager-service interface

To connect the interface, in a terminal run:

<tt><b>sudo snap connect mongodb-compass:password-manager-service</b></tt>"
if ! snapctl is-connected password-manager-service; then
  echo "password-manager-service not connected, please connect with:"
  echo "sudo snap connect mongodb-compass:password-manager-service"
  zenity --title "MongoDB Compass: Connect to Password Manager Service" --info --text "$connect_text" --width 600
  exit
fi


WAYLAND_OPTS=""

if [ -n "$WAYLAND_DISPLAY" ] && [ -z "$DISABLE_WAYLAND" ]; then
  WAYLAND_OPTS="--enable-features=WaylandWindowDecorations,WebRTCPipeWireCapturer,UseOzonePlatform --ozone-platform-hint=auto"
fi

pushd "${SNAP}" > /dev/null

exec "${SNAP}/usr/bin/mongodb-compass" --ignore-additional-command-line-flags --no-sandbox --disable-seccomp-filter-sandbox $WAYLAND_OPTS "$@"

popd > /dev/null
