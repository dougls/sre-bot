import time, os, requests
from kubernetes import client, config, watch
import google.generativeai as genai

# Configuração da IA (Gemini)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def enviar_para_slack(texto_ia, pod_name):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL não definida. Ignorando envio.")
        return

    payload = {
        "text": f"🚨 *Incidente detetado no Pod: {pod_name}*",
        "attachments": [{"color": "#E01E5A", "text": texto_ia}]
    }
    try:
        requests.post(webhook_url, json=payload)
        print("✅ Notificação enviada para o Slack.")
    except Exception as e:
        print(f"❌ Erro ao enviar para o Slack: {e}")

def call_ai_llm(contexto):
    print("🧠 Consultando Gemini para análise de causa raiz...")
    prompt = f"Tu és um SRE Sénior. Analisa o erro de Kubernetes abaixo e fornece a Causa Raiz e o comando de correção:\n{contexto}"
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro na IA: {e}"

config.load_incluster_config()
v1 = client.CoreV1Api()

def monitor():
    print("🚀 Bot SRE Online. Monitorando eventos...")
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, namespace="default"):
        pod = event['object']
        status = pod.status.container_statuses[0] if pod.status.container_statuses else None
        
        if status and not status.ready and status.state.waiting:
            reason = status.state.waiting.reason
            if reason in ["CreateContainerConfigError", "CrashLoopBackOff", "ImagePullBackOff"]:
                pod_name = pod.metadata.name
                print(f"🔍 Falha detetada: {pod_name} ({reason})")
                
                # Coleta contexto
                evts = v1.list_namespaced_event(namespace="default", field_selector=f"involvedObject.name={pod_name}")
                ctx = "\n".join([f"{e.type}: {e.message}" for e in evts.items])
                
                # Processamento
                analise = call_ai_llm(ctx)
                print(f"\n--- ANÁLISE IA ---\n{analise}\n")
                
                # Notificação
                enviar_para_slack(analise, pod_name)

if __name__ == "__main__":
    monitor()