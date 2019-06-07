## Все работы проводим с первого мастера под рутом

Запускаем оператор
```bash
kubectl apply -f team-operator/deploy/role.yaml -f team-operator/deploy/service_account.yaml -f team-operator/deploy/role_binding.yaml -f team-operator/deploy/crds/ops_v1beta1_team_crd.yaml -n kube-system
kubectl apply -f team-operator/deploy/operator.yaml -n kube-system
```

Проверяем, что под создался
```bash
kubectl get po -n kube-system
```

Создаем команду
```bash
kubectl apply -f team-operator/deploy/crds/ops_v1beta1_team_cr.yaml
```

Смотрим на нэймспэйсы

```bash
kubectl get ns
kubectl describe ns example-team-qa
kubectl describe ns example-team-stage
kubectl get po -n example-team-stage
kubectl get po -n example-team-qa
```
