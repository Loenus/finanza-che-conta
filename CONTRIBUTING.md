### How to commit for building Docker Hub Image

prima fare la commit normale, poi creare il tag ( `git tag vX.Y.Z` ) da pushare successivamente ( `git push origin vX.Y.Z` ). <br>
Inserire sempre X.Y.Z, in cui
- `major or X` can be incremented if there are major changes in software, like backward-incompatible API release.
- `minor or Y` is incremented if backward compatible APIs are introduced.
- `patch or Z` is incremented after a bug fix.

<br>

### How to test in local

Dentro il .env, aggiungi una variabile del tipo `ENV=local` così che i due scheduler partano una volta sola, senza schedulazione. 

Per farlo partire in locale e testarlo, aprire un terminale nella root del progetto ed eseguire, ad esempio:
```
> /local_build_script.sh
```
In questo modo sulla macchina non rimarrà traccia dell'immagine docker eseguita.

Per testarlo però sarà inoltre necessario creare su telegram un channel, e inserire il @nomeDelCanale come CHANNEL_ID nel .env; poi aprire la chat con BotFather e creare un newbot, e da lì prendersi il token da settare nel .env; infine, dal channel Telegram creato, andare su Subscribers>Add Subscribers e cercare il bot telegram creato e aggiungerlo.

<br>
<hr>

### Link utili

[Python-telegram-bot documentation](https://github.com/python-telegram-bot/python-telegram-bot/wiki) <br>
[Job Queue documentation](https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html) <br>
[Docker Image Uploading](https://dev.to/derlin/lets-code-a-reusable-workflow-for-building-state-of-the-art-multi-platform-docker-images-with-github-action-5cj9#tags)<br>
[Docker Image Uploading 2](https://docs.docker.com/build/ci/github-actions/manage-tags-labels/) <br>
[Markdown Extended](https://www.markdownguide.org/extended-syntax/#fenced-code-blocks) <br>

