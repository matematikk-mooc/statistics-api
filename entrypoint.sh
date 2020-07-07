#!/usr/bin/env bash
# These commands are run as root
/usr/sbin/sshd
su appuser -c "./start_web_app.sh"
