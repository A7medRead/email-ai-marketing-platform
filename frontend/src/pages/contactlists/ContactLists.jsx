import "./ContactLists.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";
import Card from "../../components/Card";

export default function ContactLists(){

const [lists,setLists]=useState([]);
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

}

}

useEffect(()=>{

api.get("/contact-lists/")
.then(res=>{
setLists(res.data);
})
.catch(err=>{
console.log(err);
});

},[]);


return (

<div className="page">

<h1>Contact Lists</h1>

<p className="subtitle">
Manage your customer groups
</p>

<Button
onClick={()=>navigate("/contact-lists/create")}
>
+ Create Contact List
</Button>


<div className="contactlists-cards">

{
lists.length === 0
?
<Card className="contactlists-card">

<h2>
No Contact Lists Found
</h2>

<p>
Create a contact list to organize your customers.
</p>

</Card>
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
