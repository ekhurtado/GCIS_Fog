# Install helm
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# Para que no falle la instalacion (si no devuelve connection refused error)
kubectl config view --raw > ~/.kube/config

# Add repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install chart
helm install influxdb-gcis --set auth.admin.password=admingcis \
     --set auth.admin.token=hkC8oAkLLa43mp6DJQ2maXPWTL1d=A9Caa!?onlkyrtWel3iD9wtF32CWBs4cdEzElxu \
     bitnami/influxdb --version 5.4.11
