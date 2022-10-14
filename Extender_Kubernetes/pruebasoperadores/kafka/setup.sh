export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
operator-sdk olm install #Instalo el operator lifecycle manager.
kubectl create -f https://operatorhub.io/install/strimzi-kafka-operator.yaml #Instalo el operator de strimzi para kafka.
# kubectl apply -R -f . # Esto no puede hacerse hasta que se instale el operator, habria que esperar.