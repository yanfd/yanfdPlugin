from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
import requests
from astrbot.api.star import Context, Star, register
from PIL import Image
from io import BytesIO
import tweepy
from jinja2 import Template

@register("YANFD_Plugins", "YANFD", "测试集", "1.0", "repo url")
class YANFD_Plugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 获取消息的纯文本内容
        yield event.plain_result(f"Hello, {user_name}!") # 发送一条纯文本消息

    # 自定义的 Jinja2 模板，支持 CSS
    TMPL = '''
    <div style="font-size: 32px;"> 
    <h1 style="color: black">Todo List</h1>

    <ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
    </div>
        '''

    @filter.command("todo")
    async def custom_t2i_tmpl(self, event: AstrMessageEvent):
        url = await self.html_render(TMPL, {"items": ["吃饭", "睡觉", "玩原神"]}) # 第二个参数是 Jinja2 的渲染数据
        yield event.image_result(url)


    @filter.command_group("yanfd")
    def yanfd():
        pass

    @yanfd.group("clutter")
    def clutter():
        pass

    @clutter.command("github_status")
    async def github_status(self, event: AstrMessageEvent):
        try:
            git_TMPL = '''
<!DOCTYPE html>
<html>
<head>
<title>Markdown to HTML</title>
<style>
body {
    background-color: #0c1117;
    margin: 0;
}

.center {
    text-align: center;
}
.flex-center {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
}
.icon {
    width: 30px;
    margin: 5px;
}
.left-image, .right-image {
    width: 45%;
    max-width: 450px;
    margin: 10px 6%; /* Adjust margin for centering */
    padding-left: 30px;
    display: inline-block;
}
.banner {
    max-width: 90%;
    height: auto;
}
.clearfix::after {
    content: "";
    clear: both;
    display: table;
}
</style>
</head>
<body>

<div class="center">
    <a href="#"><img class="banner" align="center" src="https://raw.githubusercontent.com/yanfd/yanfd/main/banner.png" alt="Banner"></a>
</div>

<div class="center">
    <div class="flex-center">
        <p>Maintainer of <a href="https://gallery.yanfd.tech/">ALMOST HUMAN GALLERY</a><br/>
        BLOG: <a href="https://www.yanfd.tech/">JOYLAB</a></p>
    </div>
    <div class="flex-center">
        <img class="icon" alt="Apple" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/apple/apple-original.svg" />
        <img class="icon" alt="Ubuntu" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ubuntu/ubuntu-plain.svg" />
        <img class="icon" alt="Visual Studio" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/visualstudio/visualstudio-plain.svg" />
        <img class="icon" alt="MySQL" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" />
        <img class="icon" alt="Java" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg"/>
        <img class="icon" alt="Spring" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/spring/spring-original.svg" />
        <img class="icon" alt="Git" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" />
        <img class="icon" alt="Linux" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg" />
        <img class="icon" alt="HTML" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-plain.svg" />
        <img class="icon" alt="CSS" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-plain.svg" />
        <img class="icon" alt="JavaScript" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-plain.svg" />
        <img class="icon" alt="Python" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-plain.svg" />
        <img class="icon" alt="C++" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-line.svg" />
        <img class="icon" alt="GitHub" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" />
    </div>
</div>

<hr>

<div class="clearfix">
    <a href="#"><img class="left-image" alt="这是生成的图片，无互动" src="https://raw.githubusercontent.com/yanfd/yanfd/main/metrics.left.svg"></a>
    <a href="#"><img class="right-image" alt="这是生成的图片，无互动" src="https://raw.githubusercontent.com/yanfd/yanfd/main/metrics.right.svg"></a>
</div>

</body>
</html>
            '''
            # 生成图片F
            url = await self.html_render(git_TMPL, {})

            # 从 URL 加载图片
            response = requests.get(url)
            response.raise_for_status()
            pic = Image.open(BytesIO(response.content))
            pic.save("status.png")
            yield event.image_result("status.png")

        except Exception as e:
            yield event.plain_result(f"⚠️ 状态获取失败: {str(e)}")

    

#   # Twitter 解析    
    bearer_token = "AAAAAAAAAAAAAAAAAAAAALTnrQEAAAAASq2mZWi2Dfq%2Bkg9HpVAPhIWaslw%3DIGNGoRIQ88VaVdXQ2hgRpwvZvmsCCtbH8Vm7SannjHUcRUPMPV" # 对于 API v2，推荐使用 Bearer Token
    @yanfd.command("twitter")
    async def twitter_info(self, event: AstrMessageEvent, text: str):
        '''这是一个 推特解析 指令'''
        tweet_url = text
        parts = tweet_url.split('/')
        try:
            tweet_id = parts[5].split('?')[0]
        except IndexError:
            yield event.plain_result("无效的 Twitter URL。")
            return

        async def get_tweet_info(tweet_id, bearer_token):
            client = tweepy.Client(bearer_token)

            try:
                response = client.get_tweet(
                    tweet_id,
                    expansions=['author_id', 'attachments.media_keys'],
                    tweet_fields=['created_at', 'public_metrics'],
                    user_fields=['profile_image_url', 'username'],
                    media_fields=['url']
                )

                if response.data:
                    tweet = response.data
                    author = response.includes['users'][0]
                    media = response.includes.get('media', [])

                    tweet_text = tweet.text
                    username = author.username
                    avatar_url = author.profile_image_url
                    created_at = tweet.created_at.strftime("%Y-%m-%d %H:%M UTC")  # 格式化时间

                    like_count = tweet.public_metrics['like_count']
                    retweet_count = tweet.public_metrics['retweet_count']

                    image_urls = [m.url for m in media if m.type == 'photo']

                    markdown_template = """
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                          <img src="{{ avatar_url }}" alt="头像" width="30" style="margin-right: 10px;">
                          <b>{{ username }}</b>
                        </div>
                        <div style="margin-bottom: 10px;">
                          {{ tweet_text }} <a href="{{ tweet_url }}" target="_blank">🔗</a>
                        </div>
                        {% if image_urls %}
                        <div align="center" style="margin-bottom: 10px;">
                          {% for image_url in image_urls %}
                          <img src="{{ image_url }}" alt="推文图片" width="300" style="margin-bottom: 5px;">
                          {% endfor %}
                        </div>
                        {% endif %}
                        <hr style="margin: 5px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em; color: #888;">
                          <div>
                            📅 `{{ created_at }}`
                          </div>
                          <div>
                            👍 {{ like_count }} 🔁 {{ retweet_count }}
                          </div>
                        </div>
                        <div style="font-size: 0.7em; color: #aaa; text-align: right;">
                          ID: `{{ tweet_id }}`
                        </div>
                        """
                    template = Template(markdown_template)
                    html = template.render(
                        avatar_url=avatar_url,
                        username=username,
                        tweet_text=tweet_text,
                        tweet_url=tweet_url,
                        image_urls=image_urls,
                        created_at=created_at,
                        like_count=like_count,
                        retweet_count=retweet_count,
                        tweet_id=tweet_id
                    )
                    url = await self.html_render(html, {})

                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        pic = Image.open(BytesIO(response.content))
                        pic.save("status.png")
                        yield event.image_result("status.png")
                    except requests.exceptions.RequestException as e:
                        yield event.plain_result(f"下载渲染图片失败: {e}")
                    except Exception as e:
                        yield event.plain_result(f"保存图片失败: {e}")

                else:
                    yield event.plain_result(f"无法找到 ID 为 {tweet_id} 的推文。")

            except tweepy.errors.NotFound:
                yield event.plain_result(f"推文 ID {tweet_id} 不存在。")
            except tweepy.errors.TweepyException as e:
                yield event.plain_result(f"获取推文信息时发生错误: {e}")

        if self.bearer_token:
            async for result in get_tweet_info(tweet_id, self.bearer_token):
                yield result
        else:
            yield event.plain_result("Bearer Token 未配置，无法获取推文信息。")
