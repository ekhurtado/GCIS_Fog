sudo k3s kubectl delete ns kubernetes-dashboard
sudo k3s kubectl delete clusterrolebinding kubernetes-dashboard
sudo k3s kubectl delete clusterrole kubernetes-dashboard

sudo k3s kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml
sudo k3s kubectl delete -f dashboard.admin-user.yml -f dashboard.admin-user-role.yml