# Báo cáo Lab: Self evolving Agentic


## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| VoCongDanh | 2A202602739 | Hoàn thiện harness, tổ chức thí nghiệm và phân tích báo cáo. |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenRouter, `openai/gpt-4o-mini`, nhiệt độ 0, `recursion_limit=60`. Giới hạn đầu ra mỗi lời gọi là 2.048 token, timeout API 60 giây, tối đa 1 lần thử lại; giữ cùng cấu hình cho các điều kiện hợp lệ.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, Python `3.12.14`; chạy trực tiếp trong Linux qua WSL `docker-desktop` trên máy Windows, không chạy container Docker.
- Trước đóng băng: 9 lần chạy tác vụ học (3 baseline, 3 subagents, 3 skills-auto phát triển), 3 lần gọi curator; ngân sách tiền không được cung cấp. Kết quả chính thức dự kiến 18 ô, kèm 3 lần học phát triển để đo nhiễu. Các lần khởi động lỗi lưu riêng, không cộng vào bảng chính.
- Commit của tag `freeze`: chưa tạo; sẽ tạo sau khi sinh skill và commit H1–H3.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): dự đoán điểm trung bình eval của subagents cao hơn baseline, nhưng token trung bình cũng cao hơn. Baseline code-learn chỉ đạt 4/10: tác tử sửa test có sẵn và bỏ sót hai yêu cầu docstring. Explorer/reviewer có thể giúp đọc và đối chiếu đặc tả đầy đủ hơn. Anthropic mô tả lợi ích của phân việc và chi phí token lớn hơn trong hệ thống nghiên cứu đa tác tử; kết quả đó thuộc bối cảnh khác, không dùng mức tăng của họ làm dự báo định lượng cho lab này.
- H2 (skills-auto so với baseline): dự đoán skills-auto có điểm eval cao nhất trong ba điều kiện nhờ nhớ quy ước chung từ phản hồi tác vụ học, nhưng vẫn có thể bỏ sót quy ước mới. Ba check quy ước ở baseline code-learn đều thất bại, tạo phản hồi rõ cho curator. Đây là dự đoán cần kiểm chứng: SkillsBench ghi nhận skill tự sinh không có lợi trung bình, nên không mặc định việc thêm skill sẽ tăng điểm.
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán điểm trung bình skills-auto trên learn cao hơn eval vì skill được rút từ learn, còn eval đổi dữ liệu và thêm quy ước. SkillEvolBench cho thấy lợi ích ở tác vụ đã gặp có thể không chuyển ổn định sang tình huống mới; cần tách learn/eval và so sánh hai lần chạy learn để tránh nhầm nhiễu với quá khớp.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tour liệt kê 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ `execute` chạy lệnh shell; `task` giao việc cho subagent.
2. `general-purpose` dùng để nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và làm việc nhiều bước; có cùng công cụ như tác tử chính. Mỗi lần gọi mặc định là một phiên mới, chỉ thấy prompt được giao và trả lại một báo cáo cuối. Vì vậy tác tử chính phải truyền đủ yêu cầu và đường dẫn.
3. Tour xác nhận system prompt mặc định là chuỗi rỗng (`''`), nhưng mô tả tool vẫn hướng dẫn hành vi. Trong `task`: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Trong `execute`: “Quote paths containing spaces (e.g. cd \"/path/with spaces\").”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | tests_not_modified | G — sửa tệp bị cấm | `the original files in tests/ must not be modified (new test files are allowed)`; tác tử sửa test trong sandbox dù đề cấm. |
| code-learn | parse_price_all_formats | B — kiểm chứng chưa đủ | `wrong for: ['(12.00)']`; đã đọc docstring nhưng chỉ chạy suite sẵn có, chưa kiểm tra ca ngoặc biểu thị số âm. |
| code-learn | csv_quoting_follows_docstring | B — kiểm chứng chưa đủ | `to_csv_row returned 'Desk, large "oak",10.00,2'`; đã đọc đặc tả nhưng chưa đối chiếu CSV có dấu phẩy/dấu nháy. |
| code-learn | rule_type_hints | E — quy ước tổ chức | `RULE: every public function (name not starting with '_') in the package has type hints...` |
| code-learn | rule_regression_tests | E — quy ước tổ chức | `RULE: add tests/test_regressions.py with one test function per bug you fixed...` |
| code-learn | rule_changelog | E — quy ước tổ chức | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet...` |

| logs-learn | entry_count | D — bỏ sót dữ liệu | `wrong number of entries (got 13)`; viết JSON thủ công sau hai lần đọc log, không dùng chương trình kiểm đếm. |
| logs-learn | timestamps_utc | D — định dạng thời gian | `0/25 timestamps match`; output thiếu bản ghi và chuyển đổi thời gian không khớp. |
| logs-learn | exception_fields | D — traceback/kiểu dữ liệu | `25 wrong exception values`; trace ghi chuỗi `"null"` thay cho JSON null ở nhiều entry. |
| logs-learn | repeat_counts | D — dữ liệu lặp | `25 wrong repeat_count values`; không đối chiếu các dòng thông báo lặp. |
| logs-learn | counts_by_service | D — tổng hợp sai | `counts_by_service: wrong values`; kết quả phụ thuộc số entry và repeat_count sai. |
| logs-learn | rule_service_names | E — quy ước tổ chức | `service names ... lower-case with '-' replaced by '_'`; JSON vẫn dùng tên có gạch ngang. |
| logs-learn | rule_sorted_errors | E — quy ước tổ chức | `errors is sorted by service, then by timestamp_utc, ascending`; chưa thực hiện quy ước. |
| logs-learn | rule_schema_header | E — quy ước tổ chức | Thiếu `schema_version: 2` và `generated_by: log-triage`. |

Trong 14 check thất bại của hai lần chạy kết thúc bình thường, E nhiều nhất (6), rồi D (5), B (2), G (1). Các lỗi D có thể cùng nguyên nhân và không phải năm sự cố độc lập. Baseline logs chỉ đọc log rồi viết JSON, không có `execute` kiểm chứng; baseline code chạy test nhưng sửa test và bỏ sót ca biên. Skill về kiểm chứng toàn bộ đặc tả, xử lý dữ liệu bằng chương trình và lưu quy ước có thể phòng ngừa một phần các lỗi này. Không gán A khi vết chứng minh docstring đã được đọc; không gán F vì `errors.json` thật sự đã được tạo.

Baseline data-learn có `GraphRecursionError` sau giới hạn 60 bước; cả 8 check thất bại do không có `answer.json`. Vết lặp `python -c` với `with` đặt sau dấu chấm phẩy gây SyntaxError, rồi thử `python3` không có trên PATH. Đây là thất bại quá trình có yếu tố môi trường; không tính tám check này vào thống kê nguyên nhân E/D ở trên. Lỗi API 402 của lần khởi động nằm riêng trong `results/infra/`, không dùng làm bằng chứng lỗi tác tử.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): `explorer` đọc đặc tả và dữ liệu, không sửa tệp; `implementer` thực hiện thay đổi và kiểm tra; `reviewer` kiểm tra độc lập, không sửa tệp. Ba vai trò tách việc tìm hiểu, thực hiện và rà soát. Mỗi `description` nêu tình huống gọi; mỗi subagent nhận thêm quy ước đường dẫn tương đối.
- Trên learn, `subagent_calls`: code 0, data 3, logs 0. Cả ba lần giao việc của data đều gọi `implementer`; explorer/reviewer không được gọi. Việc có vai trò chuyên biệt không bảo đảm mô hình dùng chúng: code tự sửa và chạy test, logs chỉ đọc hai phần của log rồi dừng.
- Lời giao việc data có đường dẫn và năm chỉ số nhưng lược mất README, yêu cầu giải thích cách làm và chi tiết mốc cuối quý ở 23:59:59 UTC; nó không nêu quy ước Acme. Hai lần đầu implementer trả báo cáo không xử lý được môi trường, lần cuối trả kết quả. Tác tử chính không đọc lại `answer.json` hoặc chạy phép kiểm tra độc lập trước câu trả lời cuối. Trace chỉ chứa báo cáo subagent, không thấy nội bộ nên không suy đoán toàn bộ cách tính của nó.
- Token learn baseline/subagents lần lượt: code 61.345/91.089; data 338.755/233.878; logs 20.033/15.152. Thời gian subagents code/data/logs: 50,8/133,4/26,1 giây. Trung bình learn subagents 113.373 token thấp hơn baseline 140.044, nhưng baseline data bị lặp tới giới hạn; điều này không chứng minh đa tác tử vốn rẻ hơn. Điểm code bằng nhau 4/10, data tăng từ 0/8 lên 3/8, logs giảm từ 1/9 xuống 0/9.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator được gọi 3 lần (lần đầu và 2 lần chạy lại đúng giới hạn hướng dẫn). Hai lần đầu không có skill hợp lệ; lần 2 lưu ở `report/curator-attempt-2.json`, tên chứa dấu gạch dưới nên không đạt `SAFE_NAME`. Lần 3 bổ sung ví dụ tên gạch ngang vào prompt và sinh 3 skill; đầu ra và usage lưu ở `report/curator-attempt-3.json`. Không sửa tay nội dung và không xóa skill. Curator lần đầu dùng max_tokens 2.048, hai lần sau 4.096; tác tử giải tác vụ luôn dùng 2.048. Curator chỉ dùng baseline learn, loại lỗi API; phản hồi data có lỗi vòng lặp được giữ kèm trace để học lỗi quá trình.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| avoid-modifying-test-files | Tổng quát cho sửa mã với test bất biến. | Đúng với ràng buộc lab; câu “always” quá rộng cho dự án cho phép sửa test. Chưa hướng dẫn type hint, regression test theo từng bug hay changelog đúng mẫu. | 3 dòng thân; description: “Use this skill when working with test files to ensure that original test files remain unchanged.” |
| handle-file-not-found-errors | Tổng quát cho lỗi đường dẫn, không chứa đáp án hoặc dữ liệu học. | Hướng dẫn kiểm tra đường dẫn hợp lý nhưng chẩn đoán chưa đúng nguyên nhân baseline data: thiếu output do SyntaxError/vòng lặp, không phải thiếu input. Không dạy sửa cú pháp hoặc tránh lặp lệnh lỗi. | 3 dòng thân; description: “Use this skill when encountering file not found errors during data processing tasks.” |
| enforce-log-output-standards | Quy ước xử lý log học được, có thể áp dụng log mới. | Đúng về tên service và UTC; schema chỉ nói chung, thiếu schema_version/generated_by, sắp xếp, repeat_count và parser toàn bộ log. Không chứa dòng log hay đáp án cụ thể. | 3 dòng thân; description: “Use this skill when generating log outputs to ensure they meet specified formatting and content rules.” |

Lần phát triển trước freeze được sao lưu nguyên trạng ở `results/skills-auto-dev`: code 4/10, data 0/8 (GraphRecursionError), logs 1/9. Trên code/logs, `skills_read=0`: hành động đầu là tìm source/đọc log, không đọc SKILL.md. Vì vậy chưa có bằng chứng skill đã giúp hai tác vụ này; việc skill tồn tại không đồng nghĩa được dùng. Kết quả phát triển được giữ riêng khỏi sáu lần skills-auto chính thức sau freeze.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. Chỉ ba tác vụ mỗi vai trò, một mô hình và một lần chạy cho mỗi ô; không có khoảng tin cậy. Chênh lệch nhỏ không đủ để suy rộng sang tác vụ khác.
2. WSL tối giản chỉ có alias `python`, không có `python3` hay pandas. PATH giống nhau cho mọi điều kiện nhưng mô hình chọn lệnh khác nhau; lỗi môi trường và vòng lặp làm điểm/token data khó diễn giải như năng lực suy luận thuần túy.
3. Giới hạn 2.048 token mỗi lời gọi và 60 bước giúp kiểm soát chi phí nhưng có thể làm tác tử kết thúc thiếu output hoặc dừng giữa quá trình. Không coi lần có GraphRecursionError là tác vụ giải thành công.
4. Skill ngắn, còn thiếu nhiều quy ước; skill xử lý FileNotFoundError học sai trọng tâm. Kết quả đo chất lượng bộ skill tự sinh này, không đại diện mọi cách viết skill.
5. Ba tác vụ độc lập chạy đồng thời; tải API có thể ảnh hưởng thời gian. Token có cộng nội bộ subagent nhưng trace chỉ có luồng chính; không thể kiểm toán từng thao tác bên trong subagent.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Thứ tự và lệnh tái lập: xem `report/REPRODUCE.md`. Các batch chạy cùng tham số qua `run_task`; helper trong `.venv/` điều phối phase và nạp lại key, không được đưa vào bài nộp. `report/reproduce.py` cung cấp giao diện tái lập cùng cấu hình.
- Không làm thử thách mở rộng; hoàn thiện các mục bắt buộc 1–6 của rubric.
- `.env` và `.venv/` được bỏ qua bởi Git. API key không được kế thừa vào shell sandbox. Lần khởi động lỗi 402 được lưu riêng, không dùng trong bảng so sánh. Mô hình thật có thể được provider cập nhật dù giữ cùng ID và temperature.

### Tài liệu tham khảo

1. [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): phân việc theo vai trò và chi phí token của đa tác tử.
2. [SkillsBench](https://arxiv.org/abs/2602.12670): phân biệt skill biên soạn với skill tự sinh; lợi ích trung bình của skill tự sinh không được bảo đảm.
3. [SkillEvolBench](https://skillevolbench.github.io/): lợi ích cục bộ và khả năng chuyển giao sang tác vụ đóng băng là hai việc khác nhau.
