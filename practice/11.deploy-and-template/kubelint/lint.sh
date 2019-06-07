#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
EXIT_CODE=0


log() {
    case $1 in
        error)
            LOG_LEVEL="error" COLOR=$RED
            ;;
        notice)
            LOG_LEVEL="notice"
            COLOR=$GREEN
            ;;
    esac

    timestamp="$(date +"%Y/%m/%d %H:%M:%S")"
    echo -e "$timestamp [$LOG_LEVEL] $0: ${COLOR}$2${NC}"
}

usage() {
    echo "Script for linting Helm charts and compiled kubernetes objects"
    echo ""
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --chart-dir: Directory where the chart for linting can be found (Default /helm)"
    echo "  --k8s-api-url: Kubernetes API server url to check manifests against (Default omitted and no dry-run validation is run)"
    echo "  --k8s-token: Kubernetes token to authenticate at Kubernetes API server (Default omitted and no dry-run validation is run)"
    echo "  -h, --help: Show this help message"
}

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --k8s-api-url)
    K8S_API_URL="$2"
    shift
    shift
    ;;
    --k8s-token)
    K8S_TOKEN="$2"
    shift
    shift
    ;;
    --chart-dir)
    CHART_DIR="$2"
    shift
    shift
    ;;
    -h|--help)
    usage
    exit 0
    shift
    shift
    ;;
    *)
    usage
    exit 1
    shift
    ;;
esac
done

if [ -z "$CHART_DIR" ]; then
    CHART_DIR=/helm
fi

if [ ! -d "$CHART_DIR" ]; then
    log error "Directory $CHART_DIR not found"
    exit 1
fi

log notice "Start linting"
echo "----------------"


log notice "Executing helm lint on ${CHART_DIR}"

sed -i.bak 's/^name: .*/name: helm/g' "$CHART_DIR"/Chart.yaml

if helm lint "$CHART_DIR"; then
    log notice "helm lint succesfull"

else log error "helm lint found some issues"
     EXIT_CODE=1
fi

mv "$CHART_DIR"/Chart.yaml.bak "$CHART_DIR"/Chart.yaml

echo "----------------"


log notice "Compiling kubernetes resources"
helm template "$CHART_DIR" | tee /kubelint-compiled.yaml
echo "----------------"


log notice "Executing yamllint on compiled Kubernetes resources"

if yamllint /kubelint-compiled.yaml; then
    log notice "yamllint succesfull"

else log error "yamllint found some issues"
     EXIT_CODE=1
fi

echo "----------------"


log notice "Executing python tests on compiled Kubernetes resources"

if python -m unittest discover tests/ -vvv; then
    log notice "python test succesfull"

else 
    log error "python test found some issues"
    EXIT_CODE=1
fi

echo "----------------"


if [ -n "$K8S_API_URL" ] && [ -n "$K8S_TOKEN" ]; then
    log notice "Executing kubectl dry-run on compiled Kubernetes resources"
    kubectl config set-cluster k8s --insecure-skip-tls-verify=true --server="$K8S_API_URL" > /dev/null
    kubectl config set-credentials ci --token="$K8S_TOKEN" > /dev/null
    kubectl config set-context ci --cluster=k8s --user=ci > /dev/null
    kubectl config use-context ci > /dev/null
    if kubectl apply -f /kubelint-compiled.yaml --dry-run; then
      log notice "kubectl dry-run succesfull"
    else 
        log error "kubectl dry-run found some issues"
        EXIT_CODE=1
    fi
    echo "----------------"
fi


if [ "$EXIT_CODE" -ne 0 ]; then
    log error "[LINT FAILED]"
    exit 1
else
    log notice "[LINT OK]"
    exit 0
fi
