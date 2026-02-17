# 部署指南

本文档介绍如何部署自动英语听写软件。

## 目录

- [系统要求](#系统要求)
- [本地部署](#本地部署)
- [Docker部署](#docker部署)
- [云服务部署](#云服务部署)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 系统要求

### 硬件要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 10GB | 20GB+ |
| 网络 | 需要联网 | 稳定网络 |

### 软件要求

- Python 3.8+
- pip 20.0+
- 操作系统: macOS / Linux / Windows

---

## 本地部署

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/dictation.git
cd dictation
```

### 2. 创建虚拟环境（推荐）

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n dictation python=3.10
conda activate dictation
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量（可选）

```bash
# MiniMax TTS API（可选，用于高质量语音）
export MINIMAX_API_KEY="your_api_key"
export MINIMAX_GROUP_ID="your_group_id"
```

### 5. 运行应用

```bash
streamlit run app.py
```

或使用启动脚本：

```bash
chmod +x start.sh
./start.sh
```

### 6. 访问应用

打开浏览器访问: http://localhost:8501

---

## Docker部署

### 1. 构建镜像

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建镜像：

```bash
docker build -t dictation:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name dictation \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -e MINIMAX_API_KEY="your_api_key" \
  dictation:latest
```

### 3. Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  dictation:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - MINIMAX_GROUP_ID=${MINIMAX_GROUP_ID}
    restart: unless-stopped
```

启动：

```bash
docker-compose up -d
```

---

## 云服务部署

### Streamlit Cloud

1. 将项目推送到 GitHub
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 连接 GitHub 仓库
4. 选择 `app.py` 作为入口文件
5. 配置环境变量（Secrets）
6. 部署

### Heroku

1. 创建 `Procfile`:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. 创建 `setup.sh`:

```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. 部署:

```bash
heroku create your-app-name
heroku config:set MINIMAX_API_KEY=your_key
git push heroku main
```

### AWS EC2

1. 启动 EC2 实例（推荐 t3.medium 或更高）
2. 安装 Python 和依赖
3. 配置安全组开放 8501 端口
4. 使用 systemd 管理服务

创建 `/etc/systemd/system/dictation.service`:

```ini
[Unit]
Description=Dictation App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/dictation
Environment="PATH=/home/ubuntu/dictation/venv/bin"
ExecStart=/home/ubuntu/dictation/venv/bin/streamlit run app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable dictation
sudo systemctl start dictation
```

---

## 配置说明

### Streamlit 配置

创建 `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| MINIMAX_API_KEY | MiniMax API密钥 | 否 |
| MINIMAX_GROUP_ID | MiniMax 组ID | 否 |
| LOG_LEVEL | 日志级别 (DEBUG/INFO/WARNING/ERROR) | 否 |

---

## 常见问题

### Q: OCR模型下载失败

A: 首次运行需要下载 PaddleOCR 模型，请确保网络畅通。可以手动下载模型放到 `~/.paddleocr/` 目录。

### Q: 语音播报失败

A:
1. 检查网络连接
2. 如果使用 MiniMax，检查 API Key 是否正确
3. 尝试使用 Edge TTS（默认备选）

### Q: 内存不足

A:
1. 增加服务器内存
2. 减少并发用户数
3. 定期清理音频缓存

### Q: 端口被占用

A: 修改启动命令中的端口号：

```bash
streamlit run app.py --server.port=8502
```

---

## 性能优化建议

1. **启用音频缓存**: 预加载常用单词音频
2. **使用 CDN**: 静态资源使用 CDN 加速
3. **数据库优化**: 大量数据时考虑使用 SQLite 或 PostgreSQL
4. **负载均衡**: 高并发时使用 Nginx 负载均衡

---

## 安全建议

1. 使用 HTTPS
2. 配置防火墙规则
3. 定期更新依赖
4. 不要在代码中硬编码 API Key
5. 启用 XSRF 保护

---

## 监控和日志

### 日志位置

- 应用日志: `logs/dictation.log`
- 错误日志: `logs/error.log`

### 日志级别

在 `src/logger.py` 中配置：

```python
from src.logger import set_log_level
import logging

set_log_level(logging.DEBUG)  # 调试模式
set_log_level(logging.INFO)   # 生产模式
```

---

## 备份和恢复

### 数据备份

```bash
# 备份词库数据
tar -czvf backup_$(date +%Y%m%d).tar.gz data/

# 备份日志
tar -czvf logs_$(date +%Y%m%d).tar.gz logs/
```

### 数据恢复

```bash
tar -xzvf backup_20260217.tar.gz
```

---

## 联系支持

如有问题，请提交 Issue 或联系开发团队。
