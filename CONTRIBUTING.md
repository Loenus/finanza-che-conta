### How to commit for building Docker Hub Image

prima fare la commit normale, poi creare il tag ( `git tag vX.Y.Z` ) da pushare successivamente ( `git push origin vX.Y.Z` ). <br>
Inserire sempre X.Y.Z, in cui
- `major or X` can be incremented if there are major changes in software, like backward-incompatible API release.
- `minor or Y` is incremented if backward compatible APIs are introduced.
- `patch or Z` is incremented after a bug fix.