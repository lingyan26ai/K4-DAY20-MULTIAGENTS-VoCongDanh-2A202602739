# Tái lập thí nghiệm

**Lần nộp hiện tại bị chặn API.** Chỉ thực hiện được toàn bộ learn baseline/subagents, ba lượt skills-auto phát triển, đóng băng và một phần baseline eval. Theo yêu cầu người thực hiện, đã dừng API và chốt báo cáo với kết quả còn thiếu. Các lệnh dưới là quy trình đầy đủ để tiếp tục khi API hoạt động, không phải khẳng định tất cả đã chạy thành công. Xem experiment-status.json để biết từng ô.

Chạy trên Linux có Python 3.12, Git và shell. Cài theo README: `python -m pip install -e .`. Điền `.env` từ `.env.example`: `LAB_MODEL=openai/gpt-4o-mini`, `LAB_BASE_URL=https://openrouter.ai/api/v1`, `LAB_TEMPERATURE=0`, `LAB_API_KEY=<key riêng>`. Không đưa key vào Git.

Các lệnh dưới đây tái lập quy trình trên checkout mới. Không chạy đè bằng chứng đã nộp nếu muốn giữ kết quả cũ. Mô hình có thể trả kết quả khác dù nhiệt độ 0.

```bash
python report/reproduce.py --condition baseline --tasks learn
python report/reproduce.py --condition subagents --tasks learn
python report/reproduce.py --condition curator --max-tokens 4096
# Đọc và đánh giá skill; không chỉnh nội dung skill sinh ra.
python report/reproduce.py --condition skills-auto --tasks learn
cp -r results/skills-auto results/skills-auto-dev
# Điền H1-H3 và phân tích learn trong report/REPORT.md trước khi xem eval.
git add src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report skills/auto results
git commit -m hypotheses
git commit --allow-empty -m 'freeze skills'
git tag freeze
python report/reproduce.py --condition baseline --tasks eval --workers 1
python report/reproduce.py --condition subagents --tasks eval --workers 1
python report/reproduce.py --condition skills-auto --tasks all --workers 1
python -m lab.compare > report/table.md
python scripts/check_breakdown.py > report/check_breakdown.txt
# Hoàn thiện phần phân tích và kết luận từ kết quả thật, rồi kiểm tra cuối.
python -m pytest tests
python scripts/verify_freeze.py
git diff --check -- src/lab report skills
```

Các batch learn dùng tối đa 3 tác vụ độc lập đồng thời, cùng mô hình, nhiệt độ 0, max_tokens 2048, recursion_limit 60, timeout API 60 giây và max_retries 1. Sau lỗi 402 in-flight ở baseline eval, các lượt tiếp theo dùng `--workers 1` và chờ Retry-After 120 giây trước khi chạy lại. Lượt lỗi lưu trong results/infra; không giữ lượt API lỗi làm kết quả chính. Curator dùng phản hồi learn và tối đa 3 skill; hai lần đầu của lần nộp không sinh skill hợp lệ, lần 3 có thêm hướng dẫn tên gạch ngang. Đầu ra lần 2/3 được lưu trong report để giải thích việc chạy lại.

Trên máy thực hiện, Python và thư viện đặt trong runtime Linux tạm trên `/mnt/host/wsl/` để tránh I/O chậm của ổ Windows. Sandbox có `python` trên PATH, không cài pandas, không có alias `python3`; đây là hạn chế môi trường đã ghi trong REPORT. Không cần sao chép runtime `.venv/` khi nộp.

Trace giữ nguyên đầu ra của render_trace, kể cả khoảng trắng cuối dòng có trong log/tool output; không chỉnh lại bằng chứng chỉ để làm sạch whitespace.
