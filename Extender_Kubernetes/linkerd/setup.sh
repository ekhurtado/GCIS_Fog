export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
linkerd check --pre
echo ######### INSTALANDO LINKERD EN EL CLUSTER ########
linkerd install | kubectl apply -f -
export PATH=$PATH:/home/julen/.linkerd2/bin
echo ######### COMPROBANDO LA INSTALACION ########
linkerd check
echo ######### INYECTO EL PROXY DE LINKERD ########
kubectl get -l app=kafka-test deploy -o yaml \
  | linkerd inject - \
  | kubectl apply -f -
echo ######### INSTALO LA HERRAMIENTA DE VISUALIZACION ########
linkerd viz install | kubectl apply -f -
linkerd check
linkerd viz dashboard &
