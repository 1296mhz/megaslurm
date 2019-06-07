## Сначала создаем локальные постоянные тома

> заходим в каталог pv и правим во всех файлах
> pv1.yml, pv2.yml, pv3.yml, pv4.yml название узла в разделе nodeAffinity

> `m000` на свой номер студента.

```
cd pv
vi pv1.yml
vi pv2.yml
vi pv3.yml
vi pv4.yml
vi pv5.yml
vi pv6.yml
cd ..
```

## применяем
```
kubectl apply -f pv
```

## проверяем, должен быть список из 4 pv со статусом available

```
kubectl get pv
```

## тестируем подключение, для этого задеплоим тестовое приложение

```
kubectl apply -f test
```

## Проверяем, что pvc захватил себе pv
```
kubectl get pv
```

## Под не поднялся, смотрим его describe

```
kubectl get pod
kubectl describe pod local-pv-test-<pod-name>
```

## видим что надо создать пути на node-1 и node-2

```
ssh node-1.m000
mkdir -p /local/pv1
mkdir -p /local/pv2
mkdir -p /local/pv3

ssh node-2.m000
mkdir -p /local/pv4
mkdir -p /local/pv5
mkdir -p /local/pv6
```

## После этого под поднялся, можно в него зайти и создать что нибудь в каталоге /data, после этого проверить что это появилось в каталоге на узле.
## Похулиганим. Заскейлим под в 3

```
kubectl scale deployment.apps/local-pv-test --replicas 3
```

> Все поды поднялись на одном узле, смотрим в новый под, видим тот же каталог внутри пода.
> Смотрим на pvc

```
kubectl get pvc pvc1 -o yaml
```

#Вопрос - что не так с pvc и тремя подами ?

## Удаляем приложение, смотрим что с pv

```
kubectl delete -f test
kubectl get pv
```

> Статус pv - Released, использовать повторно нельзя. надо удалять руками или ставить local-provisioner, который умеет создавать pv, 
> для всех подключенных локальных дисков, и пересоздавать их, при удалении pvc


## Скачиваем values

```
helm inspect values stable/stolon > values.yaml
```
## Прописываем значения в файле values.yaml:
## (Пример можно посмотреть в файле v.yaml)


```
persistence:
  enabled: true
  storageClassName: "local-storage"
  accessModes:
    - ReadWriteOnce
  size: 1Gi

superuserUsername: "postgres"
superuserPassword: stolon

replicationUsername: "repluser"
replicationPassword: replpass

clusterSpec:
  usePgrewind: true
```

## Устанавливаем

```
helm install stable/stolon --name stolon --values values.yaml
```

## Смотрим за появлением пода

```
kubectl get pod -o wide -w
```

## Смотрим логи sentinel И keeper
## Подставляем свое имя пода!

```
kubectl logs stolon-sentinel-cf97cbd74-j5zt6
kubectl logs stolon-keeper-0
kubectl logs stolon-keeper-1
```

## Запускаем демо приложение

```
kubectl apply -f demo.yaml
```

## Дожидаемся пока запустится, узнаем имя подов и смотрим в его логи
## Подставляем свое имя пода!

```
kubectl get pod | grep psql-client-demo
kubectl logs -f psql-client-demo-556cc6fd56-ssdtw 
```

## Для удобства Открываем вторую консоль в sbox.slurm.io
## в первой путь будут логи, во второй будем пробовать пошатать постгресс

## Сначала сохраним sts
```
kubectl get statefulset stolon-keeper --export -o yaml > sts.yaml
```

## Теперь убьем его, оставив поды жить
```
kubectl delete statefulset stolon-keeper --cascade=false
```

## Ищем мастера и убиваем его
```
kubectl delete pod stolon-keeper-0
```

## В консоли приложения смотрим на ошибки, ждем восстановления

## Восстанавливаем sts
```
kubectl apply -f sts.yaml
```

## Смотрим как поднимается убитый под
```
kubectl get pod
```

## Смотрим в логи
```
kubectl logs stolon-keeper-0
```

> Ищем строчку pg_rewind
> 2019-03-16T18:14:49.289Z        INFO    postgresql/postgresql.go:783    running pg_rewind
> возможно и не будет записи.??? но база должна догнать основную

## Попробуем увеличить количество реплик

```
kubectl scale sts stolon-keeper --replicas 3
```

## Опять сохраним sts !!! У нас изменилось количество реплик
```
kubectl get statefulset stolon-keeper --export -o yaml > sts.yaml
```

## ждем, смотрим в логи
```
kubectl logs stolon-keeper-2
```

> Ищем строчку pg_basebackup
> 2019-03-16T18:54:53.015Z        INFO    postgresql/postgresql.go:824    running pg_basebackup

## Опять убиваем sts, оставив поды жить
```
kubectl delete statefulset stolon-keeper --cascade=false
```

## для проверки отказоустойчиовасти
## и убиваем под stolon-keeper-0
```
kubectl delete pod stolon-keeper-0
```

## Ждем пока появится коннект в приложении и убиваем второй
```
kubectl delete pod stolon-keeper-1
```

> Смотрим в логи приложения - убеждаемся что все продолжает работать.
> смотрим на какой pv забаундился pvc и удаляем pvc и pv

```
kubectl delete pvc data-stolon-keeper-1
kubectl delete pv node2-pv3
```

## Восстанавливаем sts
```
kubectl apply -f sts.yaml
```

> Смотрим за появлением подов в консоли и в браузере
```
kubectl get pod -o wide -w
```

> смотрим в логи
```
kubectl logs stolon-keeper-0
kubectl logs stolon-keeper-1
```

## Видим что stolon-keeper-0 сделал pg_rewind, stolon-keeper-1 ругнулся на несовпадение UID бд current db UID different than cluster data db UID
## и сделал basebackup
## полгода назад сентинель не поднимал том, а ждал ручного вмешательства. щас поднял.

## для управления кластером можно воспользоваться утилитой stolonctl
## Заходим в под с sentinel и запускаем утилиту управления кластером stolonctl
## Подставляем свое имя пода!

```
kubectl exec -it stolon-sentinel-58b899d64f-2nk4k bash

stolonctl status --cluster-name stolon --store-backend kubernetes --kube-resource-kind=configmap
```

## Если в логах мы видим ругань на несовпадение dataID, то придется зайти в управлятор кластера и удалить старый keeper1
## потому что stolon сам не смог сообразить, что член кластера поменялся
```
stolonctl removekeeper keeper1 --cluster-name stolon --store-backend kubernetes --kube-resource-kind=configmap
stolonctl status --cluster-name stolon --store-backend kubernetes --kube-resource-kind=configmap
```

## для продакщен stolon рекомендует использовать свой образ постгресса, с нужными дополнениями, добавив в него бинарники
## Dockerfile.template - пример сборки образа с кипером для запуска постгресса

## Удаляем все
```
kubectl delete -f demo.yaml

helm delete --purge stolon

kubectl delete pvc data-stolon-keeper-0
kubectl delete pvc data-stolon-keeper-1
kubectl delete pvc data-stolon-keeper-2
kubectl delete cm stolon-cluster-stolon
kubectl delete job stolon-create-cluster

```
