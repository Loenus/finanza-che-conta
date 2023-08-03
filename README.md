### Link utili

[Python-telegram-bot documentation](https://github.com/python-telegram-bot/python-telegram-bot/wiki) <br>
[Job Queue documentation](https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html) <br>
[Docker Image Uploading](https://dev.to/derlin/lets-code-a-reusable-workflow-for-building-state-of-the-art-multi-platform-docker-images-with-github-action-5cj9#tags)<br>
[Docker Image Uploading 2](https://docs.docker.com/build/ci/github-actions/manage-tags-labels/) <br>
[Markdown Extended](https://www.markdownguide.org/extended-syntax/#fenced-code-blocks) <br>

Per controllare quali TimeZone sono disponibili, eseguire in python: 
```
import zoneinfo
zoneinfo.available_timezones()
```

<hr>

### TODO

- [X] aggiungendo una richiesta direttamente all'articolo, potrei fare in modo di fare uscire anche la pubblicazione ufficiale (non provvisoria) sapendo esattamente il giorno in cui uscirà (gestire l'errore nel caso di ritardi di pubblicazione)
- [X] add timezone
- [ ] aggiungere https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html (giornalmente)
  - un job settimanale (lunedì) che ne comunica il valore aggiornato (altri dati no? magari in combinazione con il secondo, segnala l'andamento settimanale..) 
  - un job quotidiano che controlla l'oscillazione senza comunicarla in chat. Se negli ultimi giorni (quanti?) la variazione è elevata, lo segnala in chat. (Come? controlla la memoria persiste tra i jobs)
- [ ] Valutare se salvarsi i dati in un file della repo (per eventuale resoconto periodico)
