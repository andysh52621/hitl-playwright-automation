from sqlalchemy.orm import Session

from db_models.api_test_db_models import APITestRun, APITestResult, APITestCaseConfig, APIUITaskMapping, \
    APIServiceConfig


class APITestServiceConfig:
    pass


class APITestDAO:

    # ✅ Insert API_Test_Run
    @staticmethod
    def insert_test_run(session: Session, data: dict) -> APITestRun:
        record = APITestRun(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    @staticmethod
    def update_test_run(session: Session, run_id: int, updates: dict) -> APITestRun:
        record = session.query(APITestRun).filter_by(run_id=run_id).first()
        for k, v in updates.items():
            setattr(record, k, v)
        session.commit()
        return record

    # ✅ Insert API_Test_Result
    @staticmethod
    def insert_test_result(session: Session, data: dict) -> APITestResult:
        record = APITestResult(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    @staticmethod
    def update_test_result(session: Session, result_id: int, updates: dict) -> APITestResult:
        record = session.query(APITestResult).filter_by(test_result_id=result_id).first()
        for k, v in updates.items():
            setattr(record, k, v)
        session.commit()
        return record

    # ✅ Insert API_Service_Config
    @staticmethod
    def insert_service_config(session: Session, data: dict) -> APIServiceConfig:
        record = APIServiceConfig(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    @staticmethod
    def update_service_config(session: Session, service_id: int, updates: dict) -> APIServiceConfig:
        record = session.query(APIServiceConfig).filter_by(service_id=service_id).first()
        for k, v in updates.items():
            setattr(record, k, v)
        session.commit()
        return record

    # ✅ Insert API_Test_Case_Config
    @staticmethod
    def insert_test_case(session: Session, data: dict) -> APITestCaseConfig:
        record = APITestCaseConfig(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    @staticmethod
    def update_test_case(session: Session, test_case_id: int, updates: dict) -> APITestCaseConfig:
        record = session.query(APITestCaseConfig).filter_by(test_case_id=test_case_id).first()
        for k, v in updates.items():
            setattr(record, k, v)
        session.commit()
        return record

    # ✅ Insert API_UI_Task_Mapping
    @staticmethod
    def insert_ui_mapping(session: Session, data: dict) -> APIUITaskMapping:
        record = APIUITaskMapping(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    @staticmethod
    def update_ui_mapping(session: Session, testcase_id: int, updates: dict) -> APIUITaskMapping:
        record = session.query(APIUITaskMapping).filter_by(testcase_id=testcase_id).first()
        for k, v in updates.items():
            setattr(record, k, v)
        session.commit()
        return record
