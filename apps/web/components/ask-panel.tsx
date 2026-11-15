"use client";

import { useState } from "react";
import { askQuestion, type ChatResponse } from "@/lib/api";

const SUGGESTIONS = [
  {
    en: "What is the retention period for uploaded documents?",
    ar: "ما هي مدة الاحتفاظ بالمستندات المرفوعة؟",
  },
  {
    en: "Who approves a refund above 5,000?",
    ar: "من يعتمد استرداد المبلغ الذي يتجاوز ٥٠٠٠؟",
  },
];

export function AskPanel() {
  const [language, setLanguage] = useState<"en" | "ar">("en");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(text: string) {
    const trimmed = text.trim();
    if (!trimmed || pending) return;

    setPending(true);
    setError(null);
    setAnswer(null);
    try {
      setAnswer(await askQuestion(trimmed, language));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Request failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="panel" dir={language === "ar" ? "rtl" : "ltr"}>
      <div className="panel-head">
        <div className="segmented" role="group" aria-label="Answer language">
          {(["en", "ar"] as const).map((code) => (
            <button
              key={code}
              type="button"
              aria-pressed={language === code}
              onClick={() => setLanguage(code)}
            >
              {code === "en" ? "English" : "العربية"}
            </button>
          ))}
        </div>
        <span className="hint">{pending ? "Retrieving…" : "Grounded answers only"}</span>
      </div>

      <form
        className="ask"
        onSubmit={(event) => {
          event.preventDefault();
          void submit(question);
        }}
      >
        <label className="sr-only" htmlFor="question">
          Question
        </label>
        <textarea
          id="question"
          rows={3}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={
            language === "ar"
              ? "اكتب سؤالك هنا…"
              : "Ask about a policy, procedure or document…"
          }
        />
        <div className="ask-actions">
          <div className="suggestions">
            {SUGGESTIONS.map((item) => (
              <button
                key={item.en}
                type="button"
                className="chip"
                onClick={() => {
                  setQuestion(item[language]);
                  void submit(item[language]);
                }}
              >
                {item[language]}
              </button>
            ))}
          </div>
          <button className="primary" type="submit" disabled={pending || !question.trim()}>
            {pending ? "Asking…" : "Ask"}
          </button>
        </div>
      </form>

      {error ? (
        <p className="alert" role="alert">
          {error}
        </p>
      ) : null}

      {answer ? (
        <article className="answer">
          <p className="answer-meta">
            {answer.language.toUpperCase()} · {answer.model} · {answer.latency_ms} ms
          </p>
          <p className="answer-body">{answer.answer}</p>
          {answer.citations.length > 0 ? (
            <ol className="citations">
              {answer.citations.map((citation) => (
                <li key={`${citation.document_id}-${citation.chunk_id}`}>
                  <span className="citation-title">{citation.title}</span>
                  <span className="citation-score">
                    score {citation.score.toFixed(3)}
                  </span>
                  <p>{citation.snippet}</p>
                </li>
              ))}
            </ol>
          ) : (
            <p className="hint">No supporting passages were retrieved.</p>
          )}
          <p className="trace">trace {answer.trace_id}</p>
        </article>
      ) : null}
    </section>
  );
}
