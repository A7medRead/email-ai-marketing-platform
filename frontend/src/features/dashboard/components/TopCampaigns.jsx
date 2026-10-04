import { useNavigate } from "react-router-dom";

export default function TopCampaigns({campaigns, search=""}){
    const navigate = useNavigate();
    const filtered = campaigns.filter(c => (c.name || "").toLowerCase().includes(search.toLowerCase())).slice(0,5);
    return (
        <section className="dashboard-panel top-campaigns-panel">
            <div className="panel-header"><h3>Recent Campaigns</h3><button className="view-all-btn" onClick={() => navigate("/campaigns")}>View all</button></div>
            <table className="dashboard-table">
                <thead><tr><th>Campaign</th><th>Status</th><th>Sent</th><th>Failed</th></tr></thead>
                <tbody>
                    {filtered.map(c => <tr key={c.id}>
                        <td><div className="campaign-cell"><span className="campaign-image" aria-hidden="true">📧</span><div><strong>{c.name}</strong></div></div></td>
                        <td>{c.status || "Unknown"}</td><td>{c.sent ?? 0}</td><td>{c.failed ?? 0}</td>
                    </tr>)}
                    {filtered.length === 0 && <tr><td colSpan="4" className="dashboard-empty">No campaigns found.</td></tr>}
                </tbody>
            </table>
        </section>
    );
}
