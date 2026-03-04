#!/usr/bin/env python3
"""
AlphaFabric - Web服务接口
用于KIMI CLAW健康检查和状态监控
"""
import os
import sys
import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import load_config

logger = logging.getLogger('AlphaFabric')

# 全局状态
system_status = {
    "status": "running",
    "version": "1.0.0",
    "start_time": datetime.now().isoformat(),
    "last_select": None,
    "stock_count": 0,
    "data_updated": False
}


class HealthHandler(BaseHTTPRequestHandler):
    """健康检查处理器"""
    
    def log_message(self, format, *args):
        """禁用默认日志"""
        pass
    
    def do_GET(self):
        """处理GET请求"""
        path = self.path
        
        if path == '/health':
            self._handle_health()
        elif path == '/status':
            self._handle_status()
        elif path == '/metrics':
            self._handle_metrics()
        else:
            self._handle_404()
    
    def _handle_health(self):
        """健康检查端点"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "alphafabric",
            "version": "1.0.0"
        }
        self._send_json(health, 200)
    
    def _handle_status(self):
        """状态查询端点"""
        self._send_json(system_status, 200)
    
    def _handle_metrics(self):
        """Prometheus格式指标"""
        metrics = f"""# AlphaFabric Metrics
alphafabric_status{{version="1.0.0"}} 1
alphafabric_stock_count {system_status.get('stock_count', 0)}
alphafabric_data_updated {1 if system_status.get('data_updated') else 0}
"""
        self._send_text(metrics, 200)
    
    def _handle_404(self):
        """404处理"""
        self._send_json({"error": "Not Found"}, 404)
    
    def _send_json(self, data, status_code):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def _send_text(self, text, status_code):
        """发送文本响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode())


def start_web_server(port=8000):
    """启动Web服务器"""
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Web服务器启动: http://0.0.0.0:{port}")
    
    # 在后台线程运行
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    return server


def update_status(**kwargs):
    """更新系统状态"""
    global system_status
    system_status.update(kwargs)
    system_status['timestamp'] = datetime.now().isoformat()


if __name__ == '__main__':
    # 测试运行
    start_web_server(8000)
    
    # 保持运行
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("服务器停止")
