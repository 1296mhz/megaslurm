## Все работы все еще проводим из админбокса по адресу sbox.slurm.io

Переходим в директорию с практикой.
```bash
cd ~/slurm/practice/10.deployment-strategies/blue-green
```

Открываем файл ingress.yaml
В нем находим
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
configmap/configmap-blue created
deployment.extensions/myapp-blue created
configmap/configmap-green created
deployment.extensions/myapp-green created
ingress.extensions/my-ingress created
service/myapp created
```
Смотрим на поды
```bash
kubectl get pod --show-labels
```
Видим
```bash
NAME                           READY   STATUS    RESTARTS   AGE   LABELS
myapp-blue-78c998b576-6qwfc    1/1     Running   0          22m   app=myapp,deploy=blue
myapp-blue-78c998b576-xfpdn    1/1     Running   0          22m   app=myapp,deploy=blue
myapp-green-57766d7c86-dlv44   1/1     Running   0          22m   app=myapp,deploy=green
myapp-green-57766d7c86-zpdzb   1/1     Running   0          22m   app=myapp,deploy=green
```
Смотрим куда сейчас смотрит сервис
```bash
kubectl get service -o custom-columns='NAME:.metadata.name, SELECTOR:.spec.selector.deploy'
```
> Видим
```bash
NAME         SELECTOR
myapp        green
```
Пробуем проверить, что наше приложение доступно через ингресс
и оно "зеленой" версии
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

I am green!
```

Пробуем перенаправить трафик на "голубую" версию
```bash
kubectl patch service myapp -p '{"spec":{"selector":{"deploy":"blue"}}}'
```
Проверяем сервис
```bash
kubectl get service -o custom-columns='NAME:.metadata.name, SELECTOR:.spec.selector.deploy'
```
Видим
```bash
NAME         SELECTOR
myapp        blue
```
И через ингресс
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

I am blue!
```

Чистим за собой кластер
```bash
kubectl delete -f .
```
