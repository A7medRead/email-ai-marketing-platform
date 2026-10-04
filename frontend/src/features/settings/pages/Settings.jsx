import { useCallback, useEffect, useState } from "react";
import { Check, Languages, Mail, MessageSquareText, SlidersHorizontal } from "lucide-react";
import api from "../../../shared/api/client";
import "./Settings.css";

const initialPreferences = {
    preferred_language: "English",
    preferred_tone: "Professional",
    preferred_length: "Medium",
};

export default function Settings() {
    const [preferences, setPreferences] = useState(initialPreferences);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState("");

    const loadPreferences = useCallback(async () => {
        try {
            const { data } = await api.get("/users/me");
            setPreferences({
                preferred_language: data.preferred_language || initialPreferences.preferred_language,
                preferred_tone: data.preferred_tone || initialPreferences.preferred_tone,
                preferred_length: data.preferred_length || initialPreferences.preferred_length,
            });
        } catch {
            setMessage("Could not load your preferences. Please try again.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect -- loadPreferences updates state after its async API request.
        loadPreferences();
    }, [loadPreferences]);

    async function savePreferences(event) {
        event.preventDefault();
        setSaving(true);
        setMessage("");
        try {
            await api.put("/users/me", preferences);
            setMessage("Your preferences have been saved.");
        } catch {
            setMessage("Could not save your preferences. Please try again.");
        } finally {
            setSaving(false);
        }
    }

    if (loading) return <div className="settings-page" role="status">Loading settings…</div>;

    return (
        <section className="settings-page">
            <header className="settings-heading">
                <div className="settings-heading-icon"><SlidersHorizontal size={22} /></div>
                <div>
                    <p className="settings-eyebrow">YOUR WORKSPACE</p>
                    <h1>Settings</h1>
                    <p>Choose the defaults used when AI creates emails for you.</p>
                </div>
            </header>

            <form className="settings-card" onSubmit={savePreferences}>
                <div className="settings-card-heading">
                    <div className="settings-card-icon"><Mail size={19} /></div>
                    <div>
                        <h2>Email preferences</h2>
                        <p>These choices are applied to new AI generated emails.</p>
                    </div>
                </div>

                <label className="settings-field">
                    <span><Languages size={17} /> Writing language</span>
                    <select value={preferences.preferred_language} onChange={event => setPreferences({ ...preferences, preferred_language: event.target.value })}>
                        <option>English</option>
                        <option>Arabic</option>
                    </select>
                </label>

                <label className="settings-field">
                    <span><MessageSquareText size={17} /> Writing tone</span>
                    <select value={preferences.preferred_tone} onChange={event => setPreferences({ ...preferences, preferred_tone: event.target.value })}>
                        <option>Professional</option>
                        <option>Friendly</option>
                        <option>Casual</option>
                    </select>
                </label>

                <label className="settings-field">
                    <span><Mail size={17} /> Email length</span>
                    <select value={preferences.preferred_length} onChange={event => setPreferences({ ...preferences, preferred_length: event.target.value })}>
                        <option>Short</option>
                        <option>Medium</option>
                        <option>Long</option>
                    </select>
                </label>

                <footer className="settings-actions">
                    <p className={message.includes("saved") ? "settings-message success" : "settings-message"} aria-live="polite">{message}</p>
                    <button type="submit" disabled={saving}>
                        <Check size={17} /> {saving ? "Saving…" : "Save preferences"}
                    </button>
                </footer>
            </form>
        </section>
    );
}
