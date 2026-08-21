# sre-bot

```
.
├── README.md
├── bot
│   ├── Dockerfile
│   ├── k8s
│   │   ├── deployment.yaml
│   │   ├── rbac.yaml
│   │   ├── sa.yaml
│   │   └── secret.yaml
│   ├── requirements.txt
│   └── sre_bot.py
├── infra
│   └── main.tf
└── k8s
    ├── deploy-notok.yaml
    ├── deploy-ok.yaml
    └── secret.yaml
```

## Fase 1: Backstage (Preparação)

### 1. Exportar Credenciais
- Gemini API: [Tutorial](https://ai.google.dev/gemini-api/docs/api-key?hl=pt-br)
- Slack Webhook: [Tutorial](https://www.svix.com/resources/guides/how-to-get-slack-webhook-url/)

```bash
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
export SLACK_WEBHOOK_URL="SUA_URL_WEBHOOK_AQUI"
```

### 2. Subir Infra (infra/)
```bash
cd infra && \
terraform init && \
terraform apply -auto-approve && \
cd ..
```

### 3. Build e Carga da Imagem (bot/)
```bash
cd bot
docker build -t tdc-sre-bot:latest .
kind load docker-image tdc-sre-bot:latest --name tdc-ia-demo
cd ..
```

## Fase 2: Setup do Bot

### Deploy dos Recursos bot
```bash
kubectl apply -f bot/k8s/sa.yaml
kubectl apply -f bot/k8s/rbac.yaml
envsubst < bot/k8s/secret.yaml | kubectl apply -f -
kubectl apply -f bot/k8s/deployment.yaml
```

### Deploy dos Recursos k8s
```bash
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deploy-ok.yaml
```

## Fase 3: O Show (Live Demo)

### Terminal 1 (Logs do pod BOT)
```bash
kubectl logs -f deployment/sre-bot
```

### Terminal 2 (Logs do pod API)
```bash
kubectl logs deployment/payment-api
```

### Injetar problemas
```bash
kubectl apply -f k8s/deploy-notok.yaml
```

## Fase 4: Teardown
```bash
terraform destroy -auto-approve
```
