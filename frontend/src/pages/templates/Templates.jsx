import { useEffect,useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";


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


<button
className="add-contact-btn"
onClick={()=>navigate("/templates/create")}
>
+ Create Template
</button>


</div>



<div className="contact-cards">


{
templates.map(t=>(

<div className="contact-card" key={t.id}>


<div className="contact-avatar">
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



<div className="contact-actions">


<button
onClick={()=>navigate(`/templates/${t.id}/edit`)}
>
✎ Edit
</button>


<button
onClick={()=>remove(t.id)}
>
🗑 Delete
</button>


</div>


</div>

))
}


</div>


</div>

)

}
