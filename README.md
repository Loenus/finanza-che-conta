[Python-telegram-bot documentation](https://github.com/python-telegram-bot/python-telegram-bot/wiki) <br>
[Job Queue documentation](https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html)

TODO:
- add timezone (tramite env per privacy magari)
- aggiungendo una richiesta direttamente all'articolo, potrei fare in modo di fare uscire anche la pubblicazione ufficiale (non provvisoria) sapendo esattamente il giorno in cui uscirà (a meno di ritardi??? gestire l'errore nel caso)
- aggiungere https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html (giornalmente)


### how to commit (for Docker Hub Image)

prima fare la commit normale,
poi creare il tag (git tag v*.*.*) da pushare successivamente (git push origin v*.*.*)
Inserire sempre X.Y.Z in cui
<code>major or X</code> can be incremented if there are major changes in software, like backward-incompatible API release.
<code>minor or Y</code> is incremented if backward compatible APIs are introduced.
<code>patch or Z</code> is incremented after a bug fix.