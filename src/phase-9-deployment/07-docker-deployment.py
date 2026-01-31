"""
Docker 部署
===========

学习目标：
    1. 编写 LLM 服务的 Dockerfile
    2. 使用 Docker Compose 编排服务
    3. 掌握 GPU 容器配置

核心概念：
    - Dockerfile：容器镜像构建脚本
    - Docker Compose：多容器编排
    - NVIDIA Container Toolkit：GPU 支持

环境要求：
    - Docker with NVIDIA GPU support
    - nvidia-container-toolkit
"""


# ==================== 第一部分：Dockerfile 编写 ====================


def introduction():
    """Dockerfile 编写"""
    print("=" * 60)
    print("第一部分：Dockerfile 编写")
    print("=" * 60)

    dockerfile = """
# 多阶段构建
FROM nvidia/cuda:12.1-devel AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM nvidia/cuda:12.1-runtime
WORKDIR /app

# 非root用户（安全最佳实践）
RUN useradd -m -u 1000 appuser
USER appuser

# 复制依赖和代码
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
"""
    print(dockerfile)


# ==================== 第二部分：Docker Compose ====================


def docker_compose():
    """Docker Compose 编排"""
    print("\n" + "=" * 60)
    print("第二部分：Docker Compose 编排")
    print("=" * 60)

    compose = """
# docker-compose.yml
version: "3.8"
services:
  llm-api:
    build: .
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "8000:8000"
    volumes:
      - model-cache:/root/.cache/huggingface
    environment:
      - MODEL_NAME=Qwen/Qwen2-7B-Instruct
      - GPU_MEMORY_UTILIZATION=0.9
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  model-cache:
  redis-data:

# 启动
# docker-compose up -d
# docker-compose logs -f llm-api
"""
    print(compose)


# ==================== 第三部分：GPU 配置 ====================


def gpu_configuration():
    """GPU 容器配置"""
    print("\n" + "=" * 60)
    print("第三部分：GPU 容器配置")
    print("=" * 60)

    print("""
    # 安装 NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \\
        sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
    sudo systemctl restart docker

    # 验证 GPU 支持
    docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi

    # 运行 GPU 容器
    docker run --gpus all ...           # 使用所有 GPU
    docker run --gpus '"device=0"' ...  # 使用指定 GPU
    docker run --gpus 2 ...             # 使用 2 个 GPU
    """)


# ==================== 第四部分：生产部署清单 ====================


def production_checklist():
    """生产部署清单"""
    print("\n" + "=" * 60)
    print("第四部分：生产部署清单")
    print("=" * 60)

    print("""
    ✅ 安全配置
    - 使用非 root 用户运行
    - 限制容器资源（内存、CPU）
    - 不暴露不必要的端口

    ✅ 健康检查
    - 配置 HEALTHCHECK 指令
    - 设置合理的检查间隔

    ✅ 日志配置
    - 输出到 stdout/stderr
    - 配置日志驱动

    ✅ 持久化
    - 模型缓存挂载卷
    - 日志和数据持久化

    ✅ 网络配置
    - 使用自定义网络
    - 配置服务发现
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：编写 LLM 服务的 Dockerfile
    练习 2：使用 Docker Compose 部署完整服务栈

    思考题：为什么使用多阶段构建？
    答案：减小最终镜像大小，分离构建环境和运行环境
    """)


def main():
    introduction()
    docker_compose()
    gpu_configuration()
    production_checklist()
    exercises()
    print("\n课程完成！下一步：08-kubernetes-scaling.py")


if __name__ == "__main__":
    main()
