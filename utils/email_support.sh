#!/bin/bash


red='\e[1;31m\e[0m'
green='\e[1;32m\e[0m'
yellow='\e[1;33m\e[0m'
blue='\e[1;34m\e[0m'
magenta='\e[1;35m\e[0m'
cyan='\e[1;36m\e[0m'



echo -e "Please provide" '\e[1;31mMAIL_USERNAME\e[0m' 'and' '\e[1;31mMAIL_PASSWORD\e[0m'
read -p "Mail username: " username
read -s -p "Mail password: " password
echo -ne "\n"

export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=587
export MAIL_USE_TLS=1


echo -e '[\e[1;32m*\e[0m]' 'Exporting \e[1;31mMAIL_USERNAME\e[0m' 'and' '\e[1;31mMAIL_PASSWORD\e[0m'
export MAIL_USERNAME=$username
export MAIL_PASSWORD=$password
