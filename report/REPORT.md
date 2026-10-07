# Báo cáo Lab: Self evolving Agentic

**Trạng thái: hoàn thiện mã nguồn và báo cáo; thí nghiệm chính thức chưa đủ vì API bị chặn.** Sau lỗi 402 lặp lại dù chạy tuần tự và chờ Retry-After, người thực hiện chọn chốt báo cáo với phần API bị chặn. Không điền giả kết quả còn thiếu.


## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| VoCongDanh | 2A202602739 | Hoàn thiện harness, tổ chức thí nghiệm và phân tích báo cáo. |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenRouter, `openai/gpt-4o-mini`, nhiệt độ 0, `recursion_limit=60`. Giới hạn đầu ra mỗi lời gọi là 2.048 token, timeout API 60 giây, tối đa 1 lần thử lại; giữ cùng cấu hình cho các điều kiện hợp lệ.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, Python `3.12.14`; chạy trực tiếp trong Linux qua WSL `docker-desktop` trên máy Windows, không chạy container Docker.
- Bộ bằng chứng hiện có: 9 bản ghi ở baseline/subagents (7 lượt kết thúc không lỗi API, 2 lượt API bị chặn có điểm một phần); 3 lượt skills-auto phát triển lưu riêng; 3 lần curator. Không đủ 18 ô chính thức. Hai lượt GraphRecursionError (baseline data-learn và skills-auto-dev data-learn) là thất bại có giới hạn, không giải xong tác vụ. Ngân sách tiền không được cung cấp.
- Commit giả thuyết: `a11fb14`; tag `freeze`: `cf755c3e78893e9e995704cba16b7325cf9394c0`. H1–H3 được ghi trước freeze; eval chỉ bắt đầu sau đó.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)


- H1 (subagents so với baseline): dự đoán điểm trung bình eval của subagents cao hơn baseline, nhưng token trung bình cũng cao hơn. Baseline code-learn chỉ đạt 4/10: tác tử sửa test có sẵn và bỏ sót hai yêu cầu docstring. Explorer/reviewer có thể giúp đọc và đối chiếu đặc tả đầy đủ hơn. Anthropic mô tả lợi ích của phân việc và chi phí token lớn hơn trong hệ thống nghiên cứu đa tác tử; kết quả đó thuộc bối cảnh khác, không dùng mức tăng của họ làm dự báo định lượng cho lab này.
- H2 (skills-auto so với baseline): dự đoán skills-auto có điểm eval cao nhất trong ba điều kiện nhờ nhớ quy ước chung từ phản hồi tác vụ học, nhưng vẫn có thể bỏ sót quy ước mới. Ba check quy ước ở baseline code-learn đều thất bại, tạo phản hồi rõ cho curator. Đây là dự đoán cần kiểm chứng: SkillsBench ghi nhận skill tự sinh không có lợi trung bình, nên không mặc định việc thêm skill sẽ tăng điểm.
- H3 (tác vụ học so với tác vụ đánh giá): dự đoán điểm trung bình skills-auto trên learn cao hơn eval vì skill được rút từ learn, còn eval đổi dữ liệu và thêm quy ước. SkillEvolBench cho thấy lợi ích ở tác vụ đã gặp có thể không chuyển ổn định sang tình huống mới; cần tách learn/eval và so sánh hai lần chạy learn để tránh nhầm nhiễu với quá khớp.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tour liệt kê 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ `execute` chạy lệnh shell; `task` giao việc cho subagent.
2. `general-purpose` dùng để nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và làm việc nhiều bước; có cùng công cụ như tác tử chính. Mỗi lần gọi mặc định là một phiên mới, chỉ thấy prompt được giao và trả lại một báo cáo cuối. Vì vậy tác tử chính phải truyền đủ yêu cầu và đường dẫn.
3. Tour xác nhận system prompt mặc định là chuỗi rỗng (`''`), nhưng mô tả tool vẫn hướng dẫn hành vi. Trong `task`: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Trong `execute`: “Quote paths containing spaces (e.g. cd \"/path/with spaces\").”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)


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

Bảng dưới do `lab.compare` sinh trực tiếp từ các bản ghi hiện có. Ô `-` là chưa chạy; không có cột skills-auto vì chưa có lượt chính thức sau freeze. Điểm code-eval/data-eval baseline là điểm tệp một phần lúc API lỗi; không dùng để suy luận chất lượng mô hình. Hàng trung bình của công cụ chưa loại lượt API lỗi nên chỉ là thống kê bản ghi.

| Task | baseline | subagents |
|---|---|---|
| code-learn | 4/10 | 4/10 |
| data-learn | 0/8 | 3/8 |
| logs-learn | 1/9 | 0/9 |
| code-eval | 1/11 | - |
| data-eval | 0/9 | - |
| logs-eval | 2/10 | - |
| **Mean score - learning tasks** | 0.17 | 0.26 |
| **Mean score - evaluation tasks** | 0.10 | - |
| **Mean tokens per run** | 124,237 | 113,373 |
| **Runs that read a skill** | 0/6 | 0/3 |

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      2/18         1/12         108,429      0/3
baseline      learn     5/18         0/9          140,044      0/3
subagents     learn     7/18         0/9          113,373      0/3
```

Kết quả skills-auto **phát triển trước freeze**, không phải kết quả chính thức:

| Task | Điểm | Token | skills_read | error |
|---|---|---:|---:|---|
| code-learn | 4/10 | 62,233 | 0 | Không |
| data-learn | 0/8 | 320,812 | 0 | GraphRecursionError |
| logs-learn | 1/9 | 22,076 | 0 | Không |

Các lượt có error đang được giữ trong bộ bằng chứng:

- baseline/code-eval: APIStatusError, 1/11, 297,083 token.
- baseline/data-eval: APIStatusError, 0/9, 10,421 token.
- baseline/data-learn: GraphRecursionError, 0/8, 338,755 token.
- skills-auto-dev/data-learn: GraphRecursionError, 0/8; vết có lặp lệnh lỗi.

Các lần 402 trước đó lưu tại results/infra; có bản sao cùng timestamp, không coi chúng là các lượt độc lập. Bản ghi API lỗi không dùng cho taxonomy lỗi tác tử. Không có lượt sửa skill. Ba bản ghi skills-auto trước freeze đã giữ tại skills-auto-dev và bỏ khỏi thư mục chính, nên không trộn lượt phát triển vào kết quả đóng băng.

Còn thiếu 9 lượt: subagents code-eval/data-eval/logs-eval và skills-auto cả 6 tác vụ; baseline code-eval/data-eval cần chạy lại không lỗi API. Danh sách trạng thái từng ô nằm trong report/experiment-status.json.

## 8. Phân tích

1. **Điểm và giả thuyết.** Trên learn, baseline có điểm trung bình 0.1704; subagents có điểm trung bình 0.2583; skills-auto-dev có điểm trung bình 0.1704. Subagents tăng 0,0880 điểm chuẩn hóa so với baseline; code không đổi, data tăng 3 check, logs giảm 1 check. Skills-auto-dev không cải thiện điểm trung bình so với baseline. H1/H2 dự đoán trên eval chưa kiểm chứng được vì thiếu eval subagents/skills-auto; baseline logs-eval đạt 2/10 nhưng chỉ một tác vụ không đại diện cả eval. H3 cũng chưa kiểm chứng được do không có skills-auto eval. Không kết luận có hay không quá khớp từ dữ liệu thiếu.

2. **Kỹ thuật và quy ước.** Baseline learn đạt 5/18 check kỹ thuật và 0/9 quy ước; subagents learn đạt 7/18 và 0/9; skills-auto-dev đạt 5/18 và 0/9. Bộ skill chưa giúp tăng check quy ước trên learn. Không đọc thêm nội dung check eval để bù quy ước vào skill sau freeze; chưa có dữ liệu đo việc chuyển giao sang quy ước mới ở eval. Các số eval trong check_breakdown gồm lượt API bị chặn, không dùng làm so sánh điều kiện.

3. **Cơ chế dùng skill.** Cả ba lượt skills-auto-dev có skills_read=0. Code bắt đầu bằng glob/read_file source, logs bắt đầu đọc app.log; không đọc SKILL.md. Vì vậy không có check nào có bằng chứng được skill giúp đạt. Ví dụ skill không giúp: tests_not_modified vẫn thất bại dù có avoid-modifying-test-files; rule_service_names vẫn thất bại dù skill log hướng dẫn thay gạch ngang bằng gạch dưới. Không thể nói mô hình đọc nhưng bỏ qua skill vì trace cho thấy chưa đọc.

4. **Chi phí.** Chỉ so sánh ba tác vụ learn để tránh lượt API lỗi và dữ liệu thiếu:

| Điều kiện | Token trung bình/lượt | Điểm chuẩn hóa trên 100.000 token |
|---|---:|---:|
| baseline | 140,044 | 0.1217 |
| subagents | 113,373 | 0.2279 |
| skills-auto-dev | 135,040 | 0.1262 |

Subagents có chỉ số điểm/token cao nhất trên learn, nhưng baseline data bị vòng lặp làm tăng token, còn code/logs subagents không gọi subagent. Chưa đủ bằng chứng đa tác tử đáng chi phí trên eval hoặc luôn rẻ hơn. Token không phải chi phí USD; không suy ra giá tiền nếu không có hóa đơn/usage thực.

5. **Rò rỉ và quá khớp.** Curator chỉ dùng baseline learn và trace; eval chưa chạy trước freeze. Validator chặn marker eval và tên/path không hợp lệ. Skill không chứa đáp án hoặc dòng dữ liệu; giữ nguyên sau tag. Skill log học quy ước từ learn, skill FileNotFoundError lại thiếu chẩn đoán nguyên nhân thật, nên chất lượng còn hạn chế. Đóng băng đúng thư viện không thay thế yêu cầu đủ kết quả eval.

6. **Nhiễu.** Đã sao lưu skills-auto-dev trước freeze: code 4/10, data 0/8, logs 1/9, trung bình 0,1704. Chưa có lần learn chính thức sau freeze nên chênh lệch trước/sau là **chưa đo**, không phải 0. Không thể ước lượng nhiễu hoặc khẳng định các chênh lệch nhỏ là ổn định.

## 9. Hạn chế và tính hợp lệ

0. API trả 402 in_flight_budget_exhausted lặp lại; phần lớn eval và toàn bộ skills-auto chính thức chưa có. Vì vậy không đủ dữ liệu kiểm chứng H1–H3, không có bảng so sánh chính thức đủ ba điều kiện. Lượt lỗi API không được tính là lỗi suy luận tác tử.

1. Chỉ ba tác vụ mỗi vai trò, một mô hình và một lần chạy cho mỗi ô; không có khoảng tin cậy. Chênh lệch nhỏ không đủ để suy rộng sang tác vụ khác.
2. WSL tối giản chỉ có alias `python`, không có `python3` hay pandas. PATH giống nhau cho mọi điều kiện nhưng mô hình chọn lệnh khác nhau; lỗi môi trường và vòng lặp làm điểm/token data khó diễn giải như năng lực suy luận thuần túy.
3. Giới hạn 2.048 token mỗi lời gọi và 60 bước giúp kiểm soát chi phí nhưng có thể làm tác tử kết thúc thiếu output hoặc dừng giữa quá trình. Không coi lần có GraphRecursionError là tác vụ giải thành công.
4. Skill ngắn, còn thiếu nhiều quy ước; skill xử lý FileNotFoundError học sai trọng tâm. Kết quả đo chất lượng bộ skill tự sinh này, không đại diện mọi cách viết skill.
5. Các batch learn ban đầu có ba tác vụ độc lập chạy đồng thời. Batch baseline eval gặp 402 `in_flight_budget_exhausted`, nên các lượt tiếp theo chuyển sang tuần tự và chờ Retry-After 120 giây; lượt lỗi được lưu riêng rồi chạy lại. Thời gian khác biệt tải API không thích hợp để kết luận điều kiện nào nhanh hơn. Token có cộng nội bộ subagent nhưng trace chỉ có luồng chính; không thể kiểm toán từng thao tác bên trong subagent.

## 10. Kết luận

Harness, subagent, curator, bộ skill và giả thuyết trước freeze đã hoàn thiện. Trên ba tác vụ learn, subagents đạt trung bình 0,2583, baseline và skills-auto-dev cùng 0,1704. Skill chưa được đọc ở ba lượt phát triển nên chưa có bằng chứng giúp tăng điểm. API bị chặn khiến chưa thể kết luận về eval, chuyển giao hoặc nhiễu trước/sau freeze. Bước tiếp theo là khôi phục khả năng gọi API rồi chạy đủ các lượt còn thiếu với skill đã đóng băng, trước khi kiểm chứng H1–H3.

## Phụ lục

- Thứ tự và lệnh tái lập: xem `report/REPRODUCE.md`. Các batch chạy cùng tham số qua `run_task`; helper trong `.venv/` điều phối phase và nạp lại key, không được đưa vào bài nộp. `report/reproduce.py` cung cấp giao diện tái lập cùng cấu hình.
- Không làm thử thách mở rộng. Các mục thí nghiệm bắt buộc bị thiếu đã liệt kê trong trạng thái nộp.
- `.env` và `.venv/` được bỏ qua bởi Git. API key không được kế thừa vào shell sandbox. Lượt 402 khởi động lưu riêng; hai lượt API lỗi cuối vẫn xuất hiện trong bảng thô và được đánh dấu partial, không dùng để kết luận chất lượng mô hình. Mô hình thật có thể được provider cập nhật dù giữ cùng ID và temperature.

### Tài liệu tham khảo

1. [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): phân việc theo vai trò và chi phí token của đa tác tử.
2. [SkillsBench](https://arxiv.org/abs/2602.12670): phân biệt skill biên soạn với skill tự sinh; lợi ích trung bình của skill tự sinh không được bảo đảm.
3. [SkillEvolBench](https://skillevolbench.github.io/): lợi ích cục bộ và khả năng chuyển giao sang tác vụ đóng băng là hai việc khác nhau.
4. [OpenRouter — Credit limits](https://github.com/OpenRouterTeam/docs/blob/main/api_reference/limits.mdx): in-flight budget tính cả request vừa hoàn tất trong thời gian quyết toán; lỗi này có thể tiếp diễn dù không còn request đang chạy. Đã thử chờ Retry-After và chạy tuần tự nhưng vẫn bị chặn.

### Trạng thái nộp

Mã nguồn và báo cáo có thể nộp hiện trạng; phần thí nghiệm bị chặn chưa đáp ứng đủ rubric 2.1, 3.2, 4.3, 5.1 và phân tích nhiễu của 6.2. Không khẳng định bài đã hoàn thành toàn bộ hay đạt đủ điểm.

Kiểm tra cuối ngày 07/10/2026: `32 passed in 15.16s` (report/pytest.txt). `verify_freeze.py` báo `checked 0 runs of skill conditions: OK` (report/freeze-check.txt): tag, giả thuyết và thư viện skill không đổi đạt kiểm tra cấu trúc, nhưng chưa có lượt skills-auto chính thức để đối chiếu hash/timestamp; không coi đây là hoàn thành rubric 4.3. Kiểm tra tính toàn vẹn xác nhận tệp được cung cấp và các prompt/hàm bắt buộc giữ nguyên; key cấu hình không có trong tệp nộp.
