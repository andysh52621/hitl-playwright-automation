import os
import subprocess
from datetime import datetime

from utils.ado.ado_test_plan_reader import fetch_total_planned_cases


def generate_html_email(runner, test_user, failure_details_html: str) -> str:
    run_env = os.getenv("RUN_ENV", "").lower() or test_user.test_env
    is_pipeline = os.getenv("IS_PIPELINE", "local").lower()
    run_type = "PIPELINE" if is_pipeline == "cicd" else "LOCAL"
    failed = len(runner.failures)
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M%p")

    try:
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    except Exception as e:
        branch_name = "unknown"

    total_cases = fetch_total_planned_cases(runner)
    executed_cases = runner.executed_test_count
    passed_cases = runner.executed_test_count - len(runner.failures)
    skipped = runner.skipped_test_count

    ado_run_url = f"{runner.org_url}/{runner.project}/_TestManagement/Runs?runId={runner.run_id}&_a=runCharts"

    html_body = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
            color: #333;
          }}
          .container {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            max-width: 800px;
            margin: auto;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          }}
          .header {{
            text-align: center;
            margin-bottom: 30px;
          }}
          .badges span {{
            background: #007acc;
            color: white;
            padding: 6px 12px;
            margin-right: 8px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
          }}
          h2 {{
            color: #c0392b;
            margin-bottom: 10px;
          }}
          h3 {{
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 10px;
          }}
          ul.failures li {{
            margin-bottom: 15px;
          }}
          ul.failures li a {{
            display: block;
            margin: 3px 0;
          }}
          .summary-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
            margin-top: 15px;
          }}
          .summary-table th, .summary-table td {{
            border: 1px solid #ccc;
            padding: 8px 12px;
            text-align: center;
          }}
          .footer {{
            text-align: center;
            font-size: 11px;
            color: #888;
            margin-top: 40px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h2>❌ HITL Automation Test Report</h2>
            <div class="badges">
              <span>Project: HITL</span>
              <span>Env: {run_env.upper()}</span>
              <span>Branch: {branch_name}</span>
              <span>{run_type}</span>
              <span>{timestamp}</span>
            </div>
          </div>

          <h3>❌ Failed Test Cases ({failed})</h3>
          <ul class="failures">
            {failure_details_html}
          </ul>

          <h3>🔗 View Full ADO Test Run</h3>
          <p><a href="{ado_run_url}" target="_blank">{ado_run_url}</a></p>

          <h3>📄 Attached HTML Report</h3>
          <p>The test report is attached as <b>pytest_html_report.html</b>.</p>

          <h3>📊 Execution Summary</h3>
          <table class="summary-table">
            <tr style="background-color:#f2f2f2;">
              <th>Total</th>
              <th>Executed</th>
              <th>Passed</th>
              <th>Failed</th>
              <th>Skipped</th>
            </tr>
            <tr>
              <td>{total_cases}</td>
              <td>{executed_cases}</td>
              <td>{passed_cases}</td>
              <td>{failed}</td>
              <td>{skipped}</td>
            </tr>
          </table>

          <div class="footer">
            — HITL Automation Framework · Powered by Playwright + Pytest + Azure DevOps
          </div>
        </div>
      </body>
    </html>
    """
    return html_body
