"""
Kubernetes 扩展
===============

学习目标：
    1. 理解 K8s 基础概念
    2. 部署 LLM 服务到 K8s
    3. 配置 GPU 调度和自动扩缩容

核心概念：
    - Deployment：无状态应用部署
    - Service：服务发现和负载均衡
    - HPA：水平自动扩缩容

环境要求：
    - kubectl
    - Kubernetes 集群 with GPU 支持
"""


# ==================== 第一部分：K8s 基础 ====================


def introduction():
    """K8s 基础"""
    print("=" * 60)
    print("第一部分：K8s 基础概念")
    print("=" * 60)

    print("""
    📌 K8s 核心资源：
    ┌────────────────────────────────────────────────────────┐
    │  Pod      → 最小部署单位，包含一个或多个容器          │
    │  Deployment → 管理 Pod 的副本和更新策略              │
    │  Service  → 服务发现和负载均衡                        │
    │  Ingress  → 外部访问入口                               │
    │  HPA      → 水平自动扩缩容                            │
    │  PVC      → 持久化存储                                 │
    └────────────────────────────────────────────────────────┘

    📌 LLM 服务架构：
    Ingress → Service → Deployment (Pod × N) → PVC (模型存储)
                              ↓
                         GPU Node Pool
    """)


# ==================== 第二部分：Deployment 配置 ====================


def deployment_config():
    """Deployment 配置"""
    print("\n" + "=" * 60)
    print("第二部分：Deployment 配置")
    print("=" * 60)

    yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-service
  template:
    metadata:
      labels:
        app: llm-service
    spec:
      containers:
      - name: vllm
        image: llm-service:v1.0
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
          requests:
            memory: "16Gi"

        # 探针配置
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60  # 模型加载需要时间
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30

      # GPU 节点调度
      nodeSelector:
        nvidia.com/gpu.product: "NVIDIA-A100"

      tolerations:
      - key: "nvidia.com/gpu"
        operator: "Exists"
        effect: "NoSchedule"
"""
    print(yaml)


# ==================== 第三部分：Service 和 Ingress ====================


def service_ingress():
    """Service 和 Ingress"""
    print("\n" + "=" * 60)
    print("第三部分：Service 和 Ingress")
    print("=" * 60)

    yaml = """
# Service
apiVersion: v1
kind: Service
metadata:
  name: llm-service
spec:
  selector:
    app: llm-service
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  rules:
  - host: llm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: llm-service
            port:
              number: 80
"""
    print(yaml)


# ==================== 第四部分：HPA 自动扩缩容 ====================


def hpa_config():
    """HPA 配置"""
    print("\n" + "=" * 60)
    print("第四部分：HPA 自动扩缩容")
    print("=" * 60)

    yaml = """
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: requests_queue_size
      target:
        type: AverageValue
        averageValue: "50"  # 队列积压超50触发扩容

# kubectl get hpa llm-hpa -w  # 监控扩缩容
"""
    print(yaml)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：编写 LLM 服务的 K8s 部署清单
    练习 2：配置 HPA 并测试自动扩缩容

    思考题：K8s 部署 LLM 服务有什么挑战？
    答案：1. GPU 调度复杂 2. 模型加载时间长 3. 资源成本高
    """)


def main():
    introduction()
    deployment_config()
    service_ingress()
    hpa_config()
    exercises()
    print("\n课程完成！下一步：09-monitoring-logging.py")


if __name__ == "__main__":
    main()
