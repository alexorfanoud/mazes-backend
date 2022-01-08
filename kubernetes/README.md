## Dependencies

1. Install Docker: https://docs.docker.com/engine/install/ubuntu/
2. Install minikube: https://minikube.sigs.k8s.io/docs/start/
3. Install kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
4. Install golang: https://go.dev/doc/install
5. Start minikube with the appropriate configuration
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
* Replace the <newimage> placeholder in mazes-kubernetes/kustomization.yaml
```
kubectl apply -k .
```
