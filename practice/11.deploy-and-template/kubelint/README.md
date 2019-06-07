# Kubelint

Скрипт для линта Helm чартов и манифестов Kubernetes.

## Getting Started

#### TL;DR

```bash
docker run --rm -v $PWD/<CHART_DIRECTORY>:/helm centosadmin/kubelint
```

### CI pipeline

Пример использования в Gitlab CI:

```yaml
stages:
  - test

kubelint:
  stage: test
  script:
    - docker run
      --rm
      -v $PWD/.helm:/helm
      centosadmin/kubelint
```

### Run options

```bash
Script for linting Helm charts and compiled kubernetes objects

Usage: ./lint.sh [options]
Options:
  --chart-dir: Directory where the chart for linting can be found (Default /helm)
  --k8s-api-url: Kubernetes API server url to check manifests against (Default omitted and no dry-run validation is run)
  --k8s-token: Kubernetes token to authenticate at Kubernetes API server (Default omitted and no dry-run validation is run)
  -h, --help: Show this help message
```

## How it works

Скрипт линта запускает несколько шагов:

1. helm lint - проверяется базовая корректность Helm чарта
2. helm template - собираются манифесты Kubernetes из темплэйтов, для последующей валидации
3. yamllint - проверяет манифесты на предмет корректности Yaml
4. python -m unittest - выполняет тесты на написанные питоне, проверяет манифесты на соответствие внутренним требованиям
5. [Optional] kubectl apply --dry-run - проверяет валидность манифестов в Kube API-server (тербуется доступ к API server)

### Yamllint

Файл с конфигурацией для Yamllint лежит в корне проекта (.yamllint).
В данной сборке слегка ослаблены [дефолтные правила](https://yamllint.readthedocs.io/en/stable/rules.html).
Для кастомизации можно внести изменения в .yamllint и пересобрать образ.

### Unittest

Файл с тестами лежит в директории tests/
В данный момент там описаны следующие тесты:

* test_labels - проверяет, что во всех манифестах есть необходимые лэйблы
  * app
  * component
  * release
* test_not_latest_tag - проверяет, что имадж не запускается с тэгом latest
* test_minimum_replicas - проверяет, что в деплойменте указано как минимум две реплики
* test_host - проверяет, что в ингрессе указано поле host

Любой тест можно пропуcтить, для этого нужно в манифесте указать аннотацию

```yaml
lint.southbridge.io/skip: test-name
```

test-name - это имя функции с тестом, который нужно пропускать для данного манифеста, без преффикса test_ и с замененными _ на -

## TODO:

- [ ] Дописать инструкции по запуску без докера
- [ ] Переписать скрипт на Python
- [ ] Реализовать вывод конкретных файлов в темплэйтах, где встречается ошибка

## Built With

* [Yamllint](https://github.com/adrienverge/yamllint) - Yaml линтер
* [Supermutes](https://pypi.org/project/supermutes/) -  Python библиотека для JS like доступа к словарям и спискам через точку
* [Helm](https://helm.sh/) - Пакетный менеджер для Kubernetes (используется helm template и helm lint)
* [Kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) - Консольная утилита для работы с Kubernetes (используется kubectl apply --dry-run)

## Authors

* Павел Селиванов - Southbridge

## License

This project is licensed under the MIT License
