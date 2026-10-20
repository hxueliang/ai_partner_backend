from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

engine: AsyncEngine = None
session_factory = None


async def init_db():
    global engine, session_factory
    # 1. 创建SQLAlchemy引擎, 管理数据库连接、配置信息
    engine = create_async_engine("mysql+aiomysql://root:hxl12345@localhost:3306/ai_partner_db",
                                 echo=True)  # echo=True : 由连接产生的 SQL 语句, 会输出在日志中;
    # 2.会话工厂(支持异步操作)
    session_factory = async_sessionmaker(engine)


async def close_db():
    if engine:
        await engine.dispose()


# 3. 声明模型父类, 定义与数据库表映射的模型类 (ORM --> 对象关系映射 : 类 ---> 表)
class Base(DeclarativeBase):
    pass


# 获取异步session
async def get_session():
    session = session_factory()
    try:
        yield session  # 使用yield代替return暂停函数并返回session，从而实现session的创建与销毁由同一个函数完成
    except Exception as e:
        print(f"get_session出错了：{e}")
        await session.rollback()
        raise
    finally:
        await session.close()
