import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";

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


<div className="contact-cards">

{
lists.map(list=>(

<div className="contact-card" key={list.id}>

<div className="contact-avatar">
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


<div className="contact-actions">

<button
onClick={()=>navigate(`/contact-lists/${list.id}/manage`)}
>
👁 View
</button>


<button
onClick={()=>navigate(`/contact-lists/${list.id}/manage`)}
>
⚙ Manage
</button>


</div>


</div>

))
}


</div>

</div>

)

}
