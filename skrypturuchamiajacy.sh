#!/bin/bash
cd /home/norb1x/projekty/DISCORDBOT || exit

while true; do
    echo "Uruchamianie bota: $(date)"
    python bot.py
    echo "Proces bota zakończył się. Ponowne uruchomienie za 5 sekund..."
    sleep 5
done
