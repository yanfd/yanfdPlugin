from astrbot.api.event.filter import command
from astrbot.api.star import Context, Star, register
import psutil
import platform
import datetime
import asyncio
import os
from typing import Optional
import matplotlib.pyplot as plt
import io
import base64
from jinja2 import Template

@register("状态监控", "腾讯元宝&Meguminlove", "增强版状态监控插件", "1.1.2", "https://github.com/Meguminlove/astrbot_plugin_server_status")
class ServerMonitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = getattr(context, 'config', {})
        self._monitor_task: Optional[asyncio.Task] = None

    def _get_uptime(self) -> str:
        """获取系统运行时间"""
        boot_time = psutil.boot_time()
        now = datetime.datetime.now().timestamp()
        uptime_seconds = int(now - boot_time)
        
        # 转换为可读格式
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_units = []
        if days > 0:
            time_units.append(f"{days}天")
        if hours > 0:
            time_units.append(f"{hours}小时")
        if minutes > 0:
            time_units.append(f"{minutes}分")
        time_units.append(f"{seconds}秒")
        
        return " ".join(time_units)

    def _get_load_avg(self) -> str:
        """获取系统负载信息"""
        try:
            load = os.getloadavg()
            return f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except AttributeError:
            return "不可用（Windows系统）"

    @command("状态查询2", alias=["status2"])
    async def server_status(self, event):
        try:
            # 获取系统信息
            cpu_usage = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            # 构建状态数据
            labels = ['CPU', '内存', '磁盘']
            sizes = [cpu_usage, mem.percent, disk.percent]
            colors = ['lightgray', 'gray', 'darkgray']

            # 生成饼状图
            buffer = io.BytesIO()
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.clf()

            # Jinja2 模板
            TMPL = """
            <div style="text-align: center;">
                <h1>服务器状态报告</h1>
                <img src="data:image/png;base64,{{ image_base64 }}" alt="服务器状态饼状图">
                <p>运行时间: {{ uptime }}</p>
                <p>系统负载: {{ load_avg }}</p>
                <p>网络流量: ↑{{ net_sent }}MB ↓{{ net_recv }}MB</p>
                <p>当前时间: {{ current_time }}</p>
            </div>
            """

            # 渲染 HTML
            template = Template(TMPL)
            html = template.render(
                image_base64=image_base64,
                uptime=self._get_uptime(),
                load_avg=self._get_load_avg(),
                net_sent=self._bytes_to_mb(net.bytes_sent),
                net_recv=self._bytes_to_mb(net.bytes_recv),
                current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # 生成图片
            url = await self.html_render(html)
            yield event.image_result(url)

        except Exception as e:
            yield event.plain_result(f"⚠️ 状态获取失败: {str(e)}")

    @staticmethod
    def _bytes_to_gb(bytes_num: int) -> float:
        return round(bytes_num / 1024**3, 1)
    
    @staticmethod
    def _bytes_to_mb(bytes_num: int) -> float:
        return round(bytes_num / 1024**2, 1)

    async def terminate(self):
        if self._monitor_task and not self._monitor_task.cancelled():
            self._monitor_task.cancel()
        await super().terminate()