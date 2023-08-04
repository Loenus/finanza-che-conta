<p align="center">
  <img src="logo.png" alt="Logo" height=170 vspace="1">
</p>
<h1 align="center">Finanza che conta <br> Telegram Bot</h1>

<p align="center">
  <img src="https://img.shields.io/github/repo-size/Loenus/finanza-che-conta" alt="GitHub repo size"/>
  <a href="https://github.com/Loenus/finanza-che-conta/actions/workflows/docker-image.yml"><img src="https://github.com/Loenus/finanza-che-conta/actions/workflows/docker-image.yml/badge.svg" alt="Docker Image CI"/></a>
</p>

## What it does

Periodicamente (circa ogni due settimane, quando esce il comunicato stampa della ISTAT) manda un messaggio su telegram indicando il cambiamento dell'inflation rate in Italia; inoltre, ogni lunedì manda un messaggio con il valore dell'€STR.

## How to self host

È possibile trovare la docker image di questa repo su [DockerHub](https://hub.docker.com/r/loenus/finanza-che-conta).<br>
Quindi sarà sufficiente avere una macchina linux su cui eseguire le istruzioni riportate su DockerHub.

Ricordarsi di creare o settare le [variabili d'ambiente](https://docs.docker.com/engine/reference/commandline/run/#env), elencate nel file `.env.sample` <br>
A tal proposito, per controllare quali TimeZone sono disponibili, eseguire in python: 
```
import zoneinfo
zoneinfo.available_timezones()
```

<br><br>
<hr>

### TODO

- [ ] aggiungere https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html (giornalmente)
  - [X] un job settimanale (lunedì) che ne comunica il valore aggiornato (altri dati no? magari in combinazione con il secondo, segnala l'andamento settimanale..) 
  - [ ] un job quotidiano che controlla l'oscillazione senza comunicarla in chat. Se negli ultimi giorni (quanti?) la variazione è elevata, lo segnala in chat. (Come? controlla la memoria persiste tra i jobs)
- [ ] Valutare se salvarsi i dati in un file della repo (per eventuale resoconto periodico)
