from datetime import datetime

from sqlalchemy import create_engine, Integer, String, DateTime, select, and_, or_, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# 1. 创建SQLAlchemy引擎, 管理数据库连接、配置信息
engine = create_engine("mysql+pymysql://root:hxl12345@localhost:3306/db002",
                       echo=True)  # echo=True : 由连接产生的 SQL 语句, 会输出在日志中;


# 2. 声明模型父类, 定义与数据库表映射的模型类 (ORM --> 对象关系映射 : 类 ---> 表)
class Base(DeclarativeBase):
    pass


class AiMessage(Base):
    __tablename__ = "ai_message"  # 指定表名

    # 格式 --> 属性名: Mapped[对象属性类型] = mapped_column(类型(SQLALchemy中的类型), 是否为空, 是否主键, 字段注释)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键")
    session_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="会话ID")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色")
    content: Mapped[str] = mapped_column(String(500), nullable=False, comment="内容")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")

    def __repr__(self):
        return f"<AiMessage(id={self.id}, session_id={self.session_id}, role={self.role}, content={self.content}, create_time={self.create_time})>"


if __name__ == '__main__':
    # 3. 执行操作
    # 3.1 获取操作数据库的会话对象session
    with (Session(engine) as session):
        # 3.2 执行添加操作
        # session.add(AiMessage(session_id=1, role="user", content="就是好笑呀", create_time=datetime.now()))
        # session.add(AiMessage(session_id=1, role="assistant", content="你笑什么呢~", create_time=datetime.now()))
        # session.commit()

        # 3.3 执行查询操作
        # result_list = session.execute(select(AiMessage)).all()
        # for r in result_list:  # r: Row
        #     print(r[0])
        #
        # print('<=>')
        # # scalars()返回r的第一个元素
        # result_list = session.execute(select(AiMessage)).scalars().all()
        # for r in result_list:  # r: Row
        #     print(r)

        # 查询指定字段
        # result_list = session.execute(select(AiMessage.role, AiMessage.content)).all()
        # for r in result_list:  # r: Row
        #     print(r)
        #
        # # mappings()查询到的第一行r，转换为字典形式
        # result_list = session.execute(select(AiMessage.role, AiMessage.content)).mappings().all()
        # for r in result_list:  # r: Row
        #     print(r)

        # 3.4 条件查询
        # 查询id为1的消息数据
        # result = session.execute(select(AiMessage).where(AiMessage.id == 1)).scalars().one()
        # print(result)

        # 查询内容包 “你好” 的消息
        # result_list = session.execute(select(AiMessage).where(AiMessage.content.like("%你好%"))).scalars().all()
        # for r in result_list:
        #     print(r)

        # 查询 role 为 'user' 并且 content 包含 '您好' 的消息
        # 方式1
        # result_list = session.execute(
        #     select(AiMessage).where(AiMessage.role == "user", AiMessage.content.like("%你好%"))).scalars().all()
        # for r in result_list:
        #     print(r)
        #
        # 方式2
        # result_list = session.execute(
        #     select(AiMessage).where(and_(AiMessage.role == "user", AiMessage.content.like("%你好%")))).scalars().all()
        # for r in result_list:
        #     print(r)

        # 查询 role 为 'user' 或者 content 包含 '您好' 的消息
        # result_list = session.execute(select(AiMessage)
        #                               .where(or_(AiMessage.role == "user", AiMessage.content.like("%你好%")))
        #                               ).scalars().all()
        # for r in result_list:
        #     print(r)

        # 3.5 排序查询
        # result_list = session.execute(select(AiMessage)
        #                               .where(or_(AiMessage.id == 6, AiMessage.role == "user"))
        #                               .order_by(AiMessage.create_time.desc(), AiMessage.id.desc())
        #                               ).scalars().all()
        # for r in result_list:
        #     print(r)

        # 3.6 分页查询
        # result_list = session.execute(select(AiMessage)
        #                               .where(or_(AiMessage.id == 1, AiMessage.role == "user"))
        #                               .offset(0).limit(2)
        #                               ).scalars().all()
        # for r in result_list:
        #     print(r)

        # 3.7 更新操作
        # 更新id为1的消息，将内容更新为 "你好"
        # 方式1.1
        # session.execute(update(AiMessage).where(
        #     AiMessage.id == 1
        # ).values(content="你好", create_time=datetime.now()))
        # session.commit()

        # 方式1.2
        # session.execute(update(AiMessage).where(
        #     AiMessage.id == 1
        # ).values({"content": "hello", "create_time": datetime.now()}))
        # session.commit()

        # 方式2
        # ai_message = session.execute(select(AiMessage).where(AiMessage.id == 1)).scalars().one()
        # <=>
        # ai_message = session.get(AiMessage, 1)
        # ai_message.content = "知道了"
        # session.commit()

        # 删除操作
        # session.execute(delete(AiMessage).where(AiMessage.id == 1))
        # session.commit()

        session.execute(delete(AiMessage).where(AiMessage.id.in_([10, 12, 14, 16])))
        session.commit()
