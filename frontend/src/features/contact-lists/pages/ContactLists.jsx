import "./ContactLists.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../shared/api/client";
import Button from "../../../shared/ui/Button";
import Card from "../../../shared/ui/Card";

export default function ContactLists(){

const [lists,setLists]=useState([]);
const [error,setError]=useState("");
const [loading,setLoading]=useState(true);
const navigate=useNavigate();

async function deleteList(id){

const ok = window.confirm(
"Are you sure you want to delete this contact list?"
);

if(!ok)
return;

try{

await api.delete(`/contact-lists/${id}`);

setLists(prev =>
prev.filter(
x=>x.id!==id
)
);

}
catch(err){

console.log(err);
setError("Could not delete this contact list. Please try again.");

}

}

useEffect(()=>{

api.get("/contact-lists/")
.then(res=>{
setLists(res.data);
})
.catch(err=>{
console.log(err);
setError("Could not load contact lists. Please refresh the page and try again.");
}).finally(()=>setLoading(false));

},[]);


return (

<div className="page">

<div className="page-header">
<div>
<h1>Contact Lists</h1>

<p className="subtitle">
Manage your customer groups
</p>
 </div>
<div className="page-header-actions">
<Button
className="page-primary-action"
onClick={()=>navigate("/contact-lists/create")}
>
+ Create Contact List
</Button>
</div>
</div>

{error && <p role="alert" className="form-error">{error}</p>}


<div className="contactlists-cards">

{
loading ? <p role="status">Loading contact lists…</p> : error ? null : lists.length === 0
?
<div className="contactlists-empty">

<h2>
No Contact Lists Found
</h2>

<p>
Create a contact list to organize your customers.
</p>

</div>
:
lists.map(list=>(

<Card className="contactlists-card" key={list.id}>

<div className="contactlists-avatar">
{list.name?.[0]}
</div>


<h2>
{list.name}
</h2>


<p>
📝 {list.description}
</p>


<span>
👥 Contacts: {list.contacts_count ?? 0}
</span>


<div className="contactlists-actions">

<Button
variant="secondary"
onClick={()=>navigate(`/contact-lists/${list.id}/manage`)}
>
👁 View
</Button>


<Button
variant="secondary"
onClick={()=>navigate(`/contact-lists/${list.id}/manage`)}
>
⚙ Manage
</Button>


<Button
variant="danger"
onClick={()=>deleteList(list.id)}
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
