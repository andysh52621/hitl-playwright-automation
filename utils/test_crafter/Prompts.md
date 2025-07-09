# 🔁 Prompt Blueprint for Building TestCrafter

This document captures the core AI prompts used to create the `TestCrafter` CLI tool — a powerful ADO-integrated test artifact generator.

---

## 🧠 Project Goal Prompt

> I want to build a CLI tool that, given a user story ID from Azure DevOps, can:
> - Create ADO Tasks from acceptance criteria
> - Create a linked ADO Test Case with test steps
> - Generate a Pytest test stub
> - Generate a YAML metadata file
> - Generate a Page Object Python file
>
> Let’s call it `TestCrafter`. Guide me through this.

---

## 🔍 Acceptance Criteria Parsing Prompts

> Here's the raw script for TestCrafter. It's not creating multiple tasks or test steps properly. Can you look at the acceptance criteria parsing and fix it so each bullet point becomes a task and step?

> The acceptance criteria is plain text, not HTML. Update parsing to handle both numbered bullets and regular paragraphs.

> Sometimes acceptance criteria comes as:
> - `<li>` tags
> - HTML `<div>` with `<br>`
> - Or as just `1.`, `2.` bullets
>
> Modify `TestCrafter` to detect format and convert them to clean line items that the rest of the script can use.

---

## 🔁 Preprocessing Strategy Prompt

> Let's reset back to the original version of TestCrafter where it only worked with `<li>`s. We’ll preprocess user stories into `<li>` format first, then let the original logic work.

---

## 🧹 HTML Cleanup Prompt

> Here's an example user story with `<div>`, `<span>`, and `&nbsp;`. It’s creating one giant task. Write a `convert_to_line_items()` function to:
> - Remove noisy tags
> - Extract numbered bullets
> - Convert into multiple `<li>` entries

---

## 📛 File Naming Strategy Prompt

> The filenames and class names generated are too long and unreadable. I want you to:
> - Shorten them to 50 characters max
> - Remove common stopwords like `qa`, `automation`, etc.
> - Use top 5 keywords
> - Provide fallback like `test_story_<id>`

---

## 🧪 Test Stub Update Prompt

> Here’s a sample test stub. It includes:
> - Correct imports
> - Updated function call: `test_create_adhoc_product_tasks()`
> - Page interaction
>
> Replace the default test stub logic in `generate_test_file()` with this.

---

## 🧾 YAML Output Fix Prompt

> The YAML file you're generating escapes newlines (`\n`). I want it to produce clean, readable literal block format using `|` instead.

> Fix `generate_yaml_file()` so multiline descriptions:
> - Use `style='|'`
> - Preserve indentation and formatting

---

## 🧩 Final Cleanup Prompt

> Give me a complete, clean version of `TestCrafter.py` with:
> - All logic fixed
> - Proper filename handling
> - Literal YAML block formatting
> - Updated test stub and page object model

---

## 📘 README Prompt

> Now create a complete, well-documented `README.md` that includes:
> - Features
> - Installation
> - Usage
> - Output examples
> - YAML samples
> - Use cases
> - Roadmap

---

## 🔁 Summary Prompt

> Can you collect and summarize all the prompts I used today that helped us build this? I want to reuse these in future.

---

## 📋 Bonus Prompts for Future Use

- "Given a user story title, generate a short, smart test filename (≤50 characters) using keywords."
- "Create a YAML description field from bullet points, formatted with literal `|` block."
- "Convert numbered acceptance criteria text to HTML `<li>` format."
- "Create a Page Object class boilerplate with logging, DB access, Allure steps, and error handling."
- "Update a Python function to use `get_test_db_engine()` instead of `get_engine()`."
- "Generate a Pytest test stub using Allure and ADO decorators."

---