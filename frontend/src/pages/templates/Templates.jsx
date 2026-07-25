import "./Templates.css";
import { useEffect,useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";


export default function Templates(){

const [templates,setTemplates]=useState([]);
const navigate=useNavigate();


async function load(){

const res = await api.get("/templates/");
setTemplates(res.data);

}



useEffect(()=>{

load();

},[]);



async function remove(id){

const confirmDelete = window.confirm(
"Are you sure you want to delete this template?"
);

if(!confirmDelete){
return;
}

await api.delete(`/templates/${id}`);

load();

}



return (

<div className="page">


<div className="contacts-header">


<div>
<h1>
Templates
</h1>

<p className="subtitle">
Manage your email templates
</p>
</div>


<Button
onClick={()=>navigate("/templates/create")}
>
+ Create Template
</Button>


</div>



<div className="templates-cards">


{
templates.map(t=>(

<div className="templates-card" key={t.id}>


<div className="templates-avatar">
{t.name?.[0]}
</div>


<h2>
{t.name}
</h2>


<p>
Purpose: {t.purpose}
</p>


<p>
Tone: {t.tone} | Language: {t.language}
</p>


<p>
Subject: {t.subject}
</p>


<p>
{t.body?.slice(0,120)}
{t.body?.length > 120 ? "..." : ""}
</p>



<div className="templates-actions">


<Button
variant="secondary"
onClick={()=>navigate(`/templates/${t.id}/edit`)}
>
✎ Edit
</Button>


<Button
variant="danger"
onClick={()=>remove(t.id)}
>
🗑 Delete
</Button>


</div>


</div>

))
}


</div>


</div>

)

}
