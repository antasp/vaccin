# Letar efter lediga vaccinationstider i Region Örebro

Pollar API var 15:e minut och skickar email med lediga tider.

__OBS! Bokning ska endast göras av de som ingår i nuvarande fas!__

## Konfiguration

config.ini

```ini
[smtp]
email=bla@bla.se
password=abc123

[receivers]
list=kalle@bla.se,pelle@bla.se
```
## Historisk data

Loggning till data.csv görs vid varje pollning. Visualisering av denna data finns [här](https://antasp.github.io/vaccin/).
