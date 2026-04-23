terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.4.0"
    }
  }
}

provider "kind" {}

resource "kind_cluster" "tdc_demo" {
  name           = "tdc-ia-demo"
  node_image     = "kindest/node:v1.30.0"
  wait_for_ready = true
}

output "kubeconfig" {
  value       = kind_cluster.tdc_demo.kubeconfig
  description = "Comando para exportar o KUBECONFIG: export KUBECONFIG=~/.kube/config"
}