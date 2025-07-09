# 🧪 TestCrafter: The Ultimate ADO Test Case & Automation Artifact Generator

TestCrafter is a CLI tool that intelligently generates:

✅ Azure DevOps (ADO) Tasks  
✅ ADO Test Cases with dynamic test steps  
✅ Pytest-compatible Test Stubs
✅ YAML metadata files  
✅ Page Object class boilerplate

All from a **single ADO User Story**.

---

## 🚀 Features

- Parses raw or HTML-formatted acceptance criteria (`<li>`, `div`, or `1.`, `2.`, etc.)
- Automatically generates:
    - Linked ADO tasks
    - ADO test cases with step-level content
    - Clean, short, smart file names
    - Fully structured test cases using Pytest and Allure
    - YAML configs with literal multiline blocks
    - Page Objects with logging, DB injection, and ADO step tracking

---

## 🛠 Installation

```bash
pip install -r requirements.txt
```

Ensure your ADO PAT is set via environment variable:

```bash
export HITL_ADO_PAT=your_pat_here
# On Windows:
# set HITL_ADO_PAT=your_pat_here
```

---

## 📦 Usage

```bash
python testcrafter.py --story-id 1047654 --output-dir ./tests/generated
```

---

## 📂 Output Structure

When run, `TestCrafter` will create:

```
./tests/generated/
├── test_calculate_batch_processing_time.py        ← Pytest test stub
├── test_calculate_batch_processing_time.yaml      ← Allure metadata (with clean YAML blocks)
├── calculate_batch_processing_time_page.py        ← Page Object boilerplate
```

All names are generated using smart keyword extraction from the ADO User Story title.

---

## 🧾 Sample Output: YAML (Literal block format)

```yaml
description: |
  - Acceptance Criteria:
  - Transaction Detection:
    After a batch task submission, the system should identify...
  - Time Calculation:
    The system should compute the batch processing time...
```

---

## 🔄 How It Works

### 🧩 Parsing Acceptance Criteria

The tool supports:

- `<li>` formatted HTML
- `<div>`-based HTML structures
- Plain text with numbered points like:
  ```
  1. Do this
  2. Then this
  3. Expect that
  ```

### 🧱 Generated Test Stub Includes:

```python
def test_story_<


id > (page, test_user, reporter, ado_runner, request):
test_create_adhoc_product_tasks(...)
login_to_dashboard(...)
navigate_to_hitl_dashboard(...)
select_domain_card(...)
run_sample_flow(...)
```

### 📘 Page Object Includes:

- Logging via `LoggerPage`
- DB injection with `TaskIdMapperDAO(get_test_db_engine())`
- Allure step annotations
- A working `sample_interaction()` method

---

## 🧪 Example Scenario

### ADO Story:

**Title**: _HITL - QA Automation: Calculate batch processing time_  
**Acceptance Criteria**:

```
1. Detect TransactionId from submitted batch
2. Compute processing duration from DB timestamps
3. Check for error logs by TransactionId
4. Set batch status based on conditions
```

### Output:

✅ 4 ADO Tasks  
✅ 1 Test Case with 4 test steps  
✅ 3 Files created:

- `test_calculate_batch_processing_time.py`
- `test_calculate_batch_processing_time.yaml`
- `calculate_batch_processing_time_page.py`

---

## 🔐 Security

Make sure your `HITL_ADO_PAT` is kept private. Consider loading it from `.env` for CI/CD use.

---

## 📘 Roadmap

- ✅ CLI support
- ✅ Short + readable file naming
- ✅ Page Object autogen
- ✅ Literal YAML output
- 🔜 Markdown doc stub generation
- 🔜 Interactive prompts

---

## 📜 License

Vizient VizTech © 2025

---