cleanup-pods:
	microk8s kubectl scale deployment deepseek-newsletter --replicas=0 2>&1
	microk8s kubectl delete pods -l app=deepseek-newsletter --ignore-not-found 2>&1
	microk8s kubectl delete deployment deepseek-newsletter --ignore-not-found 2>&1

build:
	docker build --target prod -t deepseek-newsletter:latest . 2>&1
	docker tag deepseek-newsletter:latest localhost:32000/deepseek-newsletter:latest 2>&1
	docker push localhost:32000/deepseek-newsletter:latest 2>&1

purge:
	sudo rm -rf /var/snap/microk8s/common/registry 2>&1
	echo "MicroK8s registry data has been purged." 2>&1

uninstall:
	sudo microk8s stop || true 2>&1
	sudo snap remove microk8s 2>&1
	sudo rm -rf /var/snap/microk8s 2>&1
	sudo rm -rf /var/snap/microk8s/common/registry 2>&1
	sudo rm -rf ~/.kube 2>&1
	echo "MicroK8s and all registry/configuration data have been removed." 2>&1

apply-manifests:
	sudo microk8s kubectl apply -f k8s/deployment.yaml 2>&1
	sudo microk8s kubectl apply -f k8s/service.yaml 2>&1
	sudo microk8s kubectl apply -f k8s/secrets.yaml 2>&1
	sudo microk8s kubectl rollout restart deployment deepseek-newsletter 2>&1

run:
	-make cleanup-pods
	make build
	make apply-manifests

install:
	if ! command -v docker >/dev/null 2>&1; then \
		echo "Docker not found. Installing Docker..."; \
		sudo apt-get update; \
		sudo apt-get install -y ca-certificates curl gnupg; \
		sudo install -m 0755 -d /etc/apt/keyrings; \
		curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; \
		echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; \
		sudo apt-get update; \
		sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; \
		sudo groupadd -f docker; \
		sudo usermod -aG docker $$USER; \
		echo "Docker installed. Please log out and log back in for group changes to take effect."; \
	else \
		echo "Docker is already installed."; \
	fi
	sudo snap install microk8s --classic
	sudo usermod -a -G microk8s $$USER
	sudo mkdir -p ~/.kube
	sudo chown -f -R $$USER ~/.kube
	sudo microk8s status --wait-ready
	sudo microk8s enable dns
	sudo microk8s enable ingress
	sudo microk8s enable metallb:10.64.140.43-10.64.140.49
	sudo microk8s enable hostpath-storage
	sudo microk8s kubectl get nodes
	sudo microk8s enable registry
	echo "MicroK8s installed and basic networking enabled. Please log out and log back in if you just added yourself to the microk8s or docker group."
	echo "alias kubectl='microk8s kubectl'" >> ~/.bashrc
	echo "kubectl is now aliased to microk8s kubectl. Run 'source ~/.bashrc' or open a new shell to use the alias."
