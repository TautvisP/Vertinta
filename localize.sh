activate_env="source .venv/bin/activate;"
makemessages="python manage.py makemessages -l en;"
compilemessages="python manage.py compilemessages;"


gnome-terminal --window -- \
gnome-terminal --tab --title="Localization" -e "bash -c '${activate_env} cd dev; ${makemessages} ${compilemessages} read -n 1 -s -r -p \"Press any key to continue\"'" \

