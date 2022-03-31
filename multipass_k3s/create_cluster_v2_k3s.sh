#echo "########## ADDING YOUR USER TO SUDOERS FILE ##########"
#echo "If you already have added your current user to sudoers file,"
#echo "you can skip this part and press any key to continue"
#echo
#echo "Otherwise, execute:"
#echo "  echo \"username  ALL=(ALL) NOPASSWD:ALL\" | sudo tee /etc/sudoers.d/username"
#echo "where 'username' is your current user"
#read -p "And press Ctrl+C to execute the script again"
#echo

#echo "########## INSTALLING MULTIPASS ##########"
#sudo snap install multipass
#echo

#echo "########## GENERATING KEYS ##########"
#echo "If you already have ~/.ssh/id_rsa and ~/.ssh/id_rsa.pub, you can skip this part"
#echo
#echo "Otherwise, execute 'ssh-keygen' to create a private/public key"
#echo
#read -p "Press any key to continue "
#echo
#pub_key=$(cat ~/.ssh/id_rsa.pub)
#echo "ssh_authorized_keys:" > multipass.yaml
#echo "  - "$pub_key >> multipass.yaml

#echo "########## CREATING SHARED FOLDER AMONG HOST AND NODES ##########"
#mkdir shared
#echo

echo "########## INSTALLING K3S MASTER ON HOST ##########"
host_ip=$(ifconfig mpqemubr0 | grep "inet " | awk -F: '{print $1}' | awk '{print $2}')
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -s - --node-ip $host_ip
echo

echo "########## CREATING NODES ##########"
read -p "Enter number of nodes: " number
for i in $(seq 1 $number)
do
  if [ $i -le 9 ]
  then
    node_name="node00"$i
    echo "########## CREATING "$node_name" ##########"
    multipass launch --name $node_name --cpus 2 --mem 5G --disk 6G --cloud-init multipass.yaml 
  else
    node_name="node0"$i
    echo "########## CREATING "$node_name" ##########"
    multipass launch --name $node_name --cpus 2 --mem 5G --disk 6G --cloud-init multipass.yaml 
  fi
  echo
  
  #echo "########## MOUNTING SHARED FOLDER ON "$node_name" MULTIPASS INSTANCE ##########"
  #multipass mount shared $node_name
  #echo
  
  echo "########## INSTALLING K3S AGENT ON "$node_name" ##########"
  node_ip="$(multipass list | tail -n -1 | awk '{ print $3 }')"
  k3s_token=$(sudo cat /var/lib/rancher/k3s/server/node-token)
  
  if [ $i -eq 1 ]
  then
    remote_cmd="'curl -sfL https://get.k3s.io | K3S_URL=https://"$host_ip":6443 K3S_TOKEN="$k3s_token" sh -s - --node-label node-type=factory-components'"
  else
    remote_cmd="'curl -sfL https://get.k3s.io | K3S_URL=https://"$host_ip":6443 K3S_TOKEN="$k3s_token" sh -s - --node-label node-type=multipass'"
  fi

  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip \'$remote_cmd\'
  echo
  
  free -m && sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && free -m
  echo
done
