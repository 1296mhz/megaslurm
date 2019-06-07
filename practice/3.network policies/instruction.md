# Подготавливаем к экспериментам

## Устанавливаем Calico network policy controller

```
kubectl apply -f calico-policy-only.yaml
```

## 1 Создаем поды и неймспейсы

```
./prepare.sh
```

## 2 Попингуем поды, покурлим 22 порт
## из access и test в ns prod и ns base пингуем base в base

## 3 Запрещаем все доступы к namespace base
```
kubectl apply -f 1.deny_all.yml
```
> внутри ns base пингуется, снаружи нет

## 4 Удаляем правило
```
kubectl delete networkpolicy default-deny --namespace base
```

## 5 Разрешаем доступ только с пода access
```
kubectl apply -f 2.allow_pod.yml
```
> внутри ns base из access пингуется, из test нет

## 6 Разрешаем доступ только к порту 22 с пода access - изменяем np access-bd
```
kubectl apply -f 3.allow_port_pod.yml
```
## пинга нет, только curl на 22 порт

## 7 Разрешаем доступ из ns prod только к порту 22 с пода access - добавляем np access-bd-prod
```
kubectl apply -f 4.allow_port_ns_pod.yml
```
## пинга нет, только curl на 22 порт

## 8.0 Ошибочная Network Policy, в ней не указан тип полиси, 
## а по умолчанию полиси действует на входящий и исходящий трафик
```
kubectl apply -f 5.egress_deny.yml.bad
```

## 8.1 Разрешаем доступ к подам кластера и наружу на два адреса
##  Исправляем ошибку. Разрешаем весь входящий трафик
```
kubectl apply -f 5.egress_deny.yml
```

## 9 Разрешаем доступ к подам кластера и наружу на два адреса только на порт 53/UDP
## А тут указываем, что полиси только для исходящего трафика
```
kubectl apply -f 6.egress_deny_53.yml
```
