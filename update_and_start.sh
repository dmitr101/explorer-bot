#!/bin/bash 

#It's stupid and easy to break but it works for now

echo 'Killing the old instance...'
pkill 'python3'
echo 'Pulling the new version...'
git pull
echo 'Starting the bot in background...'
nohup python3 main.py &
