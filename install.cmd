cd "C:\Guardium"
freshclam
clamd --install-service
sc config clamd start= auto
sc start clamd

