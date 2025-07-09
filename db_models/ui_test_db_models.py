from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class TestCase(Base):
    __tablename__ = 'UI_Test_Cases'

    ID = Column(Integer, primary_key=True)
    Test_Case_Name = Column(String(255), unique=True, nullable=False)
    Description = Column(Text)
    Domain = Column(String(255))
    Entity = Column(String(255))
    Created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    Created_by = Column(String(255))

    # 🆕 ADO integration columns
    Ado_Plan_Id = Column(Integer)
    Ado_Suite_Id = Column(Integer)
    Ado_Case_Id = Column(Integer)

    # dev ops build Integration
    Build_Definition_Id = Column(String(255))

    executions = relationship("TestExecution", back_populates="test_case")

    def __repr__(self):
        return (f"<TestCase(ID={self.ID}, Test_Case_Name='{self.Test_Case_Name}', "
                f"ADO_PLAN_ID={self.Ado_Plan_Id}, ADO_CASE_ID={self.Ado_Case_Id})>")


class TestExecution(Base):
    __tablename__ = 'UI_Test_Executions'

    ID = Column(Integer, primary_key=True)
    Test_Case_Id = Column(Integer, ForeignKey('UI_Test_Cases.ID'), nullable=False)
    Outcome = Column(String(50))
    Environment = Column(String(100))
    Browser = Column(String(100))
    From_Pipeline = Column(String(100))
    Error_Message = Column(Text)
    Start_Time = Column(DateTime, default=datetime.utcnow, nullable=False)
    End_Time = Column(DateTime)

    test_case = relationship("TestCase", back_populates="executions")
    steps = relationship("TestStep", back_populates="test_execution")

    def __repr__(self):
        return f"<TestExecution(ID={self.ID}, Test_Case_Id={self.Test_Case_Id}, Outcome='{self.Outcome}')>"


class TestStep(Base):
    __tablename__ = 'UI_Test_Steps'

    ID = Column(Integer, primary_key=True)
    Execution_Id = Column(Integer, ForeignKey('UI_Test_Executions.ID'), nullable=False)
    Step_Desc = Column(String(255))
    Outcome = Column(String(50))
    Timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    Details = Column(Text)

    test_execution = relationship("TestExecution", back_populates="steps")

    def __repr__(self):
        return f"<TestStep(ID={self.ID}, Execution_Id={self.Execution_Id}, Step_Desc='{self.Step_Desc}')>"
