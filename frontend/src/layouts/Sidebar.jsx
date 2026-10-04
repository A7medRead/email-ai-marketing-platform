import "./Sidebar.css";
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
    Tag
} from "lucide-react";

import { Link, useLocation } from "react-router-dom";

export default function Sidebar(){
    const location=useLocation();

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
            name:"Offers",
            path:"/offers",
            icon:Tag
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
                                    (location.pathname===link.path || location.pathname.startsWith(`${link.path}/`))
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

                <Link
                    to="/settings"
                    className={location.pathname === "/settings" ? "sidebar-link active" : "sidebar-link"}
                >

                    <Settings size={20}/>

                    <span>

                        Settings

                    </span>

                </Link>

                <div className="sidebar-link sidebar-link-muted" aria-disabled="true">

                    <CircleHelp size={20}/>

                    <span>

                        Help & Support

                    </span>

                </div>

            </div>

        </aside>

    )

}
