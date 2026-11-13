"""
待办事项接口的测试

规则：文件名 test_ 开头，函数名 test_ 开头，pytest 会自动收集。
client 这个参数不是自己传的，是 conftest.py 里的 fixture 自动注入的。
"""


async def test_create_item(client):
    """新增一条待办：验证返回 200、字段回显正确、默认值和自增 id 都生效。"""

    # 1. 发请求（只用必填字段，故意不传 id / create_time / status）
    resp = await client.post("/items/", json={
        "creator": "大肥鱼",
        "subject": "写测试",
    })

    # 2. 先看状态码，挂了的话后面断言没意义
    assert resp.status_code == 200, resp.text

    # 3. 把 JSON 转成字典，逐项检查
    data = resp.json()

    # 回显正确
    assert data["creator"] == "大肥鱼"
    assert data["subject"] == "写测试"

    # 数据库自增生效：id 有值且大于 0
    assert isinstance(data["id"], int)
    assert data["id"] > 0

    # 模型默认值生效（schema 里定义的默认值）
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert data["tags"] == ""

    # 时间字段是 ORM 自动填充的，不为空
    assert data["create_time"] is not None
    assert data["update_time"] is not None


async def test_list_items(client):
    """新增两条待办，然后查询新增的数据集合，验证返回 200、字段回显正确"""
    # 新增两条数据
    resp1 = await client.post("/items/", json={
        "creator": "傻子龙",
        "subject": "数据1",
    })
    resp2 = await client.post("/items/", json={
        "creator": "克劳德",
        "subject": "数据2",
    })
    # 看状态码，挂了的话后面断言没意义
    assert resp1.status_code == 200, resp1.text
    assert resp2.status_code == 200, resp2.text

    # 1.查询新增的待办数据
    resp = await client.get("/items/")
    # 2. 先看状态码，挂了的话后面断言没意义
    assert resp.status_code == 200, resp.text
    # 3. 把 JSON 转成字典，逐项检查
    data = resp.json()
    # 查询返回的的数据是一个集合
    assert isinstance(data, list)
    # 集合长度是2
    assert len(data) == 2
    # 创建者回显正确
    creators = [item["creator"] for item in data]
    assert creators == ["傻子龙", "克劳德"]  # 顺序：按 id 升序


async def test_get_item_not_found(client):
    # 1.根据id查询待办数据
    resp = await client.get("/items/9999")
    # 2. 验证状态码 404
    assert resp.status_code == 404, resp.text
    # 3. 把 JSON 转成字典，逐项检查
    data = resp.json()
    # 4.detail 是 "Item项不存在"。
    assert data["detail"] == "Item项不存在"


async def test_update_item(client):
    # 1. 发请求（只用必填字段，故意不传 id / create_time / status）
    resp = await client.post("/items/", json={
        "creator": "大肥鱼",
        "subject": "写测试",
    })
    # 2. 先看状态码，挂了的话后面断言没意义
    assert resp.status_code == 200, resp.text
    # 3. 把 JSON 转成字典，逐项检查
    data = resp.json()
    # 4.获取新增数据的id
    id_ = data["id"]
    # 1. 发请求（根据id修改数据的status，其他不改）
    resp1 = await client.put(f"/items/{id_}", json={
        "status": "completed",
    })
    # 2. 先看状态码，挂了的话后面断言没意义
    assert resp1.status_code == 200, resp1.text
    # 3. 把 JSON 转成字典，逐项检查
    data = resp1.json()
    # 验证 status 变了、其它字段没被动
    assert data["creator"] == "大肥鱼"
    assert data["subject"] == "写测试"
    assert data["status"] == "completed"
    assert data["priority"] == "medium"
    assert data["tags"] == ""


async def test_delete_item(client):
    # 1. 发请求（只用必填字段，故意不传 id / create_time / status）
    resp = await client.post("/items/", json={
        "creator": "大肥鱼",
        "subject": "写测试",
    })
    # 2. 先看状态码，挂了的话后面断言没意义
    assert resp.status_code == 200, resp.text
    # 3. 把 JSON 转成字典，逐项检查
    data = resp.json()
    # 4.获取新增数据的id
    id_ = data["id"]
    # 1. 发请求（根据id修改数据的status，其他不改）
    resp1 = await client.delete(f"/items/{id_}")
    # 2. 先看状态码，挂了的话后面断言没意义
    assert resp1.status_code == 200, resp.text
    assert resp1.json()["item_id"] == id_
    resp2 = await client.get(f"/items/{id_}")
    assert resp2.status_code == 404, resp2.text


async def test_create_item_invalid(client):
    """参数校验：标题只有 1 个字（min_length=2），应该被 422 拦住，不入库"""
    resp = await client.post("/items/", json={
        "creator": "大肥鱼",
        "subject": "短",          # 少于 min_length=2
    })
    # 1. 状态码必须是 422（FastAPI 的参数校验失败码）
    assert resp.status_code == 422, resp.text

    # 2. 错误详情里应该指明是 subject 这个字段
    detail = resp.json()["detail"]
    assert detail[0]["loc"][-1] == "subject"

    # 3. 校验失败的请求不应该写进数据库
    list_resp = await client.get("/items/")
    assert list_resp.json() == []

