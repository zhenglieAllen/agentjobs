# AgentJobs 着陆页 —— 生产镜像
#
# 构建上下文是**仓库根**（不是 landing/），因此下面的 COPY 路径带了 landing/ 前缀：
#     docker build -f landing/Dockerfile -t agentjobs-landing .
#
# 技术选型依据见 .spec-workflow/specs/agentjobs/tech-decision.md 第 8 节：
# 验证期着陆页保持 Python 标准库实现，不重写为 FastAPI。

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    DB_PATH=/data/landing.db

WORKDIR /app

# 只取落地页所需的文件。构建上下文虽为仓库根，但 COPY 范围收窄到 landing/。
COPY landing/ /app/

# 以非 root 运行。/data 是 SQLite 的持久卷挂载点，必须对该用户可写。
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /data \
    && chown -R app:app /app /data

USER app

# SQLite 数据文件所在卷。平台须把持久卷挂到这里——
# 若挂载的是临时文件系统，重启会丢失全部订阅，M1 指标随之失效。
VOLUME ["/data"]

EXPOSE 8000

# PORT 由平台注入（Railway / Render），server.py 已读取该环境变量。
CMD ["python", "server.py"]
