#! /bin/bash

IMAGE_NAME="minikube_thesis"
NODES=2

# ssh keys setup
rm $(pwd)/docker/.ssh/id_rsa*
ssh-keygen -f $(pwd)/docker/.ssh/id_rsa -N ""

# base image with package dependencies installed
docker build -t $IMAGE_NAME docker

# recreate cluster
minikube delete -p thesis && \
minikube start -p thesis \
	--base-image $IMAGE_NAME \
	--nodes $NODES

# Build ansible inventory
echo "[nodes]" > ansible/inventory
for node in $(kubectl get nodes | grep -v NAME | awk '{print $1}');
do
	node_ip=$(minikube ip -p thesis $node)
	echo "$node ansible_host=$node_ip" >> ansible/inventory
done

# Run playbooks
pushd ansible
ansible-playbook playbooks/test.yaml
popd
