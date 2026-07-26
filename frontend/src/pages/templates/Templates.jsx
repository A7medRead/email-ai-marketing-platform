import "./Templates.css";
import { useEffect,useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Loading from "../../components/Loading";
import EmptyState from "../../components/EmptyState";


export default function Templates(){

const [templates,setTemplates]=useState([]);
const [pageLoading,setPageLoading]=useState(true);
const navigate=useNavigate();


async function load(){

const res = await api.get("/templates/");
setTemplates(res.data);
setPageLoading(false);

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



if(pageLoading)
return <Loading />;


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
onClick={()=>{console.log("CREATE TEMPLATE CLICKED"); navigate("/templates/create")}}
>
+ Create Template
</Button>


</div>



<div className="templates-cards">


{
templates.length === 0
?
<EmptyState
title="No templates found"
message="Create your first email template"
/>
:
templates.map(t=>(

<Card className="templates-card" key={t.id}>


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


</Card>

))
}


</div>


</div>

)

}
