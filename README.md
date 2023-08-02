### Link utili

[Python-telegram-bot documentation](https://github.com/python-telegram-bot/python-telegram-bot/wiki) <br>
[Job Queue documentation](https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html) <br>
[Markdown Extended](https://www.markdownguide.org/extended-syntax/#fenced-code-blocks)

<hr>

### TODO

- [ ] aggiungendo una richiesta direttamente all'articolo, potrei fare in modo di fare uscire anche la pubblicazione ufficiale (non provvisoria) sapendo esattamente il giorno in cui uscirà (a meno di ritardi??? gestire l'errore nel caso)
- [ ] aggiungere https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html (giornalmente)
- [ ] add timezone

<hr>

### how to commit (for Docker Hub Image)

prima fare la commit normale, poi creare il tag (git tag vX.Y.Z) da pushare successivamente (git push origin vX.Y.Z). <br>
Inserire sempre X.Y.Z, in cui
- `major or X` can be incremented if there are major changes in software, like backward-incompatible API release.
- `minor or Y` is incremented if backward compatible APIs are introduced.
- `patch or Z` is incremented after a bug fix.