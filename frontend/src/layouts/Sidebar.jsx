import "./Sidebar.css";
import { useEffect, useState } from "react";
import api, { assetUrl } from "../shared/api/client";
import {
    LayoutDashboard,
    Megaphone,
    Users,
    List,
    FileText,
    Mail,
    Send,
    Settings,
    CircleHelp,
    LogOut
} from "lucide-react";

import { Link, useNavigate, useLocation } from "react-router-dom";

export default function Sidebar(){

    const [user,setUser]=useState(null);

    useEffect(()=>{
        api.get("/users/me")
        .then(res=>{
            console.log("USER DATA:", res.data); setUser(res.data);
        })
        .catch(err=>{
            console.log(err);
        });
    },[]);

    const navigate=useNavigate();
    const location=useLocation();

    function logout(){

        localStorage.removeItem("token");
        navigate("/");

    }

    const links=[

        {
            name:"Dashboard",
            path:"/dashboard",
            icon:LayoutDashboard
        },

        {
            name:"Campaigns",
            path:"/campaigns",
            icon:Megaphone
        },

        {
            name:"Contacts",
            path:"/contacts",
            icon:Users
        },

        {
            name:"Contact Lists",
            path:"/contact-lists",
            icon:List
        },

        {
            name:"Templates",
            path:"/templates",
            icon:FileText
        },

        {
            name:"Emails",
            path:"/emails",
            icon:Mail
        },

        {
            name:"Sender Accounts",
            path:"/senders",
            icon:Send
        }

    ];

    return(

        <aside className="sidebar">

            <div className="sidebar-logo">

                <h2>

                    AI Mail

                </h2>

                <p>

                    Marketing Platform

                </p>

            </div>

            <nav>

                {

                    links.map(link=>{

                        const Icon=link.icon;

                        return(

                            <Link
                                key={link.path}
                                to={link.path}
                                className={
                                    location.pathname===link.path
                                    ?
                                    "sidebar-link active"
                                    :
                                    "sidebar-link"
                                }
                            >

                                <Icon size={20}/>

                                <span>

                                    {link.name}

                                </span>

                            </Link>

                        )

                    })

                }

            </nav>

            <div className="sidebar-extra">

                <a className="sidebar-link">

                    <Settings size={20}/>

                    <span>

                        Settings

                    </span>

                </a>

                <a className="sidebar-link">

                    <CircleHelp size={20}/>

                    <span>

                        Help & Support

                    </span>

                </a>

            </div>

            <div className="sidebar-bottom">

                <div className="user-card">

                    <div className="user-avatar">
    <img
        src={
            user?.avatar
            ? assetUrl(user.avatar)
            : "https://via.placeholder.com/80"
        }
        alt="avatar"
    />
</div>

                    <div>

                        <strong>

                            {user?.name || "User"}

                        </strong>

                        <p>

                            {user?.email || "user@example.com"}

                        </p>

                    </div>

                </div>

                <button
                    onClick={logout}
                    className="logout-btn"
                >

                    <LogOut size={18}/>

                    Logout

                </button>

            </div>

        </aside>

    )

}
