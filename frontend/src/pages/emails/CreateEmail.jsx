import "./Emails.css";

import { useState, useRef, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";
import RichTextEditor from "../../components/RichTextEditor";

export default function CreateEmail() {

  const [searchParams] = useSearchParams();

  const templateId = searchParams.get("template");

  const [form, setForm] = useState({
    purpose: "",
    description: "",
    tone: "Professional",
    language: "English",
    action: "generate",
  });

  const [editor, setEditor] = useState({
    subject: "",
    body: "",
  });

  const [originalBody, setOriginalBody] = useState("");

  const [loading, setLoading] = useState(false);

  const [senderAccounts, setSenderAccounts] = useState([]);

  const [senderAccountId, setSenderAccountId] = useState("");

  const [showPreview, setShowPreview] = useState(false);

  const editorRef = useRef(null);

  useEffect(() => {

    async function loadTemplate(){

      if(!templateId) return;

      try{

        const res = await api.get(`/email/${templateId}`);

        console.log("TEMPLATE RESPONSE:", res.data);

        const email = res.data.email || res.data.data || res.data;

        setEditor({
          subject: email.subject || "",
          body: email.body || email.body_html || "",
        });

        setShowPreview(true);

      }catch(err){

        console.error("Template load error", err);

      }

    }


    loadTemplate();


    async function loadSenderAccounts(){

      try{

        const res = await api.get("/sender-accounts/");

        setSenderAccounts(res.data);

        if(res.data.length){
          setSenderAccountId(res.data[0].id);
        }

      }catch(err){
        console.error(err);
      }

    }

    loadSenderAccounts();

  }, []);


  function handleFormChange(e) {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  }

  function handleEditorChange(field, value) {
    setEditor((prev) => ({
      ...prev,
      [field]: value,
    }));
  }

  async function generateEmail() {
    try {
      setLoading(true);

      const res = await api.post("/email/generate", form);

      const htmlBody = res.data.body
        .split("\n")
        .filter(Boolean)
        .map((line) => `<p>${line}</p>`)
        .join("");

      setEditor({
        subject: res.data.subject,
        body: htmlBody,
      });

      setTimeout(() => {
        if (editorRef.current) {
          editorRef.current.commands.setContent(htmlBody);
        }
      }, 100);

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function saveTemplate() {

    const name = window.prompt("Template name:");

    if (!name) return;

    try {

      await api.post("/templates/", {
        name,
        purpose: form.purpose,
        description: form.description,
        tone: form.tone,
        language: form.language,
        subject: editor.subject,
        body: editor.body,
      });

      alert("✅ Template saved");

    } catch (err) {

      console.error(err);
      alert("❌ Failed to save template");

    }
  }


  async function sendTestEmail() {

    const to_email = window.prompt("Send test email to:");

    if (!to_email) return;


    try {

      const formData = new FormData();

      formData.append("to_email", to_email);
      formData.append("sender_account_id", senderAccountId);
      formData.append("subject", editor.subject);
      formData.append("body", originalBody || editor.body);


      await api.post(
        "/email/send",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );


      alert("✅ Test email sent");

    } catch (err) {

      console.error(err);
      alert("❌ Failed to send email");

    }
  }


  async function runAction(action) {
    if (!editor.subject && !editor.body) return;

    try {
      setLoading(true);

      const res = await api.post("/email/edit", {
        subject: editor.subject,
        body: editor.body,
        action,
      });

      const htmlBody = res.data.body
        .split("\n")
        .map((line) => `<p>${line}</p>`)
        .join("");

      setEditor({
        subject: res.data.subject,
        body: htmlBody,
      });

      setTimeout(() => {
        if (editorRef.current) {
          editorRef.current.commands.setContent(htmlBody);
        }
      }, 100);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="ai-studio">

      <h1 className="ai-title">
        ✨ AI Email Studio
      </h1>

      <div className="ai-grid">
              {/* ================= LEFT PANEL ================= */}

        <div className="ai-card">

          <h2>Prompt</h2>

          <label className="ai-label">
            Purpose
          </label>

          <input
            className="ai-input"
            name="purpose"
            placeholder="e.g. Welcome Email"
            value={form.purpose}
            onChange={handleFormChange}
          />

          <label className="ai-label">
            Description
          </label>

          <textarea
            className="ai-textarea"
            rows={10}
            name="description"
            placeholder="Describe what you want the AI to write..."
            value={form.description}
            onChange={handleFormChange}
          />

          <label className="ai-label">
            Tone
          </label>

          <select
            className="ai-select"
            name="tone"
            value={form.tone}
            onChange={handleFormChange}
          >
            <option>Professional</option>
            <option>Friendly</option>
            <option>Casual</option>
            <option>Persuasive</option>
          </select>

          <label className="ai-label">
            Language
          </label>

          <select
            className="ai-select"
            name="language"
            value={form.language}
            onChange={handleFormChange}
          >
            <option>English</option>
            <option>Arabic</option>
            <option>French</option>
            <option>Spanish</option>
          </select>

          <div className="ai-generate">

            <Button
              onClick={generateEmail}
              disabled={loading}
            >
              {loading ? "Generating..." : "✨ Generate Email"}
            </Button>

          </div>

        </div>

        {/* ================= RIGHT PANEL ================= */}

        <div className="ai-card">

          <h2>AI Editor</h2>

          <label className="ai-label">
            Subject
          </label>

          <input
            className="ai-input"
            value={editor.subject}
            onChange={(e) =>
              handleEditorChange("subject", e.target.value)
            }
          />

          <label className="ai-label">
            Email Body
          </label>

          <RichTextEditor
  ref={editorRef}
  content={editor.body}
  onChange={(value) => handleEditorChange("body", value)}
/>
                    <div className="ai-toolbar">

            <Button
              onClick={() => runAction("improve")}
              disabled={loading}
            >
              ✨ Improve
            </Button>

            <Button
              onClick={() => runAction("rewrite")}
              disabled={loading}
            >
              🔄 Rewrite
            </Button>

            <Button
              onClick={() => runAction("shorten")}
              disabled={loading}
            >
              ✂️ Shorten
            </Button>

            <Button
              onClick={() => runAction("lengthen")}
              disabled={loading}
            >
              📄 Lengthen
            </Button>

            <Button
              onClick={() => runAction("professional")}
              disabled={loading}
            >
              💼 Professional
            </Button>

            <Button
              onClick={() => runAction("friendly")}
              disabled={loading}
            >
              😊 Friendly
            </Button>

          </div>


          <div className="preview-toggle">

            <Button
              onClick={() => setShowPreview(!showPreview)}
            >
              📧 {showPreview ? "Hide Preview" : "Show Preview"}
            </Button>

          </div>


          {showPreview && (
            <div className="ai-preview">

              <h3>
                📧 Live Preview
              </h3>


              <div className="ai-preview-card">

                <div className="preview-subject">

                  <strong>
                    Subject
                  </strong>

                  <p>
                    {editor.subject || "Your subject will appear here..."}
                  </p>

                </div>


                <hr />


                <div
                  className="preview-body"
                  dangerouslySetInnerHTML={{
                    __html:
                      editor.body ||
                      "<p>Your email preview will appear here...</p>"
                  }}
                />

              </div>

            </div>
          )}


          <div className="ai-actions">

            <Button
              onClick={() =>
                navigator.clipboard.writeText(
                  `${editor.subject}\n\n${editor.body}`
                )
              }
              disabled={!editor.subject && !editor.body}
            >
              📋 Copy Email
            </Button>

            <Button
              onClick={saveTemplate}
              disabled={!editor.subject && !editor.body}
            >
              💾 Save Template
            </Button>

            <Button
              onClick={sendTestEmail}
              disabled={!editor.subject && !editor.body}
            >
              📤 Send Test
            </Button>

          </div>

        </div>
              </div>

    </div>
  );
}