cd "C:\Guardium"
clamd --install-service
sc config clamd start= auto
sc start clamd
freshclam
