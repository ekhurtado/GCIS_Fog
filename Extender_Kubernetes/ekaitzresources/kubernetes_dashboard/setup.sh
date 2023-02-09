GITHUB_URL=https://github.com/kubernetes/dashboard/releases
VERSION_KUBE_DASHBOARD=$(curl -w '%{url_effective}' -I -L -s -S ${GITHUB_URL}/latest -o /dev/null | sed -e 's|.*/||')
sudo k3s kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml


sleep 3 # espera 3 segundos a que se despliegue
sudo k3s kubectl create -f dashboard.admin-user.yml -f dashboard.admin-user-role.yml
sleep 2
sudo k3s kubectl -n kubernetes-dashboard create token admin-user > token.txt
sleep 1
kubectl patch svc -n kubernetes-dashboard kubernetes-dashboard --type='json' -p '[{"op":"replace","path":"/spec/type","value":"NodePort"}]'
kubectl patch svc -n kubernetes-dashboard kubernetes-dashboard --type='json' -p '[{"op":"replace","path":"/spec/ports/0/nodePort","value":30443}]'

# To access the dashboard> https://192.168.1.1:30443 y añadimos el token que esté en token.txt teniendo elegida la primera opcion