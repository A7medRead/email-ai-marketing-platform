import "./Contacts.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";

export default function Contacts(){

const [contacts,setContacts]=useState([]);
const [search,setSearch]=useState("");

function loadContacts(){

api.get("/contacts/")
.then(res=>{
setContacts(res.data);
})
.catch(err=>{
console.log(err);
});

}

useEffect(()=>{
loadContacts();
},[]);


const filtered = contacts.filter(c => {

const fields=[
c.first_name,
c.last_name,
c.email,
c.company
]
.filter(Boolean)
.map(x=>x.toLowerCase());

const value=search.trim().toLowerCase();

return fields.some(
field=>field.startsWith(value)
);

});


return (

<div className="page">


<div className="contacts-header">

<div>
<h1>Contacts</h1>
<p className="subtitle">
Manage your customer contacts
</p>
</div>


<Link to="/contacts/create">
<Button>
+ Add Contact
</Button>
</Link>

</div>


<input
placeholder="Search contacts..."
value={search}
onChange={(e)=>setSearch(e.target.value)}
className="contact-search"
/>


<div className="contact-cards">


{
filtered.map(contact=>(

<div className="contact-card" key={contact.id}>


<div className="contact-avatar">
{contact.first_name?.[0]}{contact.last_name?.[0]}
</div>


<h2 className="contact-name">
{contact.first_name} {contact.last_name}
</h2>


<p>
📧 {contact.email}
</p>


<p>
🏢 {contact.company || "No Company"}
</p>


<span className="status-active">
{contact.status}
</span>


<div className="contact-actions">


<Link to={`/contacts/${contact.id}`}>
<Button variant="secondary">
👁 View
</Button>
</Link>


<Link to={`/contacts/${contact.id}/edit`}>
<Button variant="secondary">
✎ Edit
</Button>
</Link>


</div>


</div>

))
}


</div>


</div>

)

}
