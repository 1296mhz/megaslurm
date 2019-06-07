### ПРАКТИКА

Давайте рассмотрим на примере как пользоваться Heptio Velero
Для работы нам потребуется утилита командой строки velero, kubctl и рабочий кластер кубернетес.


## Запускаем манифесты создания minio и velero:

```
cp velero /usr/bin/

kubectl apply -f examples/minio/00-minio-deployment.yaml

velero install \
    --provider aws \
    --bucket velero \
    --secret-file ./credentials-velero \
    --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.velero.svc:9000 \
    --snapshot-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.velero.svc:9000 \
    --use-restic --wait
```

#Давайте поиграем. 

## Создаем приложение пример:

```
kubectl apply -f examples/nginx-app/base.yaml
```

## Ждем пока все поднимется

```
kubectl get deployments -l component=velero --namespace=velero
kubectl get deployments --namespace=nginx-example
```

## Создадим бекап все объектов, у которых есть метка app=nginx

```
velero backup create nginx-backup --selector app=nginx
```

> Backup request "nginx-backup" submitted successfully.
> Run `velero backup describe nginx-backup` for more details.

## Посмотрим подробности
```
velero backup describe nginx-backup
```

## Удалим ns
```
kubectl delete ns nginx-example
```

## И восстановим в другой неймспейс:
```
velero restore create --from-backup nginx-backup --include-namespaces nginx-example --namespace-mappings nginx-example:nginx-restored
```

Добавим бекапы PV:

## Запустим редис и создадим в нем ключ

```
kubectl apply -f redis.yaml
kubectl -n red exec -it redis redis-cli
set mykey testik
get mykey
save

^D
```
> save - чтобы редис сохранил ключ в бекапный файл на диске, если не сделать, то каталог будет пустой и рестик не сможет сделать его снепшот

## Добавим аннотацию, что этот том надо бекапить:
```
kubectl -n red annotate pod/redis backup.velero.io/backup-volumes=redis-storage
```
## Создаем бекап
```
velero backup create redis1 --include-namespaces red
```

## Восстанавливаем в другой ns
```
velero restore create --from-backup redis1 --include-namespaces red --namespace-mappings red:red2
```

## Проверяем, что ключ восстановился:
```
kubectl -n red2 exec -it redis redis-cli
get mykey
```

## Удаляем
```
kubectl delete namespace/velero clusterrolebinding/velero
kubectl delete crds -l component=velero
kubectl delete ns nginx-restored red red2
```
