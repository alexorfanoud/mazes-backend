FROM gcr.io/k8s-minikube/kicbase:v0.0.28

# Ansible user
RUN useradd -m ansible
RUN usermod -aG sudo ansible
RUN usermod -p '*' ansible

WORKDIR /home/ansible

# Other dependencies for prm
RUN sudo apt update && sudo apt install -y \
	python3-pip \
	gcc \
	git \
	wget \
	vim

# Go installation
RUN wget https://go.dev/dl/go1.17.6.linux-amd64.tar.gz \
	&& rm -rf /usr/local/go \
	&& tar -C /usr/local -xzf go1.17.6.linux-amd64.tar.gz \
	&& ln -s /usr/local/go/bin/* /usr/bin/ \
	&& rm go1.17.6.linux-amd64.tar.gz
	
# Python module dependencies for prm
RUN sudo pip3 install \
	numpy \
	pandas \
	scipy \
	scikit-learn \
	docker \
	prometheus-client

# ssh setup for ansible
ADD .ssh/id_rsa.pub .ssh/authorized_keys 
RUN chmod 600 .ssh/authorized_keys && chown -R ansible:ansible .ssh
