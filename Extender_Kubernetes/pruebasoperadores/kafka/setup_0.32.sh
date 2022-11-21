# Script para instalar Strimzi v0.32
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
#operator-sdk olm install #Instalo el operator lifecycle manager.

kubectl create ns kafka-ns
kubectl create -f strimzi-cluster-operator-0.32.0.yaml -n kafka-ns
#kubectl create -f https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.32.0/strimzi-cluster-operator-0.32.0.yaml # Instalo el operator de strimzi para kafka.
#kubectl create -f https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.32.0/strimzi-crds-0.32.0.yaml # Instalo los CRDs por si no lo están ya

# kubectl apply -R -f . # Esto no puede hacerse hasta que se instale el operator, habria que esperar.