# utils/allure_writer.py
import json
import logging
import os
from datetime import datetime

from utils.ado.ado_test_plan_reader import fetch_total_planned_cases

logger = logging.getLogger("HitlLogger")


def allure_generate_categories_and_piecharts(session):
    write_allure_categories(allure_results_dir="allure-results")

    total_cases = fetch_total_planned_cases(session.ado_runner)
    executed_cases = session.ado_runner.executed_test_count
    passed_cases = session.ado_runner.passed_test_count
    failed_cases = session.ado_runner.failed_test_count
    skipped = session.ado_runner.skipped_test_count

    write_allure_pie_chart(
        total=total_cases,
        passed=passed_cases,
        failed=failed_cases,
        skipped=skipped
    )


# Update fancy summary generation
def generate_fancy_summary(session, runner):
    # total_cases = fetch_total_planned_cases(session.ado_runner)
    # executed_cases = session.ado_runner.executed_test_count
    # passed_cases = session.ado_runner.passed_test_count
    # failed_cases = session.ado_runner.failed_test_count
    # skipped = session.ado_runner.skipped_test_count

    # change here
    total_cases = fetch_total_planned_cases(runner)
    executed_cases = runner.executed_test_count
    passed_cases = runner.executed_test_count - len(runner.failures)
    skipped = runner.skipped_test_count

    html_content = generate_fancy_summary_html(
        total=total_cases,
        executed=executed_cases,
        passed_cases=passed_cases,
        failed_cases=len(runner.failures),
        skipped=skipped
    )

    summary_file = os.path.join("allure-results", "test_coverage_report.html")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Fancy summary written at {summary_file}")


def write_allure_environment_file(output_dir, test_user=None, metadata=None):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"📁 Created Allure results folder at: {output_dir}")

        # Write environment.properties
        env_prop_file = os.path.join(output_dir, "environment.properties")
        with open(env_prop_file, "w") as f:
            if test_user:
                f.write(f"Test={test_user.test_env}\n")
                f.write(f"Application={test_user.test_application}\n")
                f.write(f"Browser={test_user.browser_type}\n")
                f.write(f"User={test_user.user_id}\n")

            if metadata:
                for k, v in metadata.items():
                    f.write(f"{k.upper()}={v}\n")

        logger.info("✅ Allure environment.properties file created.")

        # Write environment.json
        env_json_file = os.path.join(output_dir, "environment.json")
        env_data = []

        if test_user:
            env_data.extend([
                {"name": "Test", "value": test_user.test_env},
                {"name": "Application", "value": test_user.test_application},
                {"name": "Browser", "value": test_user.browser_type},
                {"name": "User", "value": test_user.user_id},
            ])

        if metadata:
            for k, v in metadata.items():
                env_data.append({"name": k.upper(), "value": v})

        with open(env_json_file, "w") as f:
            json.dump(env_data, f, indent=4)

        logger.info("✅ Allure environment.json file created.")

    except Exception as e:
        logger.warning(f"⚠️ Failed to create Allure environment file: {e}")


def write_allure_executor_file(output_dir, executor_data=None):
    try:
        executor_file = os.path.join(output_dir, "executor.json")
        default_executor_data = {
            "name": "Local Run",
            "type": "pytest",
            "reportName": "HITL Test Report",
            "reportUrl": "",
            "buildName": "",
            "buildUrl": ""
        }

        with open(executor_file, "w") as f:
            json.dump(executor_data or default_executor_data, f, indent=4)

        logger.info("✅  Allure executor.json file created.")
    except Exception as e:
        logger.warning(f"⚠️ Failed to create Allure executor.json file: {e}")


def write_allure_categories_file(output_dir, categories=None):
    try:
        categories_file = os.path.join(output_dir, "categories.json")
        default_categories = categories or [
            {"name": "Ignored tests", "matchedStatuses": ["skipped"]},
            {"name": "Infrastructure problems", "matchedStatuses": ["broken"]},
            {"name": "Product defects", "matchedStatuses": ["failed"]}
        ]

        with open(categories_file, "w") as f:
            json.dump(default_categories, f, indent=4)

        logger.info("✅  Allure categories.json file created.")
    except Exception as e:
        logger.warning(f"⚠️ Failed to create Allure categories.json file: {e}")


def write_allure_categories(allure_results_dir="allure-results"):
    """
    Dynamically creates an Allure categories.json for better failure grouping.
    """

    categories = [
        {
            "name": "Timeouts",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*Timeout.*"
        },
        {
            "name": "Assertion Failures",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*"
        },
        {
            "name": "Element Not Found",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*NoSuchElementException.*"
        },
        {
            "name": "Server Errors",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*500 Server Error.*"
        },
        {
            "name": "Unknown Failures",
            "matchedStatuses": ["failed"]
        }
    ]

    os.makedirs(allure_results_dir, exist_ok=True)
    categories_file = os.path.join(allure_results_dir, "categories.json")

    with open(categories_file, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2)

    print(f"✅ Allure categories.json generated at {categories_file}")


def write_allure_pie_chart(total, passed, failed, skipped=0, allure_results_dir="allure-results"):
    """
    Write a simple pie chart dataset as JSON to Allure Results folder.
    """

    data = {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "skipped_tests": skipped,
        "pass_rate": round((passed / total) * 100, 2) if total else 0
    }

    os.makedirs(allure_results_dir, exist_ok=True)
    pie_chart_file = os.path.join(allure_results_dir, "pie_chart_data.json")

    with open(pie_chart_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Allure Pie Chart JSON created at {pie_chart_file}")


def generate_fancy_summary_html(total, executed, passed_cases, failed_cases, skipped):
    passed_cases = executed - failed_cases if executed >= failed_cases else 0
    coverage = (executed / total) * 100 if total else 0
    pass_percentage = (passed_cases / executed) * 100 if executed else 0
    fail_percentage = (failed_cases / executed) * 100 if executed else 0
    skip_percentage = (skipped / total) * 100 if total else 0

    if pass_percentage == 100:
        overall_health = "Overall health: Excellent"
    elif pass_percentage >= 80:
        overall_health = "Overall health: Good"
    elif pass_percentage >= 50:
        overall_health = "Overall health: Needs Attention"
    else:
        overall_health = "Overall health: Critical"

    health_color = "green" if pass_percentage >= 80 else "orange" if pass_percentage >= 50 else "red"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
    <html>
    <head>
        <title>HITL Test Execution Summary</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                background-color: #0b0f1a;
                color: #f1f5f9;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 30px;
            }}
            .dashboard {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #111827;
                border-radius: 12px;
                box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
                padding: 40px;
                max-width: 900px;
                margin: auto;
            }}
            .summary {{
                flex: 1;
                padding-right: 40px;
            }}
            .summary h2 {{
                font-size: 28px;
                margin-bottom: 20px;
                color: white;
            }}
            .summary ul {{
                list-style: none;
                padding: 0;
                font-size: 18px;
                line-height: 1.8;
            }}
            .summary ul li strong {{
                color: #60a5fa;
            }}
            .health {{
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
                color: {health_color};
            }}
            .chart-container {{
                flex: 1;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="summary">
                <h2>HITL Test Execution Summary</h2>
                <ul>
                    <li><strong>Date:</strong> {timestamp}</li>
                    <li><strong>Total Planned:</strong> {total}</li>
                    <li><strong>Executed:</strong> {executed}</li>
                    <li><strong>Passed:</strong> {passed_cases}</li>
                    <li><strong>Failed:</strong> {failed_cases}</li>
                    <li><strong>Skipped:</strong> {skipped}</li>
                    <li><strong>Test Coverage:</strong> {coverage:.2f}%</li>
                    <li><strong>Pass %:</strong> {pass_percentage:.2f}%</li>
                    <li><strong>Fail %:</strong> {fail_percentage:.2f}%</li>
                    <li><strong>Skip %:</strong> {skip_percentage:.2f}%</li>
                </ul>
                <div class="health">{overall_health}</div>
            </div>
            <div class="chart-container">
                <canvas id="resultChart" width="250" height="250"></canvas>
                <div style="margin-top: 20px;">
                    <span style="color:#22c55e; font-weight:bold;">&#9632;</span> Passed &nbsp;&nbsp;
                    <span style="color:#ef4444; font-weight:bold;">&#9632;</span> Failed &nbsp;&nbsp;
                    <span style="color:#facc15; font-weight:bold;">&#9632;</span> Skipped
                </div>
            </div>
        </div>

        <script>
            const ctx = document.getElementById('resultChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Passed', 'Failed', 'Skipped'],
                    datasets: [{{
                        data: [{passed_cases}, {failed_cases}, {skipped}],
                        backgroundColor: ['#22c55e', '#ef4444', '#facc15'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    cutout: '60%',
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html


def write_fancy_summary_to_file(directory: str, content: str) -> str:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "fancy_test_summary.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
