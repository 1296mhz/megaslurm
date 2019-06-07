## Все работы все еще проводим с первого мастера

Переходим в директорию с практикой.
```bash
cd ~/slurm/practice/4.secure-and-highlyavailable-apps/pdb
```

Открываем nginx/ingress.yaml
и в нем правим 
```yaml
    - host: nginx.k8s.m<номер своего логина>.slurm.io
```

Запускаем тестовое приложение
```bash
kubectl apply -f nginx/
```

Имитируем деплой/проблему.
Оставляем у приложения только одну реплику
```bash
kubectl scale deployment nginx --replicas 1
```

Смотрим на поды
```bash
kubectl get pod -o wide
```

Видим
```bash
NAME                        READY   STATUS    RESTARTS   AGE   IP           NODE                                       NOMINATED NODE
nginx-cb89cfd86-4r8x5   1/1     Running   0          1m    10.4.1.206   gke-student-0-default-pool-09e231b7-n3pl   <none>
```
Запоминаем на какой ноде запущен под

В соседнем терминале запускаем команду для проверки доступности приложения
> Не забываем менять плэйсхолдеры
```bash
while true; do curl -s --connect-timeout 1 nginx.k8s.m<ваш номер логина>.slurm.io -i | grep '200 OK' 2>&1 > /dev/null; if [ $? -eq 0 ]; then echo OK; else echo FAIL; fi; sleep 1; done
```

Выводим ноду на обслуживание
```bash
kubectl drain gke-student-0-default-pool-089176ad-7f1c --grace-period 60 --delete-local-data --ignore-daemonsets --force
```
Видим что на какое то время наше приложение становится недоступным

Возвращаем ноду
```bash
kubectl uncordon gke-student-0-default-pool-089176ad-7f1c
```

Далее применяем pdb
```bash
kubectl apply -f pdb.yaml
```
И повторяем шаги с get pod

Смотрим на поды
```bash
kubectl get pod -o wide
```
Видим
```bash
NAME                        READY   STATUS    RESTARTS   AGE   IP           NODE                                       NOMINATED NODE
nginx-cb89cfd86-4r8x5   1/1     Running   0          1m    10.4.1.206   gke-student-0-default-pool-09e231b7-n3pl   <none>
```
Запоминаем на какой ноде запущен под

В соседнем терминале запускаем команду для проверки доступности приложения
```bash
while true; do curl -s --connect-timeout 1 student<ваш номер логина>.k8s.slurm.io -i | grep '200 OK' 2>&1 > /dev/null; if [ $? -eq 0 ]; then echo OK; else echo FAIL; fi; sleep 1; done
```

Выводим ноду на обслуживание
```bash
kubectl drain gke-student-0-default-pool-089176ad-7f1c --grace-period 60 --delete-local-data --ignore-daemonsets --force
```

Видим, что кубернетис просит нас подождать
```bash
error when evicting pod "nginx-56f65c4885-kd97j" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
```
А наше приложение все еще доступно

Имитируем возвращение потерянного второго инстанса
```bash
kubectl scale deployment nginx --replicas 2
```

После этого процесс дрэйна у нас завершается успешно,
а приложение работает без единой ошибки клиенту.

Возвращаем ноду
```bash
kubectl uncordon gke-student-0-default-pool-089176ad-7f1c
```

Чистим за собой кластер
```bash
kubectl delete -f nginx/
kubectl delete -f pdb.yaml
```
