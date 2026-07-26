import "./Emails.css";

import { useState } from "react";
import api from "../../api/client";
import Button from "../../components/Button";

export default function CreateEmail() {
  const [form, setForm] = useState({
    purpose: "",
    description: "",
    tone: "Professional",
    language: "English",
    action: "generate",
  });

  const [result, setResult] = useState(null);

  const [editor, setEditor] = useState({
    subject: "",
    body: "",
  });

  const [loading, setLoading] = useState(false);

  function change(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  }

  function submit() {
    setLoading(true);

    api
      .post("/email/generate", form)
      .then((res) => {
        setResult(res.data);

        setEditor({
          subject: res.data.subject,
          body: res.data.body,
        });
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  function runAction(action) {
    if (!result) return;

    setLoading(true);

    api
      .post("/email/edit", {
        subject: editor.subject,
        body: editor.body,
        action,
      })
      .then((res) => {
        setResult(res.data);

        setEditor({
          subject: res.data.subject,
          body: res.data.body,
        });
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  return (
    <div className="ai-studio">
      <h1 className="ai-title">
        ✨ AI Email Studio
      </h1>

      {/* Prompt Card */}

      <div className="ai-card">
        <h2>Prompt</h2>

        <input
          name="purpose"
          placeholder="Purpose"
          value={form.purpose}
          onChange={change}
          className="ai-input"
        />

        <textarea
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={change}
          rows={6}
          className="ai-input"
        />

        <div className="ai-toolbar">
          <select className="ai-select"
            name="tone"
            value={form.tone}
            onChange={change}
          >
            <option>Professional</option>
            <option>Friendly</option>
            <option>Casual</option>
            <option>Persuasive</option>
          </select>

          <select className="ai-select"
            name="language"
            value={form.language}
            onChange={change}
          >
            <option>English</option>
            <option>Arabic</option>
            <option>French</option>
            <option>Spanish</option>
          </select>

          <select className="ai-select"
            name="action"
            value={form.action}
            onChange={change}
          >
            <option value="generate">Generate</option>
            <option value="improve">Improve</option>
            <option value="rewrite">Rewrite</option>
            <option value="shorten">Shorten</option>
            <option value="lengthen">Lengthen</option>
            <option value="professional">Professional</option>
            <option value="friendly">Friendly</option>
          </select>
        </div>

        <Button onClick={submit}>
          {loading ? "Generating..." : "✨ Generate Email"}
        </Button>
      </div>

      {/* AI Editor */}

      {result && (
        <div className="ai-card">
          <h2>AI Editor</h2>

          <h3>Subject</h3>

          <input
            value={editor.subject}
            onChange={(e) =>
              setEditor({
                ...editor,
                subject: e.target.value,
              })
            }
            style={{
              width: "100%",
              marginBottom: 20,
              padding: 12,
            }}
          />

          <h3>Body</h3>

          <textarea
            rows={16}
            value={editor.body}
            onChange={(e) =>
              setEditor({
                ...editor,
                body: e.target.value,
              })
            }
            style={{
              width: "100%",
              padding: 12,
              marginBottom: 24,
            }}
          />

          <div className="ai-toolbar">
            <Button onClick={() => runAction("improve")}>
              ✨ Improve
            </Button>

            <Button onClick={() => runAction("rewrite")}>
              🔄 Rewrite
            </Button>

            <Button onClick={() => runAction("shorten")}>
              ✂️ Shorten
            </Button>

            <Button onClick={() => runAction("lengthen")}>
              📄 Lengthen
            </Button>

            <Button onClick={() => runAction("professional")}>
              💼 Professional
            </Button>

            <Button onClick={() => runAction("friendly")}>
              😊 Friendly
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}