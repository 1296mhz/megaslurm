## Все работы все еще проводим из админбокса по адресу sbox.slurm.io

Переходим в директорию с практикой.
```bash
cd ~/slurm/practice/11.deployment-strategies/a-b
```

Открываем файлы stable-ingress.yaml и canary-ingress.yaml
В них находим
```yaml
    - host: nginx.k8s.m<номер своего логина>.slurm.io
```
И меняем на номер своего логина

Создаем все объекты в директории
```bash
kubectl apply -f .
```
В ответ должны увидеть
```bash
configmap/configmap-canary created
deployment.extensions/myapp-canary created
service/myapp-canary created
ingress.extensions/myingress-canary created
configmap/configmap-stable created
deployment.extensions/myapp-stable created
ingress.extensions/myingress-stable created
service/myapp-stable created
```
Смотрим на поды
```bash
kubectl get pod --show-labels
```
Видим
```bash
NAME                            READY   STATUS    RESTARTS   AGE   LABELS
myapp-canary-899cfdd96-6dnk2    1/1     Running   0          31s   app=myapp,release=canary
myapp-canary-899cfdd96-fqpzn    1/1     Running   0          31s   app=myapp,release=canary
myapp-stable-78685d76b4-9p6pt   1/1     Running   0          31s   app=myapp,release=stable
myapp-stable-78685d76b4-wzc4x   1/1     Running   0          31s   app=myapp,release=stable
```
Пробуем проверить, что наше приложение доступно через ингресс
```bash
curl -i nginx.k8s.m<номер своего логина>.slurm.io
```
В ответ получаем
```bash
HTTP/1.1 200 OK
Server: nginx/1.13.12
Date: Sun, 27 Jan 2019 15:09:36 GMT
Content-Type: application/octet-stream
Content-Length: 27
Connection: keep-alive

I am stable!
```
Пробуем проверить canary релиз
```bash
curl -i nginx.k8s.m<номер своего логина>.slurm.io -H "Cookie: tester=always"
```
В ответ получаем
```bash
HTTP/1.1 200 OK
Server: nginx/1.13.12
Date: Sun, 27 Jan 2019 15:09:36 GMT
Content-Type: application/octet-stream
Content-Length: 27
Connection: keep-alive

I am canary!
```

Чистим за собой кластер
```bash
kubectl delete -f .
```
