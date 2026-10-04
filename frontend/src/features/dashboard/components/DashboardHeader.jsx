import {
    Search,
    Bell,
    ChevronDown,
    Plus
} from "lucide-react";

import { motion } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../../shared/ui/Button";
import api, { assetUrl } from "../../../shared/api/client";

export default function DashboardHeader({
    search,
    setSearch
}){

    const navigate = useNavigate();

    function logout(){
        localStorage.removeItem("token");
        navigate("/");
    }
    const [showNotifications,setShowNotifications] = useState(false);
    const [showProfile,setShowProfile] = useState(false);
    const [user,setUser] = useState(null);


    useEffect(()=>{

        api.get("/users/me")
        .then(res=>{

            setUser(res.data);

        })
        .catch(()=>{});


    },[]);

    const profileRef = useRef();
    const dropdownRef = useRef();

    useEffect(()=>{

        function handleClick(){
            setShowProfile(false);
        }

        if(showProfile){
            document.addEventListener("click",handleClick);
        }

        return ()=>{
            document.removeEventListener("click",handleClick);
        };

    },[showProfile]);

    useEffect(()=>{
        function handleClick(e){
            if(profileRef.current && !profileRef.current.contains(e.target)){
                setShowProfile(false);
            }
        }

        document.addEventListener("mousedown",handleClick);

        return ()=>{
            document.removeEventListener("mousedown",handleClick);
        };
    },[]);

    return(

        <motion.div
            className="dashboard-header"
            initial={{opacity:0,y:-20}}
            animate={{opacity:1,y:0}}
            transition={{duration:.45}}
        >

            <div className="dashboard-header-left">

                <h1>Good evening, {user?.name || 'User'} 👋</h1>

                <p>
                    Here's what's happening with your email marketing today.
                </p>

            </div>

            <div className="dashboard-header-right">

                <div className="dashboard-header-top">

                    <div className="dashboard-search">

                        <Search size={16}/>

                        <input
                            type="text"
                            placeholder="Search..."
                            value={search}
                            onChange={(e)=>setSearch(e.target.value)}
                        />

                    </div>

                    <button onClick={() => setShowNotifications(!showNotifications)} className="header-icon notification-btn">
                        <Bell size={18}/>
                        <span className="notification-badge">
                            3
                        </span>
                    </button>

                    {showNotifications && (
                        <div className="notification-dropdown">
                            <strong>Notifications</strong>
                            <p>📨 Campaign "Summer Sale" sent</p>
                            <p>👤 New contact subscribed</p>
                            <p>📄 Template updated</p>
                        </div>
                    )}

                    <div onClick={(e)=>{e.stopPropagation();setShowProfile(!showProfile)}} className="header-user">

                        <img
                            src={
    user?.avatar
    ? assetUrl(user.avatar)
    : "https://via.placeholder.com/80"
}
                            alt=""
                        />

                        <span>{user?.name || 'User'}</span>

                        <ChevronDown size={15}/>

                    </div>

                    {showProfile && (
                        <div onClick={(e)=>e.stopPropagation()} ref={dropdownRef} className="profile-dropdown">
                            <strong>{user?.name || 'User'}</strong>
                            <button onClick={() => navigate("/profile")}>Profile</button>
                            <button onClick={() => navigate("/settings")}>Settings</button>
                            <button onClick={logout} className="logout-item">Logout</button>
                        </div>
                    )}

                </div>

                <div className="dashboard-header-actions">

                    <Button onClick={() => navigate("/campaigns/create")}>

                        <Plus size={18}/>

                        Create Campaign

                    </Button>

                </div>

            </div>

        </motion.div>

    );

}
