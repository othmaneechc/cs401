#!/bin/bash
# create_argocd_app.sh

# Variables - update these according to your setup.
APP_NAME="playlist-app"
REPO_URL="https://github.com/othmaneechc/cs401"
TARGET_REVISION="HEAD"
APP_PATH="k8s" 
DEST_NAMESPACE="othmane" 

# Optionally, log in to ArgoCD if not already logged in.
# Uncomment and update the following line if needed:
# argocd login localhost:31443 --username <username> --password <password> --insecure

# Create the ArgoCD application.
argocd app create "$APP_NAME" \
  --repo "$REPO_URL" \
  --target-revision "$TARGET_REVISION" \
  --path "$APP_PATH" \
  --dest-server "https://kubernetes.default.svc" \
  --dest-namespace "$DEST_NAMESPACE" \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Trigger a sync to deploy the application immediately.
argocd app sync "$APP_NAME"

# Optionally, get the application status.
argocd app get "$APP_NAME"
