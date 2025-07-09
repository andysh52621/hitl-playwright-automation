from datetime import datetime

from db_engine.test_automation_engine import get_test_db_session
from db_models.ui_test_db_models import TestCase, TestExecution, TestStep


class DBReporter:
    def __init__(self):
        self.session = get_test_db_session()
        self.execution = None
        self._execution_ended = False

    def start_test_execution(
            self, test_name, description, env, browser,
            domain=None, entity=None, created_by=None, from_pipeline=None,
            ado_plan_id=None, ado_suite_id=None, ado_case_id=None, build_definition_id=None
    ):
        test_case = self.session.query(TestCase).filter_by(Test_Case_Name=test_name).first()
        if not test_case:
            test_case = TestCase(
                Test_Case_Name=test_name,
                Description=description,
                Domain=domain,
                Entity=entity,
                Created_by=created_by,
                Ado_Plan_Id=ado_plan_id,
                Ado_Suite_Id=ado_suite_id,
                Ado_Case_Id=ado_case_id,
                Build_Definition_Id=build_definition_id
            )
            self.session.add(test_case)
        else:
            # Update existing test case with new metadata
            test_case.Description = description
            test_case.Domain = domain
            test_case.Entity = entity
            test_case.Created_by = created_by
            test_case.Ado_Plan_Id = ado_plan_id
            test_case.Ado_Suite_Id = ado_suite_id
            test_case.Ado_Case_Id = ado_case_id
            test_case.Build_Definition_Id = build_definition_id
            self.session.add(test_case)

        self.session.commit()

        self.execution = TestExecution(
            Test_Case_Id=test_case.ID,
            Outcome='RUNNING',
            Start_Time=datetime.now(),
            Environment=env,
            Browser=browser,
            From_Pipeline=from_pipeline
        )
        self.session.add(self.execution)
        self.session.commit()

    def end_test_execution(self, status, error_message=None):
        if self.execution and not self._execution_ended:
            self.execution.Outcome = status
            self.execution.End_Time = datetime.now()
            self.execution.Error_Message = error_message
            self.session.add(self.execution)
            self.session.commit()
            self._execution_ended = True
        elif self._execution_ended:
            print(f"⚠️ Test execution already ended. Skipping duplicate status update.")
        else:
            print("⚠️ No execution started. Cannot end test execution.")

    def add_step(self, step_name, status, details=None):
        if not self.execution:
            print("⚠️ Cannot add step — test execution not started.")
            return
        step = TestStep(
            Execution_Id=self.execution.ID,
            Step_Desc=step_name,
            Outcome=status,
            Timestamp=datetime.now(),  # ✅ Local time
            Details=details
        )
        self.session.add(step)
        self.session.commit()
