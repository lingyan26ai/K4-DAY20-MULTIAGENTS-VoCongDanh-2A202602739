# Tiến độ nửa đầu lab

Phạm vi đã cài đặt: phần nền tảng và mã nguồn. Phần thí nghiệm bằng mô hình thật và phân tích số liệu dành cho nửa sau. Đây chưa phải bài hoàn chỉnh để nộp.

## Mã nguồn

| Tệp | Đã thực hiện |
|---|---|
| `src/lab/subagents.py` | Ba vai trò explorer, implementer, reviewer; nêu rõ điều kiện gọi và phạm vi công việc. |
| `src/lab/agent.py` | Backend shell dùng đường dẫn tương đối, PATH có Python, không kế thừa biến môi trường; dựng đúng chế độ single/subagents và tùy chọn skill. |
| `src/lab/runner.py` | Sandbox tạm ngoài repo; lưu điểm, check, token, thời gian, số lần gọi tool/subagent, skill đã đọc, hash skill và timestamp; ghi lỗi khi agent thất bại; dọn sandbox. |
| `src/lab/curator.py` | Lấy phản hồi và cuối trace từ tác vụ học hợp lệ; gọi model một lần; dùng hàm kiểm tra có sẵn để lọc skill; không gọi model khi không có lỗi cần học. |

`report/REPORT.md` giữ cấu trúc mẫu, đã điền cấu hình môi trường, mục 3 từ tour thật và phần thiết kế subagent ở mục 5. Các mục cần kết quả thí nghiệm vẫn chưa có số liệu.

## Môi trường và kiểm tra

Runtime Python Linux nằm trong `.venv/`; môi trường ảo nằm trong `.venv/linux/`. Chạy qua WSL hiện có trên máy. Toàn bộ `.venv/` được Git bỏ qua.

Lệnh kiểm tra từ PowerShell trên máy hiện tại:

```powershell
wsl -d docker-desktop -- sh -lc 'cd /mnt/host/d/AI_Vin/K4-DAY20-MULTIAGENTS-VoCongDanh-2A202602739 && PYTHONDONTWRITEBYTECODE=1 .venv/linux/bin/python -m pytest tests'
```

Nếu chuyển sang máy khác, tạo môi trường Linux mới và cài bằng `python -m pip install -e .` theo README; không sao chép `.venv/`.

Kết quả kiểm tra ngày 06/10/2026: **32 passed in 87.87s**.

| Bộ test | Kết quả |
|---|---|
| `test_01_provided.py` | 15 test đạt |
| `test_02_agent.py` | 9 test đạt |
| `test_03_runner.py` | 6 test đạt |
| `test_04_curator.py` | 2 test đạt |

Tour đã chạy thành công bằng mô hình giả, liệt kê 9 công cụ và system prompt mặc định rỗng. Kiểm tra cấu trúc mã xác nhận các prompt, `CONDITIONS`, `render_trace`, `main`, `SAFE_NAME`, `validate_skill` và `parse_skill_blocks` giữ nguyên. `git diff --check` không báo lỗi; các tệp được cung cấp trong `tasks/`, `tests/`, `scripts/` và các module còn lại không bị sửa.

Test offline dùng mô hình giả; số token giả và điểm của chúng không phải số liệu thí nghiệm. Không tạo bảng so sánh từ các kết quả này.

## Việc còn lại theo thứ tự

1. Cấu hình nhà cung cấp, mô hình hỗ trợ tool calling và ngân sách trong `.env`.
2. Chạy baseline và subagents trên ba tác vụ học; phân loại lỗi A–G từ check và trace thật.
3. Chạy curator, đánh giá skill tự sinh và thử skills-auto trên tác vụ học. Không sửa tay skill; sao lưu kết quả phát triển.
4. Điền H1–H3 từ bằng chứng và tài liệu, commit `hypotheses`, rồi commit/tag `freeze`.
5. Chạy baseline/subagents trên eval và skills-auto trên cả sáu tác vụ; chạy `verify_freeze.py`.
6. Sinh `table.md`, thống kê check, hoàn thiện báo cáo với số liệu thật và phân tích nhiễu/hạn chế.

Chưa chạy thí nghiệm bằng API, chưa sinh skill, chưa commit hoặc tạo tag freeze.
