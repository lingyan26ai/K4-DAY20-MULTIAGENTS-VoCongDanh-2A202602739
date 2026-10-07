"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Use before implementation when specifications, docstrings or input formats need inspection.",
            "system_prompt": (
                "Read the delegated task, README, docstrings and representative input data. "
                "Report requirements, edge cases and evidence with file paths. Do not change files."
            ),
        },
        {
            "name": "implementer",
            "description": "Use when a scoped code fix, data transformation or log parser needs implementation.",
            "system_prompt": (
                "Implement only the delegated changes and follow every supplied task rule. "
                "Inspect shared functions before fixing symptoms. Preserve existing tests. "
                "Run relevant checks and report changed files, observed results and unresolved issues."
            ),
        },
        {
            "name": "reviewer",
            "description": "Use after implementation to independently check outputs against the specification and edge cases.",
            "system_prompt": (
                "Inspect the delegated outputs and compare them with all supplied requirements. "
                "Run tests or independent calculations where appropriate. Do not change files. "
                "Report observed evidence, failures and any checks you could not perform."
            ),
        },
    ]
