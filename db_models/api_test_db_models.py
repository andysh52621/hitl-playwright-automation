from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Boolean
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.orm import relationship

from db_models.ui_test_db_models import Base


class APIServiceConfig(Base):
    __tablename__ = "API_Test_Service_Config"

    service_id = Column("Service_Id", Integer, primary_key=True, autoincrement=True)
    is_enabled = Column("Is_Enabled", Boolean)
    request_type = Column("Request_Type", String(100))
    service_env = Column("Service_Env", String(100))
    service_desc = Column("Service_Desc", String(250))
    service_protocol = Column("Service_Protocol", String(100))
    server_name = Column("Server_Name", String(250))
    port_number = Column("Port_Number", Integer)
    http_request_type = Column("Http_Request_Type", String(100))
    service_endpoint_path = Column("Service_EndPoint_Path", String(100))
    service_encoding_type = Column("Service_Encoding_Type", String(100))
    created_by = Column("Created_By", String(100))
    created_at = Column("CreateDateTime", DateTime)
    updated_at = Column("Last_Updated_DateTime", DateTime)

    # Extended Auth Columns
    apim_base_url_server = Column("apim_base_url_server", NVARCHAR(500))
    apim_base_url_endpoint = Column("apim_base_url_endpoint", NVARCHAR(500))
    access_token_server = Column("access_token_server", NVARCHAR(500))
    access_token_endpoint = Column("access_token_endpoint", NVARCHAR(500))
    client_id_service_account = Column("client_id_service_account", NVARCHAR(500))
    client_secret_service_account = Column("client_secret_service_account", NVARCHAR(500))
    primary_subscription_key = Column("primary_subscription_key", NVARCHAR(500))
    secondary_subscription_key = Column("secondary_subscription_key", NVARCHAR(500))
    automation_db_host = Column("automation_db_host", NVARCHAR(500))
    automation_db = Column("automation_db", NVARCHAR(500))
    automation_db_authentication = Column("automation_db_authentication", NVARCHAR(500))

    test_runs = relationship("APITestRun", back_populates="service")


class APITestCaseConfig(Base):
    __tablename__ = "API_Test_Case_Config"

    test_case_id = Column("Test_Case_id", Integer, primary_key=True, autoincrement=True)
    test_case_desc = Column("Test_Case_Desc", String(500))
    event_name_prefix = Column("Event_Name_Prefix", String(200))
    event_name_suffix = Column("Event_Name_Suffix", String(200))
    event_domain = Column("Event_Domain", String(200))
    event_type = Column("Event_Type", String(200))
    created_at = Column("CreateDateTime", DateTime)

    test_runs = relationship("APITestRun", back_populates="test_case")


class APITestRun(Base):
    __tablename__ = "API_Test_Run"

    run_id = Column("Run_Id", Integer, primary_key=True, autoincrement=True)
    service_id = Column("Service_Id", Integer, ForeignKey("API_Test_Service_Config.Service_Id"))
    test_case_id = Column("Test_Case_Id", Integer, ForeignKey("API_Test_Case_Config.Test_Case_id"))
    machine_ip = Column("Machine_IP", NVARCHAR(50))
    workers = Column("Workers", Integer)
    tasks_per_worker = Column("Tasks_Per_Worker", Integer)
    avg_response_time = Column("Avg_Response_Time", Integer)
    percentile_90 = Column("90th_Percentile", Integer)
    percentile_95 = Column("95th_Percentile", Integer)
    percentile_99 = Column("99th_Percentile", Integer)
    failure_percent = Column("Failure_Percent", Integer)
    test_tag = Column("Test_Tag", NVARCHAR(250))
    start_run_timestamp = Column("Start_Run_timeStamp", DateTime)
    end_run_timestamp = Column("End_Run_timeStamp", DateTime)

    service = relationship("APIServiceConfig", back_populates="test_runs")
    test_case = relationship("APITestCaseConfig", back_populates="test_runs")
    test_results = relationship("APITestResult", back_populates="test_run")


class APITestResult(Base):
    __tablename__ = "API_Test_Result"

    test_result_id = Column("Test_Result_id", Integer, primary_key=True, autoincrement=True)
    test_run_id = Column("Test_Run_id", Integer, ForeignKey("API_Test_Run.Run_Id"))
    test_result_uuid = Column("Test_Result_UUID", NVARCHAR(100))
    machine_ip = Column("Machine_IP", NVARCHAR(100))
    response_code = Column("Response_code", Integer)
    response_time = Column("Response_time", Integer)
    connect_time = Column("Connect_time", Integer)
    latency = Column("Latency", Integer)
    size_in_bytes = Column("Size_In_Bytes", Integer)
    body_size_in_byte = Column("Body_Size_In_Byte", Integer)
    sample_count = Column("Sample_Count", Integer)
    response_code_error_count = Column("Response_Code_Error_Count", Integer)
    response_assertion_outcome = Column("Response_Assertion_OutCome", NVARCHAR(10))
    request_message = Column("Request_message", NVARCHAR(None))
    response_message = Column("Response_message", NVARCHAR(None))
    datetime = Column("Datetime", DateTime)

    test_run = relationship("APITestRun", back_populates="test_results")


class APIUITaskMapping(Base):
    __tablename__ = "API_UI_Task_Mapping"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    request_type = Column("RequestType", String(250), nullable=True)
    product_key = Column("ProductKey", BigInteger, nullable=True)
    task_id = Column("TaskId", Integer, nullable=True)
    transaction_id = Column("TransactionId", BigInteger, nullable=True)
    status = Column("Status", String(250), nullable=True)
    datetime = Column("Datetime", DateTime, nullable=True)
    env = Column("Env", String(250), nullable=True)
    domain = Column("Domain", String(250), nullable=True)
    entity = Column("Entity", String(250), nullable=True)
    is_az_pipeline = Column("IsAZPipeline", String(250), nullable=True)
    batch_processing_time_ms = Column("BatchProcessingTimeMS", Integer, nullable=True)
    batch_records = Column("BatchRecords", Integer, nullable=True)
    batch_errors = Column("BatchErrors", Integer, nullable=True)
