import { AskPanel } from "@/components/ask-panel";

export default function HomePage() {
  return (
    <main className="shell">
      <header className="masthead">
        <div>
          <p className="eyebrow">Amanah RAG · lite</p>
          <h1>Answers you can audit.</h1>
          <p className="lede">
            Ask in Arabic or English. Every answer is grounded in the uploaded corpus and
            returns the passages it used.
          </p>
        </div>
        <a className="repo-link" href="https://github.com/OmerAbdel-aziz/AmanahRAG">
          GitHub
        </a>
      </header>

      <AskPanel />

      <footer className="footer">
        <span>PII is redacted before any model call.</span>
        <span>Retrieval: {process.env.MILVUS_COLLECTION ?? "amanah_chunks"}</span>
      </footer>
    </main>
  );
}
