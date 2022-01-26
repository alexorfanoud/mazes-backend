## Dependencies

1. Install ansible

## Spin up cluster

```
# Will build the appropriate base docker image for minikube nodes
# And perform all the necessary setup for ansible and PRM to be able to run
./setup.sh
```

## TODOS
* add playbook to mount resctrl filesystem
