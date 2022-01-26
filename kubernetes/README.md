## Dependencies

1. Install Docker: https://docs.docker.com/engine/install/ubuntu/
2. Install minikube: https://minikube.sigs.k8s.io/docs/start/
3. Install kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
4. Install golang: https://go.dev/doc/install

## Cluster setup

### PRM 
If you wish to run PRM, or have ansible for more provisioning control over the cluster, please follow the instructions in the [Cluster README](./cluster/README.md)

### Basic minikube setup
If you only wish to run the cluster and deploy the manifests, you can do so with the below command:
```
minikube delete -p thesis && minikube start -p thesis \
--nodes 2 \
--memory=4000M
```

## To build
```
MAZES_IMAGE=<docker repo>/mazes-backend
MAZES_TAG=latest
sudo docker build -t $MAZES_IMAGE:$MAZES_TAG ../server/
docker push $MAZES_IMAGE:$MAZES_TAG
```

## To run
* Replace the `newName` and `newTag` field in [kustomization.yaml](kustomization.yaml) with the newly created image and tag
```
kubectl apply -k .
```
