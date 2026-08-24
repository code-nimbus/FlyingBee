#!/bin/bash

set -ex

# Update and install dependencies
apt-get update -y
apt-get install -y docker.io docker-compose git

# Add the current user to the docker group
usermod -aG docker $(whoami)

# Start and enable the docker service
systemctl start docker
systemctl enable docker

# Clone the FlyingBee repository

REPO_DIR="/FlyingBee"


git clone "https://github.com/code-nimbus/FlyingBee.git" "$REPO_DIR"
    

# Create the .env file 


cat > "$REPO_DIR/backend/.env" <<EOF
MAIL_USERNAME=${mail_username}
MAIL_PASSWORD=${mail_password}
MAIL_FROM=${mail_from}
MAIL_PORT=${mail_port}
MAIL_SERVER=${mail_server}
ACCESS_TOKEN_EXPIRE_MINUTES=${access_token_expire_minutes}
SECRET_KEY=${secret_key}
ALGORITHM=${algorithm}
TRAVELPAYOUTS_API_KEY=${travelpayouts_api_key}
TRAVELPAYOUTS_MARKER=${travelpayouts_marker}
TRAVELPAYOUTS_BASE_URL=${travelpayouts_base_url}
DUFFEL_API_TOKEN=${duffel_api_token}
EOF

# Run the docker-compose command to build and start the containers
cd "$REPO_DIR/backend"
docker compose up -d --build
# fi
