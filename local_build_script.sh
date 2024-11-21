#!/bin/bash

# Carica le variabili dal file .env (se esiste)
if [ -f .env ]; then
  # Estrai il valore della variabile ENV
  ENV_VALUE=$(grep -E "^ENV=" .env | cut -d '=' -f2)

  # Verifica se ENV è definita e se il suo valore è diverso da "local"
  if [ -z "$ENV_VALUE" ] || [ "$ENV_VALUE" != "local" ]; then
    echo "Variabile ENV mancante o non valorizzata come 'local'. Non eseguo lo script per testare."
    exit 0
  fi
fi

# Build the image
docker build -t my-app .

# Run the container
docker run --rm my-app

# Remove the image
docker rmi my-app
