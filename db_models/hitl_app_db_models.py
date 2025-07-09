from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DM_QAProduct_Product(Base):
    __tablename__ = 'DM_QAProduct_Product'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    Entity_ID = Column(Integer, nullable=True)
    Description = Column(String(2000), nullable=True)
    NumberofProductsonBase = Column(String(255), nullable=True)
    PrimaryCatalogNumber = Column(String(15), nullable=True)
    ProductBaseKey = Column(String(255), nullable=True)
    ProductKey = Column(Integer, nullable=True)
    ProductSpendCategory = Column(String(255), nullable=True)
    UNSPSCCommodity = Column(String(250), nullable=True)
    UNSPSCCommodityCode = Column(String(255), nullable=True)
    matchToExisting = Column(String(255), nullable=True)
    ProductTypeCode = Column(String(5), nullable=True)
    CatalogNumberStripped = Column(String(15), nullable=True)
    DescriptionException = Column(String(255), nullable=True)
    SyncCode = Column(String(255), nullable=True)
    SyncCodeSubCategory = Column(String(255), nullable=True)
    Json_Data = Column(Text, nullable=True)
    Modified_Json_Data = Column(Text, nullable=True)
    Status_ID = Column(Integer, nullable=True)
    Transaction_ID = Column(BigInteger, nullable=True)
    Parent_Transaction_ID = Column(BigInteger, nullable=True)
    Created_By = Column(String(255), nullable=True)
    Created_Date = Column(DateTime, nullable=True)
    Modified_By = Column(String(255), nullable=True)
    Modified_Date = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<DM_QAProduct_Product(ID={self.ID}, ProductKey={self.ProductKey}, Description={self.Description})>"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class TM_Exception_Log(Base):
    __tablename__ = 'TM_Exception_Log'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    Error_Type = Column(String(255), nullable=False)
    Message = Column(Text, nullable=False)
    Stack_Trace = Column(Text, nullable=True)
    Timestamp = Column(DateTime, nullable=False)
    Key = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<TM_Exception_Log(ID={self.ID}, Error_Type={self.Error_Type}, Timestamp={self.Timestamp})>"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
