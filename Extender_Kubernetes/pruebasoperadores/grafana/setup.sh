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

# Creas el configmap para el dashboard
kubectl create secret generic oee-secret --from-file=oee-secret.yaml
kubectl create configmap oee-config-map --from-file=oee_dashboard.json

# Install Grafana
#helm install grafana-gcis --set admin.userkey=admin \
#     --set admin.passwordkey=admingcis \
#     grafana/grafana --version 6.48.0
#helm install grafana-gcis --set grafana.config.security.admin_user=admin \
#     --set grafana.config.security.admin_password=admingcis \
#     bitnami/grafana-operator --version 2.7.10 # --set grafana.enabled=false
#helm install grafana-gcis -f values.yaml bitnami/grafana-operator
helm install grafana-gcis --set admin.user=admin \
     --set admin.password=admingcis \
     --set persistence.enabled=true \
     --set dashboardsProvider.enabled=true \
     --set datasources.secretName=oee-secret \
     bitnami/grafana --version 8.2.21 -f values.yaml

#kubectl apply -f influx-data-source.yaml