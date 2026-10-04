import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus } from "lucide-react";
import { motion } from "framer-motion";
import Button from "../../../shared/ui/Button";
import api from "../../../shared/api/client";

export default function DashboardHeader() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    api.get("/users/me").then(({ data }) => setUser(data)).catch(() => {});
  }, []);

  return (
    <motion.div
      className="dashboard-header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: .45 }}
    >
      <div className="dashboard-header-left">
        <h1>Good evening, {user?.name || "User"} 👋</h1>
        <p>Here's what's happening with your email marketing today.</p>
      </div>
      <div className="dashboard-header-actions">
        <Button onClick={() => navigate("/campaigns/create")}>
          <Plus size={18}/>
          Create Campaign
        </Button>
      </div>
    </motion.div>
  );
}
