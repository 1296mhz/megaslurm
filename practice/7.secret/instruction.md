# Далее перейдем к установке HashiCorp Vault с помошью оператора от BanzaiCloud

## Откроем все права PSP на ns default
```
kubectl apply -f psp.yaml
```

## Настроим правила RBAC
```
kubectl apply -f operator/deploy/operator-rbac.yaml
kubectl apply -f operator/deploy/rbac.yaml
```

## Установим оператор
```
kubectl apply -f operator/deploy/operator.yaml
```

## Создадим ресурс, который скажет оператору создать нам волт
## Сначала поменяем в файле operator/deploy/cr.yaml название хоста
## m000 на m_номер_студента:

```
  ingress:
    spec:
      rules:
        - host: vault.k8s.m000.slurm.io
```

## Так же убеждаемся что в PVC описан сторадж нейм local-storage

```
kind: PersistentVolumeClaim
metadata:
  name: vault-file
  spec:
    storageClassName: "local-storage"
```
 
```
kubectl apply -f operator/deploy/cr.yaml
```

## Посмотрели на волт

```
kubectl get pod
```

## Теперь устанавливаем mutating webhook with Helm

```
helm repo add banzaicloud-stable http://kubernetes-charts.banzaicloud.com/branch/master
helm upgrade --install wmwh banzaicloud-stable/vault-secrets-webhook --namespace wmwh
```


## добавляем секрет в ваулт
## Токен админа root оператор записал нам в секрет куба
## Обычный вариант входа в vault - задаем переменные окружения и входим
## export VAULT_TOKEN=$(kubectl get secrets vault-unseal-keys -o jsonpath={.data.vault-root} | base64 -d)
## export VAULT_SKIP_VERIFY=true
## export VAULT_ADDR=https://127.0.0.1:8200
## vault

## при создании волта мы попросили оператора создать на ingress и включить UI, так что можно зайти браузером по адресу
## http://vault.k8s.m000.slurm.io
## и посмотреть на интрфейс волта. для авторизации введем root token, получить его можно командой
```
kubectl get secrets vault-unseal-keys -o jsonpath={.data.vault-root} | base64 -d
```

> Смотрим, видим ключик с данными, он там появился, потому что в operator/deploy/cr.yaml мы попросили его создать

## войдем в vault конслью
## создаем под, в котором настроен vault

```
kubectl apply -f console.yaml
```

> Смотрим его имя
```
kubectl get pod
```

## Запускаем внутри пода шелл 
```
kubectl exec -it vault-console-6f8cd6476d-6tzrm sh
```

## выполняем внутри пода команды:
## статус волта
```
vault status
```

## добавление ключа
```
vault kv put secret/accounts/aws AWS_SECRET_ACCESS_KEY=myGreatKey
```

## выходим из пода
```
exit
```

## идем в браузер http://vault.k8s.m000.slurm.io посмотреть что ключ изменился
## кстати kv версии 2 поддерживает версионирование, так что можно посмотреть предыдущие значения секретов.

## Создадим тестовое приложение, которое должно получить секреты из волта
```
kubectl apply -f test-deployment.yaml
```

## Посмотрели имя пода
```
kubectl get pod | grep hello-secret
```

## Посмотрели в логи основного контейнера
```
kubectl logs hello-secrets-6d46fb96db-tvsvb
```

## Посмотрели в логи init-контейнера
```
kubectl logs hello-secrets-6d46fb96db-tvsvb -c init-ubuntu
```

## видим что нам показывает секрет

## смотрим в описание деплоймент, видим что в env: написана ссылка на ваулт, и что команда выводит значение перемнной окружения

```
cat test-deployment.yaml
```
## смотрим в describe пода - видим что там так же ссылка на ваулт, а не секретное значение
kubectl describe pod hello-secrets-6d46fb96db-tvsvb
```
  Environment:
    AWS_SECRET_ACCESS_KEY:  vault:secret/data/accounts/aws#AWS_SECRET_ACCESS_KEY
```

## Заходим в под и смотрим переменные окружения 

```
kubectl exec -it hello-secrets-6d46fb96db-tvsvb env | grep AWS
```

## видим также ссылку на vault: AWS_SECRET_ACCESS_KEY=vault:secret/data/accounts/aws#AWS_SECRET_ACCESS_KEY

## Удаляем все

```
kubectl delete deployment vault-console
kubectl delete deployment hello-secrets

# удаляем ваулт, с помощью удаления CRD
kubectl delete vault vault
# смотрим
kubectl get pod

# добиваем оператора
kubectl delete deployment vault-operator
helm delete --purge wmwh

kubectl delete ns wmwh

# удаляем диск с данными ваулта
kubectl delete pvc vault-file
```
