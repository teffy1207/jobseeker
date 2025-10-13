from fastapi import FastAPI

# 2. 创建一个 FastAPI 的实例
#    这个实例将是你的API的主要交互点
app = FastAPI()

# 3. 定义一个路径操作 "装饰器"
#    @app.get("/") 告诉 FastAPI，下面这个函数负责处理对路径 "/" 的 GET 请求
@app.get("/")
async def read_root():
    # 4. 编写路径操作函数
    #    这个函数会返回一个字典，FastAPI会自动将其转换为JSON
    return {"message": "Hello, Job Seeker! Welcome to your AI Assistant."}

# 我们再添加一个简单的测试接口
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    # 这个接口演示了如何接收路径参数 (item_id) 和查询参数 (q)
    return {"item_id": item_id, "q": q}