# Para que no falle la instalacion (si no devuelve connection refused error)
kubectl config view --raw > ~/.kube/config

helm delete grafana-gcis

kubectl delete secret oee-secret

kubectl delete configmap oee-11-config-map
kubectl delete configmap oee-22-config-map
kubectl delete configmap  oee-all-config-map
