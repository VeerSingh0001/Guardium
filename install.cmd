copy Guardium "C:\Program Files\Guardium"
cd "C:\Program Files\Guardium"
freshclam
clamd --install-service
net start clamd