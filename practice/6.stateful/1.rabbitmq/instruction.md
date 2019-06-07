# Скачиваем values

```
helm inspect values stable/rabbitmq > values.yaml
```

## Прописываем значения в файле values.yaml:
## (Пример можно посмотреть в файле v1.yaml)
## Правим s000 на свой номер студента

```
rabbitmq:
  username: user
  password: rrabit
  erlangCookie: aUncToy7vvACuDQ6WRXyLEz5txvdUel9

  ## Clustering settings
  clustering:
   address_type: hostname
   k8s_domain: cluster.local

ingress:
  enabled: true
  hostName: rabbit.k8s.m000.slurm.io

persistence:
  enabled: false

#resources:
#  requests:
#    cpu: 10m

```

# Устанавливаем

```
helm install stable/rabbitmq --name rabbitmq --values values.yaml
```

## Смотрим за появлением пода

```
kubectl get pod -o wide -w
```

## Открываем в браузере
## Правим m000 на свой номер студента
## Вводим логин-пароль, видим консоль управления раббит

```
https://rabbit.k8s.m000.slurm.io
```

## Скейлим в 3

```
kubectl scale sts rabbitmq --replicas 3
```

## Смотрим за появлением подов в консоли и в браузере

```
kubectl get pod -o wide -w
```

## В браузере смотрим: Старый остался, добавились два новых

## Удаляем один под

```
kubectl delete pod rabbitmq-0
```

## Смотрим за удалением пода в консоли и в браузере

```
kubectl get pod -o wide -w
```
## Скейлим в 4

```
kubectl scale sts rabbitmq --replicas 4
```

## Смотрим за появлением подов в консоли и в браузере

```
kubectl get pod -o wide -w
```

## Запускаем апгрейд

## Имитируем обновление кластера с рестартом всего
## Правим values.yaml (Пример можно посмотреть в файле v2.yaml)

```
livenessProbe:
  initialDelaySeconds: 122
```

## Запускаем апгрейд

```
helm upgrade rabbitmq stable/rabbitmq --values values.yaml
```

## смотрим в консоли и в браузере как узлы по одному меняют свое состояние

```
kubectl get pod -o wide -w
```

## Удаляем rabbitmq

```
helm delete --purge rabbitmq
```
