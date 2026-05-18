#!/bin/bash
set -e

echo 'Starting frontend build...'
cd /home/ubuntu/erp/frontend

echo 'Installing dependencies...'
npm install

echo 'Building production bundle...'
npm run build

echo 'Build completed successfully!'
