import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy import MetaData, update, select, or_
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

hitlLogger = logging.getLogger("HitlLogger")


@dataclass
class TaskRow:
    TaskId: int
    Status: str


class TaskIdMapperDAO:
    def __init__(self, engine: Engine, table_name: str = "API_UI_Task_Mapping", schema: str = "dbo"):
        self.engine = engine
        self.schema = schema
        self.table_name = table_name
        self.metadata = MetaData()

        try:
            self.metadata.reflect(bind=self.engine, schema=self.schema, only=[self.table_name])
            self.table = self.metadata.tables[f"{self.schema}.{self.table_name}"]
            hitlLogger.info(f"✅  Table loaded: {self.schema}.{self.table_name}")
        except Exception as e:
            hitlLogger.error(f"❌ Failed to load table '{self.schema}.{self.table_name}': {e}")
            raise

    def update_task_status_to_resolved(self, test_user, task_id: str) -> int:
        stmt = (
            update(self.table)
            .where(self.table.c.TaskId == task_id)
            .where(self.table.c.Env == test_user.test_env)
            .values(Status="Resolved")
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

                updated = result.rowcount
                if updated > 0:
                    hitlLogger.info(f"✅  {updated} row(s) updated to 'resolved' for TaskId = {task_id}")
                else:
                    hitlLogger.info(f"⚠️ No rows updated for TaskId = {task_id}")

                return updated
        except SQLAlchemyError as e:
            hitlLogger.error(f"❌ Error updating task status: {e}")
            return 0

    def get_tasks_to_resolve(self, test_meta, test_user, no_of_tasks_to_resolve) -> List[TaskRow]:
        stmt = (
            select(self.table)
            .where(or_(
                self.table.c.Status == "Submitted",
                self.table.c.Status == "In Progress"
            ))
            .where(self.table.c.Env == test_user.test_env)
            .where(self.table.c.Domain == test_meta["domain"])
            .where(self.table.c.Entity == test_meta["entity"])
            .where(self.table.c.TaskId > 0)
            .order_by(self.table.c.TaskId.desc())
            .limit(no_of_tasks_to_resolve)
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                rows = result.fetchall()

                if not rows:
                    hitlLogger.info("⚠️ No database records found with status 'processing' and TaskId > 0.")
                    return []

                task_rows = []
                for row in rows:
                    task_rows.append(TaskRow(
                        TaskId=row.TaskId,
                        Status=row.Status
                        # Add other fields if needed
                    ))

                task_ids = [row.TaskId for row in task_rows]
                hitlLogger.info(f"🔹 Found {len(task_rows)} task(s) to resolve. TaskIds: {task_ids}")

                return task_rows

        except SQLAlchemyError as e:
            hitlLogger.error(f"❌ Error fetching tasks to resolve: {e}")
            return []

    def update_task_status_to_in_progress(self, test_user, task_id: str) -> int:
        stmt = (
            update(self.table)
            .where(self.table.c.TaskId == task_id)
            .where(self.table.c.Env == test_user.test_env)
            .values(Status="In Progress")
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

                updated = result.rowcount
                if updated > 0:
                    hitlLogger.info(f"✅  {updated} row(s) updated to 'In Progress' for TaskId = {task_id}")
                else:
                    hitlLogger.info(f"⚠️ No rows updated for TaskId = {task_id}")

                return updated
        except SQLAlchemyError as e:
            hitlLogger.error(f"❌ Error updating task status to In Progress: {e}")
            return 0
