好的，为了将您的服务器状态报告以酷炫的黑白灰风格的图像呈现，我们将使用 `matplotlib` 和 `seaborn` 库。以下是修改后的代码：

```python
from astrbot.api.event.filter import command
from astrbot.api.star import Context, Star, register
import psutil
import platform
import datetime
import asyncio
import os
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

@register("服务器状态监控", "腾讯元宝&Meguminlove", "增强版状态监控插件", "1.1.2", "https://github.com/Meguminlove/astrbot_plugin_server_status")
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

    @command("状态查询", alias=["status"])
    async def server_status(self, event):
        try:
            # 获取系统信息
            cpu_usage = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            # 构建状态信息
            status_data = {
                "系统信息": f"{platform.system()} {platform.release()}",
                "运行时间": self._get_uptime(),
                "系统负载": self._get_load_avg(),
                "CPU使用率": f"{cpu_usage}%",
                "内存使用": f"{self._bytes_to_gb(mem.used)}G/{self._bytes_to_gb(mem.total)}G ({mem.percent}%)",
                "磁盘使用": f"{self._bytes_to_gb(disk.used)}G/{self._bytes_to_gb(disk.total)}G ({disk.percent}%)",
                "网络流量": f"↑{self._bytes_to_mb(net.bytes_sent)}MB ↓{self._bytes_to_mb(net.bytes_recv)}MB",
                "当前时间": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 绘制图表
            image_base64 = self._create_status_image(status_data)
            yield event.image_result(base64_image=image_base64)

        except Exception as e:
            yield event.plain_result(f"⚠️ 状态获取失败: {str(e)}")

    def _create_status_image(self, status_data: dict) -> str:
        """创建状态信息的图像"""
        sns.set_theme(style="darkgrid") # 设置主题为暗黑网格
        plt.figure(figsize=(8, 10)) # 设置图片大小

        # 绘制文本信息
        text_str = "️ 服务器状态报告\n------------------\n"
        for key, value in status_data.items():
            text_str += f"• {key}: {value}\n"
        plt.text(0.1, 0.95, text_str, fontsize=12, verticalalignment='top', family='monospace', color='white')

        plt.axis('off') # 隐藏坐标轴
        plt.gca().set_facecolor('black') # 设置背景颜色为黑色
        plt.gcf().set_facecolor('black') # 设置整个图片背景颜色为黑色

        # 保存图像到内存
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.5, facecolor='black')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        plt.clf() # 清理图片，防止内存泄漏。
        return image_base64

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
```

**主要修改：**

1.  **添加绘图函数 `_create_status_image`：**
    * 这个函数使用 `seaborn` 设置暗黑网格主题。
    * 使用 `matplotlib.pyplot.text` 在图像上绘制状态信息。
    * 设置图像的背景颜色为黑色。
    * 将图像保存到内存中的 `io.BytesIO` 缓冲区。
    * 将图像数据编码为 Base64 字符串，以便在消息中发送。
2.  **修改 `server_status` 函数：**
    * 调用 `_create_status_image` 函数生成图像。
    * 使用 `event.image_result` 发送图像消息。
3.  **导入必要的库：**
    * `matplotlib.pyplot` 用于绘图。
    * `seaborn` 用于设置主题。
    * `io` 用于内存中的字节流。
    * `base64` 用于编码图像数据。

**注意事项：**

* 确保您的环境中安装了 `matplotlib` 和 `seaborn` 库。可以使用 `pip install matplotlib seaborn` 进行安装。
* 图像的样式和布局可以根据需要进行调整。
* 使用 `event.image_result`发送图片，需要你的框架支持发送图片。

通过这些修改，您的插件将以酷炫的黑白灰风格图像显示服务器状态报告。
