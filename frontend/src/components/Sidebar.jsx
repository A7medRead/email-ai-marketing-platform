import "./Sidebar.css";
import { Link, useNavigate, useLocation } from "react-router-dom";

export default function Sidebar(){

const navigate = useNavigate();
const location = useLocation();


function logout(){

localStorage.removeItem("token");

navigate("/");

}


const links = [

{
name:"Dashboard",
path:"/dashboard",
icon:"📊"
},

{
name:"Campaigns",
path:"/campaigns",
icon:"📣"
},

{
name:"Sender Accounts",
path:"/senders",
icon:"📤"
},

{
name:"Contacts",
path:"/contacts",
icon:"👥"
},

{
name:"Contact Lists",
path:"/contact-lists",
icon:"📋"
},

{
name:"Templates",
path:"/templates",
icon:"🎨"
},

{
name:"Emails",
path:"/emails",
icon:"✉️"
},

];


return (

<div className="sidebar">


<div className="sidebar-logo">

<h2>
✉ AI Mail
</h2>

<p>
Marketing Platform
</p>

</div>



<nav>

{links.map(link=>(

<Link
key={link.path}
to={link.path}
className={
location.pathname === link.path
?
"sidebar-link active"
:
"sidebar-link"
}
>

<span>
{link.icon}
</span>

{link.name}

</Link>

))}


</nav>



<div className="sidebar-bottom">

<button
onClick={logout}
className="logout-btn"
>

🚪 Logout

</button>

</div>


</div>

)

}
