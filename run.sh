#! /bin/bash
gnome-terminal --window -- \
gnome-terminal --tab --title="IDF OSOM.Codex (Sandbox Edition)" -e 'bash -c "source .venv/bin/activate; cd dev; python manage.py runserver"' \
gnome-terminal --tab --title="NPM" -e 'bash -c "npm --prefix ./lib run build:dev"' \
