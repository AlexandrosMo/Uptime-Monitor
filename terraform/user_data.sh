#!/bin/bash
set -eux
dnf update -y
dnf install -y docker
systemctl enable --now docker

REGION="${region}"
REPO="${repo}"
NAME="${name}"

aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REPO"

IMAGE="$REPO:latest"
docker pull "$IMAGE" || true

mkdir -p /opt/$NAME/data
cat >/etc/systemd/system/${NAME}.service <<EOF
[Unit]
Description=$NAME container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm \
  --name $NAME \
  -p 80:8000 \
  -e PORT=8000 \
  -e DB_PATH=/data/uptime.db \
  -e LOG_LEVEL=INFO \
  -v /opt/$NAME/data:/data \
  $IMAGE
ExecStop=/usr/bin/docker stop $NAME

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now ${NAME}.service
