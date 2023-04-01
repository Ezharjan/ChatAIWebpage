使用python flask openai实现，数据保存在mongo中 本项目toGPT3.5分支，已经切换到最新的gpt-3.5-turbo模型。

#### 部署：

##### docker部署
```
# clone项目
git clone https://gitee.com/MIEAPP/chatai-python.git
# 进入文件夹
cd chatai-python
# 修改Dockerfile文件
CMD ["python","/code/main.py","-u","root","-p","123456","--host","mongo地址","--port","27017","--databaseName","chatui"]
将mongo准备好，用户账号密码，mongo地址等
# 修改.env文件
OPENAI_API_KEY=sk-xxx
使用openai的api-key（需要有openai的账号）
# 使用 docker build 构建image
docker build -t me/ai-image:v1 .
# 使用 docker run 创建容器并运行
docker run -d --name ai -p 8383:8383 me/ai-image:v1
```


前端项目：[chatai-vue](https://gitee.com/MIEAPP/chatai-vue)