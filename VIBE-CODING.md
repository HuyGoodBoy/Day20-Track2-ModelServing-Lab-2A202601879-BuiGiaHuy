# Vibe Coding Day 20 — BMAD Method

> Đọc 5–10 phút **trước khi bắt đầu lab**. Áp dụng cho mọi project, không chỉ Lab 20.

Day 19 giới thiệu **vibe-coding** dạng general: bạn để LLM viết phần lớn code, bạn làm architect + reviewer. Tốt cho greenfield boilerplate.

Day 20 nâng cấp lên **BMAD Method** — vẫn là vibe-coding, nhưng có *cấu trúc persona* để xử lý task phức tạp hơn (không chỉ "viết code", mà là "ra quyết định trong nhiều phase").

---

## BMAD là gì?

**BMAD** = Breakthrough Method for Agile AI-Driven Development. Open-source framework giúp bạn cộng tác với AI agents qua các *persona chuyên biệt*, không phải một AI generalist trả lời mọi thứ.

- GitHub: [github.com/bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- Docs: [docs.bmad-method.org](https://docs.bmad-method.org/)
- Cài: `npx bmad-method install` trong project (sinh ra agent files cho Claude Code / Cursor / Codex CLI)

**Insight cốt lõi của BMAD:** prompt LLM theo *persona* (PM, Architect, Developer, QA, Ops, ...) ép LLM nhìn bài toán từ một góc cụ thể. Mỗi persona surface một loại concern khác nhau. Một LLM "generic" có xu hướng trả lời chung chung; một LLM được prompt "Acting as Architect, ..." sẽ tập trung vào structural decisions.

---

## Vibe-coding (Day 19) vs BMAD (Day 20)

| | Vibe-coding (general) | BMAD |
|---|---|---|
| **Lens** | Delegate vs think-hard | Persona-driven phases |
| **Flow** | Spec → prompt → review → run → commit | Analysis → Planning → Architecture → Implementation → QA |
| **Scope** | Một function, một feature | Một project / một phase / một quyết định lớn |
| **Tốt cho** | Boilerplate, refactor nhỏ, "nhanh viết utility" | Decision-heavy task: tối ưu hệ thống, design new service, debug deep |
| **Cost** | Thấp — chỉ cần prompt template | Cao hơn — cần kỷ luật chuyển persona, viết spec rõ |

**Quy tắc cũ vẫn đúng:** nếu bug sẽ là *silent regression* (chạy nhưng kém hơn, không lỗi rõ) thay vì *loud failure* (exception, test fail), đó là **think-hard zone**. BMAD thêm: cũng là **QA-persona zone**.

---

## 5 personas chính

BMAD ship với 12+ persona, nhưng 5 cái dưới đủ cho 90% workflow hằng ngày:

### 1. **PM / Spec**
> *"What's the goal? What's the SLO? What's the success criterion?"*

Trả lời câu hỏi *bạn đang giải quyết vấn đề gì*, không phải *làm thế nào*. Output là một spec có thể đo được.

```
Acting as PM persona:
Restate my goal as a measurable spec.
Constraints I care about: <list>.
Non-goals (things I'm explicitly NOT optimizing for): <list>.
Define success in 1 sentence with a number.
```

### 2. **Architect**
> *"What's the system shape? What are the major decisions? What did we rule out?"*

Architect persona ra quyết định macro: chọn library, chọn pattern, chọn boundary. Không viết code — viết tradeoff list.

```
Acting as Architect persona:
Given <constraints>, list 3 viable approaches.
For each: 1-line summary, pros, cons, when it breaks.
Recommend one with justification ≤ 50 words.
Name the rejected alternative + reason.
```

### 3. **Developer**
> *"Write the code that implements the architect's decision."*

Đây là zone delegate boilerplate cũ. Developer persona viết code khớp spec từ PM + design từ Architect.

```
Acting as Developer persona:
Implement <spec> following <architect's decision>.
No new abstractions beyond what the spec requires.
Include the minimum tests needed to verify the spec.
```

### 4. **QA / Verify**
> *"Did the code actually meet the spec? What edge cases break it?"*

QA persona là chỗ BMAD đánh bại "pure vibe-coding". Sau khi Developer viết code, QA prompt ép LLM tìm bugs, edge cases, regressions.

```
Acting as QA persona:
Review the diff above against <spec>.
List 5 things that could fail silently — order by likelihood.
For each, write the test that would catch it.
```

### 5. **Ops / Reflect**
> *"How does this run in production? What's the cost? What's portable?"*

Ops persona xem xét deployment, monitoring, cost, portability. Hữu ích khi commit code cho team / class chứ không phải chỉ máy mình.

```
Acting as Ops persona:
This change works on my machine. List the things that
would prevent it working on a teammate's machine, in CI,
or on a production server. Rank by severity.
```

---

## Workflow loop

```
   1. PM persona       → measurable spec      (you write)
   2. Architect persona → tradeoff + decision  (you decide)
   3. Developer persona → code matching above  (LLM writes, you review)
   4. QA persona        → find silent failures (LLM lists, you test)
   5. Ops persona       → portability, cost    (you reflect)
```

**Đừng skip step 1 và 4.** Skip 1 = giải quyết sai bài toán. Skip 4 = ship silent regression. Steps 2 và 5 là *judgment calls* — bạn vẫn là người quyết.

---

## BMAD nhanh vs BMAD đầy đủ

**BMAD nhanh** (cách bạn dùng cho lab này):
- Không cần `npx bmad-method install`
- Mở Claude Code / Cursor / Codex CLI
- Prefix mỗi prompt bằng `Acting as <persona>:` khi muốn switch hat
- Đó là tất cả

**BMAD đầy đủ** (nếu bạn ấn tượng và muốn dùng cho project lớn):
- `npx bmad-method install` trong repo → sinh agent files
- Mỗi persona có context dài + tool set riêng
- IDE-integrated (auto-detect khi switch persona)
- Phù hợp cho project ≥ 1 sprint

Cả hai đều OK. Bắt đầu với "BMAD nhanh", upgrade sau nếu cần.

---

## 3 anti-pattern cần tránh

1. **Skip PM persona.** Prompt: *"Optimize my server."* — LLM không biết bạn cần TTFT < 500ms, throughput tối đa, hay cost tối thiểu. Sẽ trả lời chung chung. PM persona là 1 phút bạn bỏ ra để tiết kiệm 30 phút prompt-debate sau.

2. **Skip QA persona.** *"LLM nói flag này nhanh hơn, ship thôi."* — Đây là chỗ silent regression sinh ra. QA persona ép bạn (và LLM) tìm cái có thể sai *sau khi* code đã chạy được.

3. **BMAD-as-bureaucracy.** Sửa typo không cần PM/Architect/QA. Một command `sed` không cần workflow loop. BMAD dành cho task phức tạp; task đơn giản — vibe-code thẳng.

---

## Tài liệu thêm

- BMAD docs: [docs.bmad-method.org](https://docs.bmad-method.org/)
- Bài giới thiệu: [Reenbit — The BMAD Method: how structured AI agents turn vibe-coding into production-ready software](https://reenbit.com/the-bmad-method-how-structured-ai-agents-turn-vibe-coding-into-production-ready-software/)
- Bài Medium: [Vishal Mysore — A Simple Guide to BMAD-METHOD](https://medium.com/@visrow/what-is-bmad-method-a-simple-guide-to-the-future-of-ai-driven-development-412274f91419)

---

## Tóm tắt

> Day 19 dạy bạn **prompt LLM cho boilerplate**.
> Day 20 dạy bạn **prompt LLM cho quyết định**.
> Cùng là vibe-coding, chỉ khác structure.
