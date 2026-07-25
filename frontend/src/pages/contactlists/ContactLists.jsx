import "./ContactLists.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";

export default function ContactLists(){

const [lists,setLists]=useState([]);
const navigate=useNavigate();

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
lists.map(list=>(

<div className="contactlists-card" key={list.id}>

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


</div>


</div>

))
}


</div>

</div>

)

}
