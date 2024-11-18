copy Guardium "C:\Guardium"
cd "C:\Guardium"
freshclam
clamd --install-service
net start clamd