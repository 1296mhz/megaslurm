## Все работы проводим из админбокса по адресу sbox.slurm.io

Добавляем свой публичный SSH ключ в Gitlab.
Для этого заходим в gitlab.slurm.io
В правом верхнем углу нажимаем на значок своей учетной записи.
В выпадающем меню нажимаем Settings.
Дальше в левом меню выбираем раздел SSH Keys
И в поле key вставляем свой ПУБЛИЧНЫЙ SSH ключ.

### Первый мастер

Из админбокса заходим по SSH на первый мастер (все работы выполняем под рутом!)
```bash
ssh master-1.m<Ваш номер логина>
sudo -i
```

Клонируем репозиторий megи и переходим в директорию практики
```bash
git clone gitlab.slurm.io/mega/slurm.git
cd slurm/practice/1.kubeadm
```

Ставим, настраиваем и запускаем Docker
```bash
yum-config-manager \
  --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo

yum install -y docker-ce-18.09.5

mkdir /etc/docker

cat > /etc/docker/daemon.json <<EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "iptables": false
}
EOF

systemctl enable --now docker
```

Настраиваем sysctl
```bash
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF

sysctl --system
```

Ставим kubelet,kubectl и kubeadm
```bash
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kube*
EOF

yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

systemctl enable --now kubelet
```

Правим файл с конфигурацией для kubeadm cluster.yaml
Меняем плэйсхолдер <Ваш номер логина>
> Если Ваш номер логина 001, то IP адрес - 172.22.1.5, а не 172.22.001.5 !!!
```yaml
controlPlaneEndpoint: 172.22.<Ваш номер логина>.5:6443
```

Создаем кластер
```bash
kubeadm init --config cluster.yaml --experimental-upload-certs --ignore-preflight-errors NumCPU
```

Копируем две строки из вывода предыдущей команды и сохраняем например в файл join.txt
Они нам понадобятся в следующих шагах
Строки вида
```bash
kubeadm join 172.22.<Ваш номер логина>.5:6443 --token xxxxxxxxxxxxx \
  --discovery-token-ca-cert-hash sha256:xxxxxxxxxxxxxxxxxxx \
  --experimental-control-plane --certificate-key xxxxxxxxxxxxxxxxxxxxxxxx 
kubeadm join 172.22.<Ваш номер логина>.5:6443 --token xxxxxxxxxxxxxxxxxxxxx \
  --discovery-token-ca-cert-hash sha256:xxxxxxxxxxxxxxxx
```

Копируем kubeconfg
```bash
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
```

Ставим сетевой плагин
```bash
kubectl apply -f kube-flannel.yaml
```

Проверяем, что все заработало
```bash
kubectl get node
kubectl get po -A
```

### Второй и третий мастера

Из админбокса заходим по SSH на второй мастер (все работы выполняем под рутом!)
```bash
ssh master-2.m<Ваш номер логина>
sudo -i
```

Ставим, настраиваем и запускаем Docker
```bash
yum-config-manager \
  --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo

yum install -y docker-ce-18.09.5

mkdir /etc/docker

cat > /etc/docker/daemon.json <<EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "iptables": false
}
EOF

systemctl enable --now docker
```

Настраиваем sysctl
```bash
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF

sysctl --system
```

Ставим kubelet,kubectl и kubeadm
```bash
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kube*
EOF

yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

systemctl enable --now kubelet
```

Выполняем команду из сохраненного вывода kubeadm init.
Дополнительно к ней нужно добавить ключ --ignore-preflight-errors=NumCPU
> Нужна команда, в которой есть ключ --experimental-control-plane
```bash
kubeadm join 172.22.<Ваш номер логина>.5:6443 --token xxxxxxxxxxxxx \
  --discovery-token-ca-cert-hash sha256:xxxxxxxxxxxxxxxxxxx \
  --experimental-control-plane --certificate-key xxxxxxxxxxxxxxxxxxxxxxxx --ignore-preflight-errors=NumCPU
```

Повторяем все тоже самое на третьем мастере


### Ноды

Подготавливаем все тоже самое что и для мастеров

Из админбокса заходим по SSH на первую ноду (все работы выполняем под рутом!)
```bash
ssh node-1.m<Ваш номер логина>
sudo -i
```

Ставим, настраиваем и запускаем Docker
```bash
yum-config-manager \
  --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo

yum install -y docker-ce-18.09.5

mkdir /etc/docker

cat > /etc/docker/daemon.json <<EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "iptables": false
}
EOF

systemctl enable --now docker
```

Настраиваем sysctl
```bash
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF

sysctl --system
```

Ставим kubelet,kubectl и kubeadm
```bash
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kube*
EOF

yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

systemctl enable --now kubelet
```

Выполняем команду из сохраненного вывода kubeadm init.
> Нужна команда, в которой нет ключа --experimental-control-plane
```bash
kubeadm join 172.22.<Ваш номер логина>.5:6443 --token xxxxxxxxxxxxxxxxxxxxx \
  --discovery-token-ca-cert-hash sha256:xxxxxxxxxxxxxxxx
```

Повторяем все тоже самое на второй ноде

На первом мастере ставим на ноды лэйблы с ролью
```bash
kubectl label node node-1.m<Ваш номер логина>.slurm.io node-role.kubernetes.io/node=""
kubectl label node node-2.m<Ваш номер логина>.slurm.io node-role.kubernetes.io/node=""
```

### Установка и настройка плагинов

Ставим Helm
```bash
yum install -y helm
kubectl create sa tiller -n kube-system
kubectl create clusterrolebinding tiller --serviceaccount=kube-system:tiller --clusterrole=cluster-admin
helm init --service-account tiller --history-max 10
```

Ставим ингресс
```bash
helm upgrade -i nginx-ingress nginx-ingress/ --namespace kube-system
```

Тюним Coredns
```bash
kubectl edit configmap -n kube-system coredns
```
В открывшемся файле меняем
```bash
pods insecure
```
на
```bash
pods verified
```
и дописываем
```bash
autopath @kubernetes
```
В итоге должно получиться
```bash
Corefile: |
  .:53 {
      errors
      health
      autopath @kubernetes
      kubernetes cluster.local in-addr.arpa ip6.arpa {
         pods verified
         upstream
         fallthrough in-addr.arpa ip6.arpa
      }
      prometheus :9153
      forward . /etc/resolv.conf
      cache 30
      loop
      reload
      loadbalance
  }
```
Сохраняем и закрываем файл

