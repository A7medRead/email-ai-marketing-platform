import { useCallback, useEffect, useState } from "react";
import { Tag, Pencil, Trash2, Plus, X } from "lucide-react";
import api from "../../../shared/api/client";
import Button from "../../../shared/ui/Button";
import Card from "../../../shared/ui/Card";
import Loading from "../../../shared/ui/Loading";
import EmptyState from "../../../shared/ui/EmptyState";
import "./Offers.css";

const blank = { name: "", title: "", description: "", discount: "", coupon_code: "", starts_at: "", expires_at: "", cta_label: "", cta_url: "" };
const fields = [
  ["name", "Internal name", true], ["title", "Offer headline", true],
  ["discount", "Discount (e.g. 20% off)", false], ["coupon_code", "Coupon code", false],
  ["starts_at", "Starts at", false, "datetime-local"], ["expires_at", "Expires at", false, "datetime-local"],
  ["cta_label", "Button text", false], ["cta_url", "Destination URL", false, "url"],
];

export default function Offers() {
  const [offers, setOffers] = useState([]);
  const [form, setForm] = useState(blank);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try { const result = await api.get("/offers/"); setOffers(result.data); }
    catch { setError("Could not load offers. Please try again."); }
    finally { setLoading(false); }
  }, []);

  // eslint-disable-next-line react-hooks/set-state-in-effect -- Load starts an asynchronous request; state updates happen after it resolves.
  useEffect(() => { load(); }, [load]);

  function startEdit(offer) {
    setEditingId(offer.id);
    setForm(Object.fromEntries(Object.keys(blank).map((key) => [key, key.endsWith("_at") && offer[key] ? offer[key].slice(0, 16) : (offer[key] ?? "")] )));
    setError("");
    document.querySelector(".offers-form-card")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function cancelEdit() { setEditingId(null); setForm(blank); setError(""); }

  async function submit(event) {
    event.preventDefault(); setError(""); setBusy(true);
    const payload = { ...form, starts_at: form.starts_at || null, expires_at: form.expires_at || null, cta_url: form.cta_url || null };
    try {
      if (editingId) await api.put(`/offers/${editingId}`, payload);
      else await api.post("/offers/", payload);
      cancelEdit(); await load();
    } catch (err) { setError(err.response?.data?.detail || "Could not save this offer."); }
    finally { setBusy(false); }
  }

  async function remove(offer) {
    if (!window.confirm(`Delete “${offer.name}”? Existing campaigns keep their sent content.`)) return;
    try { await api.delete(`/offers/${offer.id}`); await load(); }
    catch { setError("Could not delete this offer."); }
  }

  if (loading) return <Loading />;
  return <div className="page offers-page">
    <header className="offers-header page-header">
      <div><p className="offers-eyebrow"><Tag size={15} /> PROMOTIONS</p><h1>Offers</h1><p className="subtitle">Create reusable promotions, then add them to a campaign email.</p></div>
    </header>

    <Card className="offers-form-card" id="offer-form">
      <div className="offers-form-heading"><div><h2>{editingId ? "Edit offer" : "Create an offer"}</h2><p>Offer details will be added to the campaign email when selected.</p></div>{editingId && <Button variant="secondary" onClick={cancelEdit}><X size={16} /> Cancel</Button>}</div>
      <form className="offers-form" onSubmit={submit}>
        {fields.map(([key, label, required, type]) => <label className="offers-field" key={key}>{label}<input required={required} type={type || "text"} value={form[key]} onChange={(e) => setForm((previous) => ({ ...previous, [key]: e.target.value }))} /></label>)}
        <label className="offers-field offers-description">Description<textarea required rows="3" value={form.description} onChange={(e) => setForm((previous) => ({ ...previous, description: e.target.value }))} /></label>
        {error && <p className="offers-error" role="alert">{Array.isArray(error) ? error.map((item) => item.msg).join(" ") : error}</p>}
        <div className="offers-submit"><Button type="submit" disabled={busy}><Plus size={17} /> {busy ? "Saving…" : editingId ? "Save changes" : "Create offer"}</Button></div>
      </form>
    </Card>

    <section className="offers-list-section"><div className="offers-list-heading"><h2>Your offers</h2><span>{offers.length} total</span></div>
      {offers.length === 0 ? <EmptyState title="No offers yet" message="Create an offer above to make it available when building campaigns." /> : <div className="offers-grid">{offers.map((offer) => <Card className="offers-card" key={offer.id}>
        <div className="offers-card-top"><span className="offers-tag"><Tag size={14} /> {offer.discount || "Promotion"}</span><div className="offers-card-actions"><button aria-label={`Edit ${offer.name}`} onClick={() => startEdit(offer)}><Pencil size={17} /></button><button aria-label={`Delete ${offer.name}`} onClick={() => remove(offer)}><Trash2 size={17} /></button></div></div>
        <h3>{offer.title}</h3><p>{offer.description}</p>
        {offer.coupon_code && <div className="offers-code"><span>Coupon code</span><strong>{offer.coupon_code}</strong></div>}
        <div className="offers-dates">{offer.starts_at && <span>Starts {new Date(offer.starts_at).toLocaleDateString()}</span>}{offer.expires_at && <span>Ends {new Date(offer.expires_at).toLocaleDateString()}</span>}</div>
        <small className="offers-internal-name">{offer.name}</small>
      </Card>)}</div>}
    </section>
  </div>;
}
