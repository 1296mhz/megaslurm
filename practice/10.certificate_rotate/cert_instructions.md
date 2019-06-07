## Все работы проводим из админбокса по адресу sbox.slurm.io

### Первый мастер

Из админбокса заходим по SSH на сервер kube (все работы выполняем под рутом!)
```bash
ssh kube.m<Ваш номер логина>
sudo -i
```

Клонируем репозиторий megи и переходим в директорию практики
```bash
git clone https://gitlab.slurm.io/mega/slurm.git
cd slurm/practice/10.certificate_rotate
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

### Создаем кластер
```bash
kubeadm init --config cluster.yaml --experimental-upload-certs --ignore-preflight-errors NumCPU
```

Копируем две строки из вывода предыдущей команды и сохраняем например в файл join.txt
Они нам понадобятся в следующих шагах
Строки вида
```bash
kubeadm join 172.22.<Ваш номер лонига>.110:6443 --token xxxxxxxxxxxxxxxxxxxxx \
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

### Нода

Подготавливаем все тоже самое что и для мастеров

Из админбокса заходим по SSH на первую ноду (все работы выполняем под рутом!)
```bash
ssh node.m<Ваш номер логина>
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
kubeadm join 172.22.<Ваш номер логина>.110:6443 --token xxxxxxxxxxxxxxxxxxxxx \
  --discovery-token-ca-cert-hash sha256:xxxxxxxxxxxxxxxx
```

На первом мастере ставим на ноды лэйблы с ролью
```bash
kubectl label node node.m<Ваш номер лонина>.slurm.io node-role.kubernetes.io/node=""
```

### Запускаем тестовый под

```bash
kubectl run red --image redis
```

### Исследуем сертификаты

на kube
cp shcert /usr/bin

# Заходим в /etc/kubernetes/pki и смотрим на сертификаты:

```
cd /etc/kubernetes/pki

# 10 лет
shcert ca.crt

# 1 год
shcert apiserver.crt
```

три корневых сертификата etcd, ca, и front-proxe-ca
В каталоге еtcd сертификаты для etcd

в каталоге /etc/kubernetes конфиги для доступа kubelet, controller-manager, scheduler
сертификат в base64

```
shcert kubelet.conf
shcert admin.conf
```

### Обновляем сертификаты

# выключаем ntp на мастере и на node

```
systemctl disable --now ntpd
```

На master и node
```
date -s 20200501
```

# на node

На рабочих узлах сертификаты обновляются автоматически
Проверяем как работаете ротация сертификатов на узле На node

```
systemctl restart kubelet
```
Смотрим в логи

```
grep rotat /var/log/kubernetes.log
```

# Возвращемся на узел kube, где запущен control plane

Обновление сертификатов в /etc/kubernetes/pki
```
kubeadm alpha certs renew all
```

смотрим, что они все продлились
```
shcert /etc/kubernetes/pki/apiserver.crt
```
теперь ребутаем контейнеры
сначала etcd, потом apiserver

```
docker ps | grep etcd
docker stop <id>
```

```
docker ps | grep api
docker stop <id>
```

Ждем пока кублет поднимет.

Исправляем скриптик update.user.cert
исправляем на последней строчке название узла с мастером: 
m000 на mномер_студента

Запускаем, скрипт создаст сертификаты и скопирует их в /etc/kubernetes
```
update.user.cert

cp /etc/kubernetes/admin.conf /root/.kube/config

```

смотрим на сертификаты

останавливаем контейнеры с controller-manager и scheduler

устанавливаем дату на июль на kube и node

```
date -s 20200701
```

Все должно работать
