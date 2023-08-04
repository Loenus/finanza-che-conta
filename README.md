<p align="center">
  <img src="logo.png" alt="Logo" height=170 vspace="1">
</p>
<h1 align="center">Finanza che conta<br><em>Telegram Bot</em></h1>

<p align="center">
  <img src="https://img.shields.io/github/repo-size/Loenus/finanza-che-conta" alt="GitHub repo size"/>
  <a href="https://github.com/Loenus/finanza-che-conta/actions/workflows/docker-image.yml"><img src="https://github.com/Loenus/finanza-che-conta/actions/workflows/docker-image.yml/badge.svg" alt="Docker Image CI"/></a>
</p>

<div align="center">
  <a href="https://t.me/finanzacheconta"><strong>Telegram Bot Channel</strong></a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://github.com/Loenus/finanza-che-conta/issues/new">Issues</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://github.com/Loenus/finanza-che-conta/issues/1">Roadmap</a>
  <br />
</div>

## Why

La finanza è un *gioco a lungo termine*, ma ci sono alcuni indicatori più concreti, attuali e tangibili di altri. Però, chi ha tempo di monitorarli con regolarità e ricordarsi di farlo? Immagina questo: un bot che manda massimo due notifiche a settimana su un'app che già utilizzi. Lascia che la tecnologia lavori per te, così puoi concentrarti sul prendere decisioni informate con il minor sforzo possibile. Arrivederci FOMO, buongiornissimo caffè!

## What it does

Periodicamente (circa ogni due settimane, quando esce il comunicato stampa della ISTAT) manda un messaggio su telegram indicando il cambiamento dell'inflation rate in Italia; inoltre, ogni lunedì manda un messaggio con il valore dell'€STR.

## How to self host

È possibile trovare la docker image di questa repo su [DockerHub](https://hub.docker.com/r/loenus/finanza-che-conta).<br>
Quindi sarà sufficiente avere una macchina linux su cui eseguire le istruzioni riportate su DockerHub.

Ricordarsi di creare o settare le [variabili d'ambiente](https://docs.docker.com/engine/reference/commandline/run/#env), elencate nel file `.env.sample` <br>
A tal proposito, per controllare quali TimeZone sono disponibili, eseguire in python: 
```python
import zoneinfo
print( zoneinfo.available_timezones() )
```
